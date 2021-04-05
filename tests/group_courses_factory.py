import factory
from faker import Faker
from datetime import timedelta
import pytz

from edutailors.apps.group_courses.models import (
    Course, Lecture, Material, Assessment, Rating,
    AssessmentQuestion, AssessmentChoice, Session,
)
from edutailors.apps.education_lists.models import (
    Subject, SubjectField, Category,
)

fake = Faker()

date = fake.date_this_year()
date_time = fake.date_time_this_year(tzinfo=pytz.utc)


class CategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Category

    title = fake.sentence()


class SubjectFieldFactory(factory.DjangoModelFactory):
    class Meta:
        model = SubjectField

    title = fake.sentence()
    category = factory.SubFactory(CategoryFactory)


class SubjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = Subject

    title = fake.sentence()
    field = factory.SubFactory(SubjectFieldFactory)


class SessionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Session

    start_date = date_time
    end_date = date_time + timedelta(days=30)
    is_default = fake.boolean()


class CourseFactory(factory.DjangoModelFactory):
    class Meta:
        model = Course

    title = fake.sentence()
    description = fake.paragraph()
    status = fake.random_element(elements=(Course.STATUS_TYPE))[0]
    start_date = date_time
    end_date = date_time + timedelta(days=30)
    subject = factory.SubFactory(SubjectFactory)
    cost = float(fake.bothify(text='###.##'))
    capacity = fake.random_digit_not_null()
    enabled = fake.boolean()


class LectureFactory(factory.DjangoModelFactory):
    class Meta:
        model = Lecture

    title = fake.sentence()
    description = fake.paragraph()
    enabled = fake.boolean()


class MaterialFactory(factory.DjangoModelFactory):
    class Meta:
        model = Material
    description = fake.paragraph()
    document = fake.image_url()
    gmat = fake.random_element(elements=(Material.GMATType.choices))[0]


class AssessmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Assessment
    title = fake.sentence()
    start_date = date_time
    end_date = date_time + timedelta(days=2)
    valid_until = date + timedelta(days=1)
    max_number_of_retries = fake.random_digit_not_null()
    total_score = fake.random_digit_not_null()


class RatingFactody(factory.DjangoModelFactory):
    """
    Needed student, course
    """
    class Meta:
        model = Rating
    ease_of_use = fake.random.randint(1, 5)
    customer_service = fake.random.randint(1, 5)
    met_learning_objectives = fake.random.randint(1, 5)
    supporting_materials = fake.random.randint(1, 5)
    teacher = fake.random.randint(1, 5)
    value_for_money = fake.random.randint(1, 5)
    likehihood_to_recommend = fake.random.randint(1, 5)
    description = fake.paragraph()


class AssessmentQuestionFactory(factory.DjangoModelFactory):
    """
    Needed group_quiz
    """
    class Meta:
        model = AssessmentQuestion
    title = fake.sentence()
    description = fake.paragraph()


class AssessmentChoiceFactory(factory.DjangoModelFactory):
    """
    Needed quiz_question
    """
    class Meta:
        model = AssessmentChoice
    title = fake.sentence()
    description = fake.paragraph()
    is_valid = fake.boolean()
