from django.test import TestCase
from faker import Faker

from edutailors.apps.group_courses.models import (
    Course, Lecture, Enrollment,
    Material, Assessment, Rating, AssessmentQuestion,
    AssessmentChoice, AssessmentAnswer,
)
from edutailors.apps.accounts.services import create_user
from edutailors.apps.education_lists.models import Subject
from edutailors.apps.group_courses.tests.group_courses_factory import (
    CourseFactory, SubjectFactory, LectureFactory, MaterialFactory,
    AssessmentFactory, RatingFactody, AssessmentQuestionFactory,
    AssessmentChoiceFactory, SessionFactory,
)

fake = Faker()


class CourseTestCase(TestCase):

    def setUp(self):
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)

    def test_string_representation_returns_title(self):
        self.assertEqual(
            str(self.course),
            self.course.title,
        )

    def test_creation_course_instance(self):
        self.assertTrue(self.course)
        self.assertEqual(self.course.__class__, Course)


class SubjectTestCase(TestCase):
    def setUp(self):
        self.subject = SubjectFactory()

    def test_string_representation_returns_title(self):
        self.assertEqual(
            str(self.subject),
            self.subject.title,
        )

    def test_creation_subject_instance(self):
        self.assertTrue(self.subject)
        self.assertEqual(self.subject.__class__, Subject)


class LectureTestCase(TestCase):
    def setUp(self):
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.lecture = LectureFactory(course=self.course)

    def test_string_representation_returns_title(self):
        self.assertEqual(
            str(self.lecture),
            self.lecture.title,
        )

    def test_creation_lecture_instance(self):
        self.assertTrue(self.lecture)
        self.assertEqual(self.lecture.__class__, Lecture)


class EnrollmentTestCase(TestCase):
    def setUp(self):
        self.user = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            registered_as='student',
            raw_password='top secret',
        )
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.lecture = LectureFactory(course=self.course)
        self.session = SessionFactory(lecture=self.lecture)
        self.enrollment = Enrollment.objects.create(
            student=self.user.student_profile, course=self.course,
        )

    def test_string_representation_returns_name(self):
        self.assertEqual(
            str(self.enrollment),
            f'{self.course} - {self.user}',
        )

    def test_creation_enrollment_instance(self):
        self.assertTrue(self.enrollment)
        self.assertEqual(self.enrollment.__class__, Enrollment)


class MaterialTestCase(TestCase):
    def setUp(self):
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.material = MaterialFactory(course=self.course)

    def test_string_representation_returns_name(self):
        self.assertEqual(
            str(self.material),
            f'Material ({self.material.id}) course({self.course.id})',
        )

    def test_creation_material_instance(self):
        self.assertTrue(self.material)
        self.assertEqual(self.material.__class__, Material)


class AssessmentTestCase(TestCase):
    def setUp(self):
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.assessment = AssessmentFactory(course=self.course)

    def test_string_representation_returns_title(self):
        self.assertEqual(
            str(self.assessment),
            f'{self.assessment.title}',
        )

    def test_creation_assessment_instance(self):
        self.assertTrue(self.assessment)
        self.assertEqual(self.assessment.__class__, Assessment)


class RatingTestCase(TestCase):
    def setUp(self):
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.user = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            registered_as='student',
            raw_password='top secret',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.rating = RatingFactody(
            student=self.user.student_profile, course=self.course)

    def test_string_representation_returns_name(self):
        self.assertEqual(
            str(self.rating),
            f'{self.rating.course} - Rating: {self.rating.rating_weight}',
        )

    def test_creation_rating_instance(self):
        self.assertTrue(self.rating)
        self.assertEqual(self.rating.__class__, Rating)

    def test_right_rating_weight(self):
        FIELDS_LIST = (
            'ease_of_use', 'customer_service',
            'met_learning_objectives', 'supporting_materials',
            'teacher', 'value_for_money', 'likehihood_to_recommend',
        )
        sum_weight = 0
        for field in FIELDS_LIST:
            sum_weight += getattr(self.rating, field)
        rating_weight = round(sum_weight / len(FIELDS_LIST), 2)

        self.assertEqual(rating_weight, self.rating.rating_weight)


class AssessmentQuestionTestCase(TestCase):
    def setUp(self):
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.user = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            registered_as='student',
            raw_password='top secret',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.assessment = AssessmentFactory(course=self.course)

        self.question = AssessmentQuestionFactory(assessment=self.assessment)
        self.choice1_1 = AssessmentChoiceFactory(question=self.question)
        self.choice1_1.is_valid = True
        self.choice1_1.save()

        self.choice1_2 = AssessmentChoiceFactory(question=self.question)
        self.choice1_2.is_valid = False
        self.choice1_2.save()

        self.question2 = AssessmentQuestionFactory(assessment=self.assessment)
        self.choice2_1 = AssessmentChoiceFactory(question=self.question)
        self.choice2_1.is_valid = True
        self.choice2_1.save()

        self.choice2_2 = AssessmentChoiceFactory(question=self.question)
        self.choice2_2.is_valid = False
        self.choice2_2.save()

        self.answer1 = AssessmentAnswer.objects.create(
            student=self.user.student_profile, choice=self.choice1_1)
        self.answer2 = AssessmentAnswer.objects.create(
            student=self.user.student_profile, choice=self.choice2_2)

    def test_string_representation_returns_title(self):
        self.assertEqual(
            str(self.question),
            f'{self.question.title}',
        )

    def test_creation_question_instance(self):
        self.assertTrue(self.question)
        self.assertEqual(self.question.__class__, AssessmentQuestion)

    def test_check_right_order(self):
        self.assertEqual(self.question.order, 1)
        self.assertEqual(self.question2.order, 2)

    def test_get_student_result(self):
        result = self.assessment.get_student_result(
            self.user.student_profile.id)
        result = result['right_answers']
        self.assertEqual(result, 1)


class AssessmentChoiceTestCase(TestCase):
    def setUp(self):
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.assessment = AssessmentFactory(course=self.course)
        self.question = AssessmentQuestionFactory(assessment=self.assessment)
        self.choice = AssessmentChoiceFactory(question=self.question)

    def test_string_representation_returns_title(self):
        self.assertEqual(
            str(self.question),
            f'{self.question.title}',
        )

    def test_creation_choice_instance(self):
        self.assertTrue(self.choice)
        self.assertEqual(self.choice.__class__, AssessmentChoice)


class AssessmentAnswerTestCase(TestCase):
    def setUp(self):
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.user = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            registered_as='student',
            raw_password='top secret',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.assessment = AssessmentFactory(course=self.course)
        self.question = AssessmentQuestionFactory(assessment=self.assessment)
        self.choice = AssessmentChoiceFactory(question=self.question)
        self.answer = AssessmentAnswer.objects.create(
            student=self.user.student_profile, choice=self.choice)

    def test_string_representation_returns_name(self):
        self.assertEqual(
            str(self.answer),
            f'student: {self.answer.student} choice: {self.answer.choice}',
        )

    def test_creation_answer_instance(self):
        self.assertTrue(self.answer)
        self.assertEqual(self.answer.__class__, AssessmentAnswer)
