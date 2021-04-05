from django.contrib.auth import get_user_model
from faker import Faker
from rest_framework import status
from rest_framework.test import (
    APIRequestFactory, APITestCase, force_authenticate,
)

from edutailors.apps.accounts.services import create_user
from edutailors.apps.group_courses.models import (
    Course, GroupCategory, Lecture, Enrollment, Assessment,
    Rating, GroupQuiz, Material, GroupQuizQuestion, GroupChoice,
    GroupAnswer,
)
from edutailors.apps.group_courses.tests.group_courses_factory import (
    CourseFactory, GroupCategoryFactory, LectureFactory, MaterialFactory,
    AssessmentFactory, RatingFactody, GroupQuizFactory,
    GroupQuizQuestionFactory, GroupChoiceFactory,
)
from edutailors.apps.group_courses.api.views import (
    CourseListCreateViewSet, GetUpdateRemoveCourseViewSet,
    GroupCategoryListCreateViewSet, GroupCategoryGetUpdateRemoveViewSet,
    LectureListCreateViewSet, LectureGetUpdateRemoveViewSet,
    EnrollmentListCreateViewSet, EnrollmentGetUpdateRemoveViewSet,
    MaterialGetUpdateRemoveViewSet,
    AssessmentGetUpdateRemoveViewSet, RatingGetUpdateRemoveViewSet,
    RatingCreateAPIView, GroupQuizGetUpdateRemoveViewSet,
    GroupQuizListCreateViewSet, GroupQuizQuestionListCreateViewSet,
    GroupQuizQuestionGetUpdateRemoveViewSet, GroupChoiceCreateAPIView,
    GroupChoiceGetUpdateRemoveViewSet, GroupAnswerCreateAPIView,
    GroupAnswerGetUpdateRemoveViewSet,
)

User = get_user_model()
fake = Faker()


class CourseViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course1 = CourseFactory(teacher=self.teacher.teacher_profile)
        self.course2 = CourseFactory(teacher=self.teacher.teacher_profile)

    def test_get_courses_list(self):
        view = CourseListCreateViewSet.as_view()
        request = self.factory.get('api/courses')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_course(self):
        date = fake.date_this_year()
        data = {
            'title': fake.sentence(),
            'teacher': self.teacher.teacher_profile.id,
            'description': fake.paragraph(),
            'start_date': date,
            'end_date': date + timedelta(days=30),
            'cost': float(fake.bothify(text='###.##')),
            'capacity': fake.random_digit_not_null(),
            'status': fake.random_element(elements=(Course.STATUS_TYPE))[0],
            'enabled': fake.boolean(),
            'category_id': self.course1.category.id,
        }
        view = CourseListCreateViewSet.as_view()
        request = self.factory.post('api/courses', data, format='json')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category_id = data.pop('category_id')
        self.assertEqual(category_id, response.data['category']['id'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_get_one_course(self):
        instance = self.course1
        field_set = {
            'title', 'description',
            'start_date', 'end_date', 'cost',
            'status', 'enabled', 'capacity',
        }
        view = GetUpdateRemoveCourseViewSet.as_view()
        request = self.factory.get('api/courses/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['teacher'], instance.teacher.id)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )

    def test_update_course(self):
        instance = self.course1
        date = fake.date_this_year()
        data = {
            'title': fake.sentence(),
            'teacher': self.teacher.teacher_profile.id,
            'description': fake.paragraph(),
            'start_date': date,
            'end_date': date + timedelta(days=30),
            'cost': float(fake.bothify(text='###.##')),
            'capacity': fake.random_digit_not_null(),
            'status': fake.random_element(elements=(Course.STATUS_TYPE))[0],
            'enabled': fake.boolean(),
            'category_id': self.course1.category.id,
        }
        view = GetUpdateRemoveCourseViewSet.as_view()
        request = self.factory.put(
            'api/courses/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category_id = data.pop('category_id')
        self.assertEqual(category_id, response.data['category']['id'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_delete_course(self):
        instance = self.course1
        view = GetUpdateRemoveCourseViewSet.as_view()
        request = self.factory.delete('api/courses/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=instance.id).exists())


class GroupCategoryViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.category1 = GroupCategoryFactory()
        self.category2 = GroupCategoryFactory()

    def test_get_categories_list(self):
        view = GroupCategoryListCreateViewSet.as_view()
        request = self.factory.get('api/categories')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_category(self):
        data = {
            'title': fake.sentence(),
            'description': fake.paragraph(),
            'enabled': fake.boolean(),
        }
        view = GroupCategoryListCreateViewSet.as_view()
        request = self.factory.post('api/categories', data, format='json')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_get_one_category(self):
        instance = self.category1
        field_set = {'title', 'description', 'enabled'}
        view = GroupCategoryGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/categories/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )

    def test_update_category(self):
        instance = self.category1
        data = {
            'title': fake.sentence(),
            'description': fake.paragraph(),
            'enabled': fake.boolean(),
        }
        view = GroupCategoryGetUpdateRemoveViewSet.as_view()
        request = self.factory.put(
            'api/categories/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_delete_category(self):
        instance = self.category1
        view = GroupCategoryGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/categories/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            GroupCategory.objects.filter(id=instance.id).exists(),
        )


class LectureViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.lecture1 = LectureFactory(course=self.course)
        self.lecture2 = LectureFactory(course=self.course)

    def test_get_lecture_list(self):
        view = LectureListCreateViewSet.as_view()
        request = self.factory.get('api/lectures')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


    def test_get_one_lecture(self):
        instance = self.lecture1
        field_set = {
            'title', 'description', 'enabled',
            'start_date', 'end_date', 'duration',
        }
        view = LectureGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/lectures/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course'], instance.course.id)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )


    def test_delete_lecture(self):
        instance = self.lecture1
        view = LectureGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/lectures/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Lecture.objects.filter(id=instance.id).exists(),
        )


class EnrollmentViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user1 = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            registered_as='student',
            raw_password='top secret',
        )
        self.user2 = create_user(
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
        self.enrollment1 = Enrollment.objects.create(
            student=self.user1.student_profile, course=self.course,
        )
        self.enrollment2 = Enrollment.objects.create(
            student=self.user2.student_profile, course=self.course,
        )

    def test_get_enrollment_list(self):
        view = EnrollmentListCreateViewSet.as_view()
        request = self.factory.get('api/enrollments')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_enrollment(self):
        data = {
            'enabled': fake.boolean(),
            'course': self.course.id,
            'student': self.user1.student_profile.id,
        }
        view = EnrollmentListCreateViewSet.as_view()
        request = self.factory.post('api/enrollments', data, format='json')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = data.pop('course')
        self.assertEqual(course_id, response.data['course'])
        student_id = data.pop('student')
        self.assertEqual(student_id, response.data['student'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_get_one_enrollment(self):
        instance = self.enrollment1
        field_set = {'enabled'}
        view = EnrollmentGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/enrollments/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course'], instance.course.id)
        self.assertEqual(response.data['student'], instance.student.id)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )

    def test_update_enrollment(self):
        instance = self.enrollment1
        data = {
            'enabled': fake.boolean(),
            'course': self.course.id,
            'student': self.user2.student_profile.id,
        }
        view = EnrollmentGetUpdateRemoveViewSet.as_view()
        request = self.factory.put(
            'api/enrollment/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course_id = data.pop('course')
        self.assertEqual(course_id, response.data['course'])
        course_id = data.pop('student')
        self.assertEqual(course_id, response.data['student'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_delete_enrollment(self):
        instance = self.enrollment1
        view = EnrollmentGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/enrollments/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Lecture.objects.filter(id=instance.id).exists(),
        )


class MaterialViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.material = MaterialFactory(course=self.course)

    def test_get_one_material(self):
        instance = self.material
        field_set = {
            'description', 'document', 'enabled',
        }
        view = MaterialGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/materials/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course'], instance.course.id)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )

    def test_update_material(self):
        instance = self.material
        data = {
            'enabled': fake.boolean(),
            'course': self.course.id,
            'document': fake.image_url(),
            'description': fake.paragraph(),
        }
        view = MaterialGetUpdateRemoveViewSet.as_view()
        request = self.factory.put(
            'api/materials/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course_id = data.pop('course')
        self.assertEqual(course_id, response.data['course'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_delete_material(self):
        instance = self.material
        view = MaterialGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/materials/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Material.objects.filter(id=instance.id).exists(),
        )


class AssessmentViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.assessment = AssessmentFactory(course=self.course)

    def test_create_assessment(self):
        date = fake.date_this_year()
        data = {
            'enabled': fake.boolean(),
            'course': self.course.id,
            'title': fake.sentence(),
            'duration': fake.random_digit_not_null(),
            'start_date': date,
            'end_date': date + timedelta(days=2),
            'valid_until': date + timedelta(days=1),
            'max_number_of_retries': fake.random_digit_not_null(),
            'finished': fake.boolean(),
        }
        view = AssessmentCreateAPIView.as_view()
        request = self.factory.post('api/assessments', data, format='json')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = data.pop('course')
        self.assertEqual(course_id, response.data['course'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_get_one_assessment(self):
        instance = self.assessment
        field_set = {
            'title', 'duration', 'start_date', 'end_date',
            'valid_until', 'max_number_of_retries', 'finished', 'enabled',
        }
        view = AssessmentGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/assessments/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course'], instance.course.id)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )

    def test_update_assessment(self):
        instance = self.assessment
        date = fake.date_this_year()
        data = {
            'enabled': fake.boolean(),
            'course': self.course.id,
            'title': fake.sentence(),
            'duration': fake.random_digit_not_null(),
            'start_date': date,
            'end_date': date + timedelta(days=2),
            'valid_until': date + timedelta(days=1),
            'max_number_of_retries': fake.random_digit_not_null(),
            'finished': fake.boolean(),
        }
        view = AssessmentGetUpdateRemoveViewSet.as_view()
        request = self.factory.put(
            'api/assessments/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course_id = data.pop('course')
        self.assertEqual(course_id, response.data['course'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_delete_assessment(self):
        instance = self.assessment
        view = AssessmentGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/assessments/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Assessment.objects.filter(id=instance.id).exists(),
        )


class RatingViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
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
            course=self.course, student=self.user.student_profile)

    def test_create_rating(self):
        data = {
            'course': self.course.id,
            'student': self.user.student_profile.id,
            'enabled': fake.boolean(),
            'ease_of_use': fake.random.randint(1, 5),
            'customer_service': fake.random.randint(1, 5),
            'met_learning_objectives': fake.random.randint(1, 5),
            'supporting_materials': fake.random.randint(1, 5),
            'teacher': fake.random.randint(1, 5),
            'value_for_money': fake.random.randint(1, 5),
            'likehihood_to_recommend': fake.random.randint(1, 5),
            'description': fake.paragraph(),
        }
        view = RatingCreateAPIView.as_view()
        request = self.factory.post('api/rating', data, format='json')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course_id = data.pop('course')
        self.assertEqual(course_id, response.data['course'])
        student_id = data.pop('student')
        self.assertEqual(student_id, response.data['student'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_get_one_rating(self):
        instance = self.rating
        field_set = {
            'ease_of_use', 'customer_service',
            'met_learning_objectives', 'supporting_materials',
            'teacher', 'value_for_money', 'likehihood_to_recommend',
            'description', 'enabled',
        }
        view = RatingGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/rating/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course'], instance.course.id)
        self.assertEqual(response.data['student'], instance.student.id)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )

    def test_update_rating(self):
        instance = self.rating
        data = {
            'course': self.course.id,
            'student': self.user.student_profile.id,
            'enabled': fake.boolean(),
            'ease_of_use': fake.random.randint(1, 5),
            'customer_service': fake.random.randint(1, 5),
            'met_learning_objectives': fake.random.randint(1, 5),
            'supporting_materials': fake.random.randint(1, 5),
            'teacher': fake.random.randint(1, 5),
            'value_for_money': fake.random.randint(1, 5),
            'likehihood_to_recommend': fake.random.randint(1, 5),
            'description': fake.paragraph(),
        }
        view = RatingGetUpdateRemoveViewSet.as_view()
        request = self.factory.put(
            'api/rating/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course_id = data.pop('course')
        self.assertEqual(course_id, response.data['course'])
        student_id = data.pop('student')
        self.assertEqual(student_id, response.data['student'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_delete_rating(self):
        instance = self.rating
        view = RatingGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/rating/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Rating.objects.filter(id=instance.id).exists(),
        )


class GroupQuizViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.assessment = AssessmentFactory(course=self.course)
        self.quiz = GroupQuizFactory(assessment=self.assessment)
        self.quiz2 = GroupQuizFactory(assessment=self.assessment)

    def test_get_quiz_list(self):
        view = GroupQuizListCreateViewSet.as_view()
        request = self.factory.get('api/group-quizzes')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_quiz(self):
        data = {
            'title': fake.sentence(),
            'assessment': self.assessment.id,
            'description': fake.paragraph(),
            'duration': fake.random_digit_not_null(),
            'total_score': fake.random_digit_not_null(),
            'finished': fake.boolean(),
        }
        view = GroupQuizListCreateViewSet.as_view()
        request = self.factory.post('api/group-quizzes', data, format='json')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assessment_id = data.pop('assessment')
        self.assertEqual(assessment_id, response.data['assessment'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_get_one_quiz(self):
        instance = self.quiz
        field_set = {
            'title', 'description', 'duration', 'total_score', 'finished',
        }
        view = GroupQuizGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/group-quizzes/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['assessment'], instance.assessment.id)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )

    def test_update_quiz(self):
        instance = self.quiz
        data = {
            'title': fake.sentence(),
            'assessment': self.assessment.id,
            'description': fake.paragraph(),
            'duration': fake.random_digit_not_null(),
            'total_score': fake.random_digit_not_null(),
            'finished': fake.boolean(),
        }
        view = GroupQuizGetUpdateRemoveViewSet.as_view()
        request = self.factory.put(
            'api/group-quizzes/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assessment_id = data.pop('assessment')
        self.assertEqual(assessment_id, response.data['assessment'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_delete_quiz(self):
        instance = self.quiz
        view = GroupQuizGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/group-quizzes/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            GroupQuiz.objects.filter(id=instance.id).exists(),
        )


class GroupQuizQuestionViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.assessment = AssessmentFactory(course=self.course)
        self.quiz = GroupQuizFactory(assessment=self.assessment)
        self.quiz_question = GroupQuizQuestionFactory(group_quiz=self.quiz)
        self.quiz_question2 = GroupQuizQuestionFactory(group_quiz=self.quiz)

    def test_get_quiz_question_list(self):
        view = GroupQuizQuestionListCreateViewSet.as_view()
        request = self.factory.get('api/group-quiz_questions')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_quiz_question(self):
        data = {
            'title': fake.sentence(),
            'description': fake.paragraph(),
            'type': fake.random.choice(GroupQuizQuestion.QUESTION_TYPE)[0],
            'group_quiz': self.quiz.id,
        }
        view = GroupQuizQuestionListCreateViewSet.as_view()
        request = self.factory.post(
            'api/group-quiz_questions', data, format='json')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        group_quiz_id = data.pop('group_quiz')
        self.assertEqual(group_quiz_id, response.data['group_quiz'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_get_one_quiz_question(self):
        instance = self.quiz_question
        field_set = {
            'title', 'description', 'type', 'enabled', 'order',
        }
        view = GroupQuizQuestionGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/group-quiz_questions/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['group_quiz'], instance.group_quiz.id)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )

    def test_update_quiz_question(self):
        instance = self.quiz_question
        data = {
            'title': fake.sentence(),
            'description': fake.paragraph(),
            'type': fake.random.choice(GroupQuizQuestion.QUESTION_TYPE)[0],
            'group_quiz': self.quiz.id,
        }
        view = GroupQuizQuestionGetUpdateRemoveViewSet.as_view()
        request = self.factory.put(
            'api/group-quiz_questions/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group_quiz_id = data.pop('group_quiz')
        self.assertEqual(group_quiz_id, response.data['group_quiz'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_delete_quiz_question(self):
        instance = self.quiz_question
        view = GroupQuizQuestionGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/group-quiz_questions/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            GroupQuizQuestion.objects.filter(id=instance.id).exists(),
        )


class GroupChoiceViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher = create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            raw_password='top secret',
            registered_as='teacher',
        )
        self.course = CourseFactory(teacher=self.teacher.teacher_profile)
        self.assessment = AssessmentFactory(course=self.course)
        self.quiz = GroupQuizFactory(assessment=self.assessment)
        self.quiz_question = GroupQuizQuestionFactory(group_quiz=self.quiz)
        self.quiz_question2 = GroupQuizQuestionFactory(group_quiz=self.quiz)
        self.choice = GroupChoiceFactory(quiz_question=self.quiz_question)

    def test_create_choice(self):
        data = {
            'quiz_question_id': self.quiz_question2.id,
            'title': fake.sentence(),
            'description': fake.paragraph(),
            'is_valid': fake.boolean(),
        }
        view = GroupChoiceCreateAPIView.as_view()
        request = self.factory.post('api/group-choices', data, format='json')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        quiz_question_id = data.pop('quiz_question_id')
        self.assertEqual(
            quiz_question_id, response.data['quiz_question']['id'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_get_one_choice(self):
        instance = self.choice
        field_set = {
            'title', 'description', 'is_valid', 'enabled',
        }
        view = GroupChoiceGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/group-choices/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['quiz_question']['id'], instance.quiz_question.id)
        for field in field_set:
            self.assertEqual(
                str(response.data[field]),
                str(getattr(instance, field)),
            )

    def test_update_choice(self):
        instance = self.choice
        data = {
            'quiz_question_id': self.quiz_question2.id,
            'title': fake.sentence(),
            'description': fake.paragraph(),
            'is_valid': fake.boolean(),
        }
        view = GroupChoiceGetUpdateRemoveViewSet.as_view()
        request = self.factory.put(
            'api/group-choices/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        quiz_question_id = data.pop('quiz_question_id')
        print(response.data)
        self.assertEqual(
            quiz_question_id, response.data['quiz_question']['id'])
        for key, value in data.items():
            self.assertEqual(str(response.data[key]), str(value))

    def test_delete_choice(self):
        instance = self.choice
        view = GroupChoiceGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/group-choices/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            GroupChoice.objects.filter(id=instance.id).exists(),
        )


class GroupAnswerViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
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
        self.quiz = GroupQuizFactory(assessment=self.assessment)
        self.quiz_question = GroupQuizQuestionFactory(group_quiz=self.quiz)
        self.choice = GroupChoiceFactory(quiz_question=self.quiz_question)
        self.choice2 = GroupChoiceFactory(quiz_question=self.quiz_question)
        self.answer = GroupAnswer.objects.create(
            student=self.user.student_profile, choice=self.choice)

    def test_create_answer(self):
        data = {
            'student': self.user.student_profile.id,
            'choice': [self.choice.id, self.choice2.id],
        }
        view = GroupAnswerCreateAPIView.as_view()
        request = self.factory.post('api/group-answers', data, format='json')
        force_authenticate(request, user=self.teacher)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0]['student'], data['student'])
        self.assertEqual(response.data[1]['student'], data['student'])
        self.assertEqual(response.data[0]['choice'], data['choice'][0])
        self.assertEqual(response.data[1]['choice'], data['choice'][1])

    def test_get_one_answer(self):
        instance = self.answer
        view = GroupAnswerGetUpdateRemoveViewSet.as_view()
        request = self.factory.get('api/group-answers/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['student'], instance.student.id)
        self.assertEqual(
            response.data['choice'], instance.choice.id)

    def test_update_answer(self):
        instance = self.answer
        data = {
            'student': self.user.student_profile.id,
            'choice': self.choice2.id,
        }
        view = GroupAnswerGetUpdateRemoveViewSet.as_view()
        request = self.factory.put(
            'api/group-answers/<pk:int>', data, format='json',
        )
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        student_id = data.pop('student')
        self.assertEqual(student_id, response.data['student'])
        choice_id = data.pop('choice')
        self.assertEqual(choice_id, response.data['choice'])

    def test_delete_answer(self):
        instance = self.answer
        view = GroupAnswerGetUpdateRemoveViewSet.as_view()
        request = self.factory.delete('api/group-answers/<pk:int>')
        force_authenticate(request, user=self.teacher)
        response = view(request, pk=instance.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            GroupAnswer.objects.filter(id=instance.id).exists(),
        )
