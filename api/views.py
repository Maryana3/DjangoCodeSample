import os
import uuid
import django_filters

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

from edutailors.apps.group_courses.custom_storage import S3Storage
from edutailors.apps.group_courses.models import (
    Course, Lecture, Enrollment,
    Material, Assessment, Rating, AssessmentQuestion,
    AssessmentChoice, AssessmentAnswer, SessionStudent,
    Session, StudentScore,
)
from .serializers import (
    GroupCourseSerializer, LectureSerializer, EnrollmentSerializer,
    MaterialSerializer, RatingSerializer, AssessmentSerializer,
    AssessmentQuestionSerializer, AssessmentChoiceSerializer,
    AssessmentAnswerSerializer,
)
from .filters import CourseFilterSet


class CourseListCreateViewSet(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = GroupCourseSerializer
    permission_classes = [AllowAny]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
    ]
    filter_class = CourseFilterSet


class GetUpdateRemoveCourseViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = GroupCourseSerializer
    permission_classes = [AllowAny]


class LectureListCreateViewSet(generics.ListCreateAPIView):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsAuthenticated]


class LectureGetUpdateRemoveViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsAuthenticated]


class EnrollmentListCreateViewSet(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]


class EnrollmentGetUpdateRemoveViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]


class MaterialCreateAPIView(generics.CreateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.POST
        course_id = data.get('course')
        description = data.get('description')
        gmat = data.get('gmat')
        sat = data.get('sat')
        gre = data.get('gre')
        file = request.FILES.get('file', '')
        file_name = file.name.split('.')[-2]
        file_format = file.name.split('.')[-1]
        new_unique_file_name = f'{file_name}-{uuid.uuid4().hex}.{file_format}'
        file_directory_within_bucket = 'group-courses/documents'
        file_path_within_bucket = os.path.join(
            file_directory_within_bucket,
            new_unique_file_name,
        )

        s3_storage = S3Storage()
        if not s3_storage.exists(file_path_within_bucket):
            s3_storage.save(file_path_within_bucket, file)
            file_url = s3_storage.url(file_path_within_bucket)

            obj = Material.objects.create(
                course_id=course_id,
                description=description,
                document=file_url,
                file_path_within_bucket=file_path_within_bucket,
                gmat=gmat,
                sat=sat,
                gre=gre,
            )
            serializer = self.get_serializer(obj)
            return Response(serializer.data)
        else:
            return Response({
                'message': f'Error: file {file.name} already exists at \
                    {file_directory_within_bucket} in bucket \
                        {s3_storage.bucket_name}',
            }, status=status.HTTP_409_CONFLICT)


class MaterialGetUpdateRemoveViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.file_path_within_bucket:
            s3_storage = S3Storage()
            s3_storage.delete(instance.file_path_within_bucket)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RatingCreateAPIView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        course_id = data.get('course')
        student_id = data.get('student')
        course = Course.objects.filter(id=course_id).first()
        if not course.last_lecture_finished:
            raise Exception('Not all sessions are finished.')
        if self.queryset.filter(
            course_id=course_id,
            student_id=student_id,
        ).exists():
            raise Exception('Rating of current user already exists.')

        Enrollment.objects.filter(
            course_id=course_id,
            student_id=student_id,
        ).update(course_rated=True)
        return super().create(request, *args, **kwargs)


class RatingGetUpdateRemoveViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]


class AssessmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
    ]
    filter_fields = ['assessment_type', 'course']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset()).filter(is_valid=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AssessmentGetUpdateRemoveViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]


class AssessmentQuestionListCreateViewSet(generics.ListCreateAPIView):
    queryset = AssessmentQuestion.objects.all()
    serializer_class = AssessmentQuestionSerializer
    permission_classes = [IsAuthenticated]


