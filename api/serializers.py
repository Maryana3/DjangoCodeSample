from rest_framework import serializers
from django.db.models import Avg

from edutailors.apps.education_lists.api.serializers import SubjectSerializer
from edutailors.apps.group_courses.models import (
    Course, Lecture, Enrollment,
    Material, Assessment, AssessmentQuestion, AssessmentChoice,
    AssessmentAnswer, Rating, Session,
)
from edutailors.apps.profiles.api.serializers import TutorDetailSerializer


class SessionSerializer(serializers.ModelSerializer):
    is_selected = serializers.SerializerMethodField(read_only=True)

    def get_is_selected(self, obj):
        if self.context['request'].user.is_authenticated:
            student = self.context['request'].user.student_profile
            if obj.session_student.filter(student=student).exists():
                return True
            return False
        return None

    class Meta:
        model = Session
        fields = (
            'id', 'start_date', 'end_date', 'description',
            'duration', 'is_selected', 'is_default',
        )


class LectureSerializer(serializers.ModelSerializer):
    sessions = SessionSerializer(many=True, required=False)

    class Meta:
        model = Lecture
        fields = (
            'id', 'title', 'description',
            'slug', 'enabled', 'course',
            'created', 'updated', 'sessions',
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = (
            'id', 'enabled', 'student', 'course',
            'created', 'updated', 'diagnostic_status',
        )


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = (
            'document', 'description', 'enabled',
            'course', 'created', 'updated', 'id',
            'gmat', 'sat', 'gre',
        )


class AssessmentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentAnswer
        fields = (
            'student', 'choice', 'created', 'id',
        )


class OneQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = ('id', 'title', 'description', 'order')


class AssessmentChoiceSerializer(serializers.ModelSerializer):
    answers = AssessmentAnswerSerializer(many=True, required=False)
    question = OneQuestionSerializer(read_only=True)
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AssessmentChoice
        fields = (
            'id', 'title', 'description', 'is_valid',
            'enabled', 'question', 'answers',
            'question_id',
        )


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    choices = AssessmentChoiceSerializer(many=True, required=False)

    class Meta:
        model = AssessmentQuestion
        fields = (
            'id', 'title', 'description', 'enabled',
            'order', 'choices',
        )


class AssessmentSerializer(serializers.ModelSerializer):
    questions = AssessmentQuestionSerializer(
        many=True, required=False)

    def get_questions(self, obj):
        request = self.context['request']
        user = request.user
        assessment_type = request.data.get('assessment_type')

        questions = obj.questions
        if assessment_type == Assessment.DIAGNOSTIC:
            answers_ids = AssessmentAnswer.objects.filter(
                student=user.student_profile,
            ).values_list('choice__question', flat=True).distinct()
            questions = questions.filter(
                assessment__assessment_type=assessment_type).exclude(
                    test_choices__test_question__in=answers_ids,
            )
        return AssessmentQuestionSerializer(
            questions, many=True, required=False,
        ).data

    class Meta:
        model = Assessment
        fields = (
            'title', 'duration', 'start_date', 'end_date',
            'valid_until', 'max_number_of_retries',
            'enabled', 'course', 'id', 'total_score',
            'assessment_type', 'questions',
        )


class RatingSerializer(serializers.ModelSerializer):
    student_info = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)

    def get_student_info(self, obj):
        first_name = obj.student.user.first_name
        last_name = obj.student.user.last_name
        avatar = obj.student.user.common_profile.avatar
        return {
            'avatar': avatar,
            'first_name': first_name,
            'last_name': last_name,
        }

    def get_average_rating(self, obj):
        return obj.get_average_rating

    class Meta:
        model = Rating
        fields = (
            'description', 'enabled', 'id', 'course', 'created', 'updated',
            'student_info', 'student', 'ease_of_use', 'customer_service',
            'met_learning_objectives', 'supporting_materials', 'teacher',
            'value_for_money', 'likehihood_to_recommend', 'rating_weight',
            'average_rating',
        )


class GroupCourseSerializer(serializers.ModelSerializer):
    teacher_info = TutorDetailSerializer(read_only=True, source='teacher.user')
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.IntegerField(write_only=True)
    lectures = LectureSerializer(many=True, required=False)
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    materials = MaterialSerializer(many=True, required=False)
    assessments = AssessmentSerializer(many=True, required=False)
    ratings = RatingSerializer(many=True, required=False)
    user_is_enrolled = serializers.SerializerMethodField(read_only=True)
    average_rating_weight = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    test_drive_available = serializers.SerializerMethodField(read_only=True)
    material_type = serializers.SerializerMethodField(read_only=True)
    allow_to_rate = serializers.SerializerMethodField(read_only=True)

    def get_test_drive_available(self, obj):
        if self.context['request'].user.is_authenticated:
            user = self.context['request'].user
            testcourse = obj.testcourse
            if all((not user.student_profile.enrollments.filter(
                course=obj).exists(), obj.test_drive, not testcourse.filter(
                    user=user).exists())):
                return True
            return False
        return None

    def get_user_is_enrolled(self, obj):
        if self.context['request'].user.is_authenticated:
            user = self.context['request'].user
            return obj.enrollments.filter(student__user=user).exists()
        return None

    def get_average_rating_weight(self, obj):
        rating = obj.ratings.all().aggregate(Avg('rating_weight'))
        return rating['rating_weight__avg']

    def get_average_rating(self, obj):
        return obj.get_average_rating

    def get_material_type(self, obj):
        if obj.materials.filter(gmat__isnull=False).exists():
            return 'gmat'
        elif obj.materials.filter(gre__isnull=False).exists():
            return 'gre'
        elif obj.materials.filter(sat__isnull=False).exists():
            return 'sat'

    def get_allow_to_rate(self, obj):
        user = self.context['request'].user
        if user:
            enrollment = user.student_profile.enrollments.filter(
                course=obj).first()
            return bool(
                enrollment and not enrollment.course_rated
                and obj.last_lecture_finished)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'description',
            'image', 'start_date', 'end_date', 'cost',
            'capacity', 'status', 'enabled', 'created',
            'updated', 'teacher', 'teacher_info', 'subject',
            'subject_id', 'lectures', 'enrollments', 'materials',
            'user_is_enrolled', 'assessments', 'ratings',
            'average_rating_weight', 'average_rating', 'level',
            'is_adaptive', 'test_drive', 'test_drive_available',
            'material_type', 'allow_to_rate',
        )