class AssessmentQuestionGetUpdateRemoveViewSet(
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = AssessmentQuestion.objects.all()
    serializer_class = AssessmentQuestionSerializer
    permission_classes = [IsAuthenticated]


class AssessmentChoiceCreateAPIView(generics.CreateAPIView):
    queryset = AssessmentChoice.objects.all()
    serializer_class = AssessmentChoiceSerializer
    permission_classes = [IsAuthenticated]


class AssessmentChoiceGetUpdateRemoveViewSet(
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = AssessmentChoice.objects.all()
    serializer_class = AssessmentChoiceSerializer
    permission_classes = [IsAuthenticated]


class AssessmentAnswerCreateAPIView(generics.CreateAPIView):
    queryset = AssessmentAnswer.objects.all()
    serializer_class = AssessmentAnswerSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        student = request.user.student_profile.id
        choices = request.data.get('choice')
        if not student or not choices:
            return Response(
                {'message': 'student and choice field is required'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        new_data = [
            {'choice': choice, 'student': student} for choice in choices
        ]
        choice = choices[0]
        assessment = Assessment.objects.filter(
            questions__choices=choice).first()
        choices = AssessmentChoice.objects.filter(
            question__assessment=assessment).values_list('id', flat=True)
        old_answer = self.get_queryset().filter(
            choice__in=choices, student=student)
        old_answer.delete()

        serializer = self.get_serializer(data=new_data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers,
        )


class DiagnosticTestAnswerCreateAPIView(generics.CreateAPIView):
    queryset = AssessmentAnswer.objects.all()
    serializer_class = AssessmentAnswerSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        student = request.user.student_profile
        choices = data.get('choice')
        course_id = data.get('course_id')
        new_data = [
            {'choice': choice, 'student': student.id} for choice in choices
        ]
        if not course_id or not choices:
            return Response(
                {'message': 'course_id and choice field is required'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        choice = AssessmentChoice.objects.filter(id=choices[0]).first()
        enrollment = Enrollment.objects.filter(
            course_id=course_id,
            student=student,
        )

        if choice.first_question():
            enrollment.update(
                diagnostic_status=Enrollment.DiagnosticStatusType.IN_PROGRESS,
            )
        if choice.last_question():
            enrollment.update(
                diagnostic_status=Enrollment.DiagnosticStatusType.COMPLETED,
            )

        serializer = self.get_serializer(data=new_data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers,
        )


class AssessmentAnswerGetUpdateRemoveViewSet(
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = AssessmentAnswer.objects.all()
    serializer_class = AssessmentAnswerSerializer
    permission_classes = [IsAuthenticated]


class AssessmentSelectedChoicesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        student_id = request.data.get('student')
        assessment_id = request.data.get('assessment')
        if not student_id or not assessment_id:
            return Response(
                {'message': 'student and assessment field is required'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        assessment = Assessment.objects.filter(id=assessment_id).first()
        if not assessment:
            return Response(
                {'message': 'Assessment not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        choices = assessment.get_selected_choices(student_id)
        serializer = AssessmentChoiceSerializer(choices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssessmentRightChoicesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        assessment = Assessment.objects.filter(id=pk).first()
        choices = assessment.get_right_choices()
        serializer = AssessmentChoiceSerializer(choices, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_student_result_view(request):
    student_id = request.user.student_profile.id
    assessment_id = request.data.get('assessment')
    if not student_id or not assessment_id:
        return Response(
            {'message': 'student and assessment field is required'},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    assessment = Assessment.objects.filter(id=assessment_id).first()
    result = assessment.get_student_result(student_id)
    persent = result['right_answers'] / result['all_question'] * 100

    score = assessment.total_score * persent / 100
    StudentScore.objects.update_or_create(
        assessment=assessment,
        student_id=student_id,
        score=score,
    )

    if persent >= 60 or assessment.assessment_type == Assessment.DIAGNOSTIC:
        result['pass'] = True
    else:
        result['pass'] = False
    return Response(result)


class ChangeSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student_id')
        session_id = request.data.get('session_id')
        session = Session.objects.filter(id=session_id).first()
        SessionStudent.objects.filter(
            session__lecture=session.lecture,
            student_id=student_id,
        ).update(session=session)

        return Response(
            {'message': 'Session Updated'},
            status=status.HTTP_201_CREATED,
        )
