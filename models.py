import string
from random import choice

from django.db import models
from django.conf import settings
from django_extensions.db.fields import AutoSlugField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.db.models import Max
from djchoices import DjangoChoices, ChoiceItem

from s3direct.fields import S3DirectField

from edutailors.apps.utils.other import TimedModel, edutailors_slugify
from edutailors.apps.group_courses.querysets import LectureQuerySet


def get_random_id(size=32):
    return ''.join(
        [choice(string.ascii_letters + string.digits) for _ in range(size)])


def get_duration(start_date, end_date):
    return int((end_date - start_date).total_seconds() / 60)


class Course(TimedModel):
    UPCOMING = 'upcoming'
    IN_PROGRESS = 'in progress'
    FINISHED = 'finished'
    STATUS_TYPE = (
        (UPCOMING, _('Upcoming')),
        (IN_PROGRESS, _('InProgress')),
        (FINISHED, _('Finished')),
    )

    class LevelType(DjangoChoices):
        ALL_LEVELS = ChoiceItem('all_levels')
        BEGINNER = ChoiceItem('beginner')
        INTERMEDIATE = ChoiceItem('intermediate')
        ADVANCED = ChoiceItem('advanced')

    level = models.CharField(
        max_length=20,
        choices=LevelType.choices,
        default=LevelType.ALL_LEVELS,
    )
    title = models.CharField(max_length=255, blank=False)
    slug = AutoSlugField(
        blank=False,
        populate_from='title',
        overwrite=True,
        slugify_function=edutailors_slugify,
        unique=True,
    )
    subject = models.ForeignKey(
        'education_lists.Subject',
        on_delete=models.PROTECT,
        related_name='courses',
        null=True,
    )
    teacher = models.ForeignKey(
        to='profiles.TeacherProfile',
        related_name='courses',
        on_delete=models.CASCADE,
    )
    assistant = models.ForeignKey(
        to='profiles.TeacherProfile',
        related_name='assistant',
        on_delete=models.CASCADE,
        null=True,
    )
    description = models.TextField()
    image = S3DirectField(dest='course-image', blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    cost = models.FloatField(validators=[MinValueValidator(0)])
    capacity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        default=5,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_TYPE,
        default=UPCOMING,
    )
    enabled = models.BooleanField(default=True)
    is_adaptive = models.BooleanField(
        default=False, verbose_name='Adaptive Course')
    test_drive = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def clean(self):
        if not self.start_date or not self.end_date:
            raise ValidationError('Fields are required')
        if self.start_date > self.end_date:
            raise ValidationError(
                'The start date should be lower than the end date')
        if self.assistant == self.teacher:
            raise ValidationError(
                'Teacher and assistant can not be the same person')
        if self.teacher.status != 'approved':
            raise ValidationError(
                'Please select another teacher. This one is not approved')

    def save(self, *args, **kwargs):
        if self.start_date > now():
            self.status = Course.UPCOMING
        elif self.end_date < now():
            self.status = Course.FINISHED
        else:
            self.status = Course.IN_PROGRESS
        super(Course, self).save(*args, **kwargs)

    @property
    def get_average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            avarage_ratings = [rating.get_average_rating for rating in ratings]
            avarage_ratings = [rating for rating in avarage_ratings if ratings]
            return sum(avarage_ratings) / len(avarage_ratings)

    def last_lecture_finished(self):
        sessions = Session.objects.filter(
            lecture__course=self,
            end_date__gte=now(),
        )
        return not sessions.exists()


class Lecture(TimedModel):
    course = models.ForeignKey(
        'Course', related_name='lectures',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField()
    slug = AutoSlugField(
        blank=False,
        populate_from='title',
        overwrite=True,
        slugify_function=edutailors_slugify,
        unique=True,
    )
    enabled = models.BooleanField(default=True)
    objects = LectureQuerySet.as_manager()

    class Meta:
        ordering = ['created', 'updated']
        verbose_name_plural = 'Course Lectures'

    def __str__(self):
        return self.title


class SessionStudent(TimedModel):
    session = models.ForeignKey(
        to='Session',
        related_name='session_student',
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        to='profiles.StudentProfile',
        related_name='session_student',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = 'Session_student'

    def save(self, *args, **kwargs):
        session_students = SessionStudent.objects.filter(
            session__lecture=self.session.lecture,
            student=self.student,
        )
        if session_students.exists():
            raise Exception('Only one session of each lecture '
                'is available for student')
        super().save(*args, **kwargs)


class Enrollment(TimedModel):
    class DiagnosticStatusType(DjangoChoices):
        NOT_STARTED = ChoiceItem('not_started')
        IN_PROGRESS = ChoiceItem('in_progress')
        COMPLETED = ChoiceItem('completed')

    student = models.ForeignKey(
        'profiles.StudentProfile', related_name='enrollments',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        'Course', related_name='enrollments',
        on_delete=models.CASCADE,
    )
    enabled = models.BooleanField(default=True)
    diagnostic_status = models.CharField(
        max_length=100,
        choices=DiagnosticStatusType.choices,
        default=DiagnosticStatusType.NOT_STARTED,
    )
    course_rated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.course} - {self.student}'

    def save(self, *args, **kwargs):
        if self._state.adding:
            for lecture in self.course.lectures.all():
                session = lecture.sessions.filter(is_default=True).first()
                if not session:
                    raise Exception('Sessions for lecture {}'
                        ' are not created'.format(lecture))
                params = {
                    'session': session,
                    'student': self.student,
                }
                SessionStudent.objects.create(**params)
        super().save(*args, **kwargs)


class Material(TimedModel):
    course = models.ForeignKey(
        'Course', related_name='materials',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    document = S3DirectField(dest='course-document', blank=True)
    enabled = models.BooleanField(default=True)
    file_path_within_bucket = models.CharField(
        max_length=255, null=True, blank=True)

    class GMATType(DjangoChoices):
        analytical_writing_assessment = ChoiceItem(
            'analytical_writing_assessment', 'Analytical Writing Assessment')
        integrated_reasoning = ChoiceItem(
            'integrated_reasoning', 'Integrated Reasoning')
        quantitative_reasoning = ChoiceItem(
            'quantitative_reasoning', 'Quantitative Reasoning')
        verbal_reasoning = ChoiceItem(
            'verbal_reasoning', 'Verbal Reasoning')

    gmat = models.CharField(
        max_length=100,
        choices=GMATType.choices,
        null=True, blank=True,
    )

    class SATType(DjangoChoices):
        essay = ChoiceItem('essay', 'Essay')
        math = ChoiceItem('math', 'Math')
        reading = ChoiceItem('reading', 'Reading')
        writing_and_language = ChoiceItem(
            'writing_and_language', 'Writing and Language')

    sat = models.CharField(
        max_length=100,
        choices=SATType.choices,
        null=True, blank=True,
    )

    class GREType(DjangoChoices):
        analytical_writing = ChoiceItem(
            'analytical_writing', 'Analytical Writing')
        quantitative_reasoning = ChoiceItem(
            'quantitative_reasoning', 'Quantitative Reasoning')
        verbal_reasoning = ChoiceItem('verbal_reasoning', 'Verbal Reasoning')

    gre = models.CharField(
        max_length=100,
        choices=GREType.choices,
        null=True, blank=True,
    )

    class Meta:
        verbose_name_plural = 'Course Content'

    def __str__(self):
        return f'Material ({self.id}) course({self.course.id})'

    def clean(self):
        SUBCATEGORIES = ['sat', 'gmat', 'gre']
        subcategory_list = [getattr(self, sub) for sub in SUBCATEGORIES]
        subcategory_list = [sub for sub in subcategory_list if sub]
        if len(subcategory_list) > 1:
            raise ValidationError('You need add only 1 subcategory')
        existing_subs = []
        added_sub = None
        for sub in SUBCATEGORIES:
            params = {f'{sub}__isnull': False}
            if self.course.materials.filter(**params).exists():
                existing_subs.append(sub)
            if getattr(self, sub):
                added_sub = sub

        if existing_subs and added_sub not in existing_subs:
            raise ValidationError('In all materials can be only 1 subcategory')


class Rating(TimedModel):
    course = models.ForeignKey(
        'Course', related_name='ratings',
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        'profiles.StudentProfile', related_name='ratings',
        on_delete=models.CASCADE, null=True,
    )
    parameters = {
        'default': 0,
        'validators': [MinValueValidator(0), MaxValueValidator(5)],
    }
    ease_of_use = models.PositiveSmallIntegerField(
        verbose_name='Ease of use', **parameters)
    customer_service = models.PositiveSmallIntegerField(
        verbose_name='Customer Service', **parameters)
    met_learning_objectives = models.PositiveSmallIntegerField(
        verbose_name='Met Learning Objectives', **parameters)
    supporting_materials = models.PositiveSmallIntegerField(
        verbose_name='Supporting Materials', **parameters)
    teacher = models.PositiveSmallIntegerField(
        verbose_name='Teacher', **parameters)
    value_for_money = models.PositiveSmallIntegerField(
        verbose_name='Value for money', **parameters)
    likehihood_to_recommend = models.PositiveSmallIntegerField(
        verbose_name='Likehihood to recommend', **parameters)

    rating_weight = models.FloatField(
        verbose_name='Rating',
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    description = models.TextField()
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Course Ratings'

    def __str__(self):
        return f'{self.course} - Rating: {self.rating_weight}'

    def save(self, *args, **kwargs):
        FIELDS_LIST = (
            'ease_of_use', 'customer_service',
            'met_learning_objectives', 'supporting_materials',
            'teacher', 'value_for_money', 'likehihood_to_recommend',
        )
        sum_weight = 0
        for field in FIELDS_LIST:
            sum_weight += getattr(self, field)
        self.rating_weight = round(sum_weight / len(FIELDS_LIST), 2)
        super(Rating, self).save(*args, **kwargs)

    @property
    def get_average_rating(self):
        FIELDS_LIST = (
            'ease_of_use', 'customer_service',
            'met_learning_objectives', 'supporting_materials',
            'teacher', 'value_for_money', 'likehihood_to_recommend',
        )
        sum_rating = 0
        for field in FIELDS_LIST:
            sum_rating += getattr(self, field)
        return sum_rating / len(FIELDS_LIST)


class Assessment(TimedModel):
    DIAGNOSTIC = 'diagnostic'
    QUIZ = 'quiz'
    MIDTERM_EXAM = 'midterm_exam'
    FINAL_EXAM = 'final_exam'
    ASSESSMENT_TYPE = (
        (DIAGNOSTIC, 'Diagnostic'),
        (QUIZ, 'Quiz'),
        (MIDTERM_EXAM, 'Midterm Exam'),
        (FINAL_EXAM, 'Final Exam'),
    )
    course = models.ForeignKey(
        'Course', related_name='assessments',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(
        null=True, blank=True,
        verbose_name='Assessment Description',
    )
    duration = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Minutes',
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_number_of_retries = models.PositiveSmallIntegerField(default=1)
    enabled = models.BooleanField(default=True)
    # is_valid is needed for DiagnosticTest to choose one of 3 options
    is_valid = models.BooleanField(default=True)
    total_score = models.IntegerField(null=False)
    assessment_type = models.CharField(
        max_length=20,
        choices=ASSESSMENT_TYPE,
        default='quiz',
    )

    class Meta:
        verbose_name_plural = 'Assessments'
        verbose_name = 'Assessment'

    def __str__(self):
        return f'{self.title}'

    def clean(self):
        if self.is_valid and self.assessment_type == self.DIAGNOSTIC:
            if self.course.assessments.filter(
                assessment_type=self.DIAGNOSTIC, is_valid=True,
            ).exists():
                raise ValidationError(
                    'Should be only one valid Diagnostic Test')

    def save(self, *args, **kwargs):
        self.duration = get_duration(self.start_date, self.end_date)
        super(Assessment, self).save(*args, **kwargs)

    def get_selected_choices(self, student_id):
        return AssessmentChoice.objects.filter(
            answers__student=student_id,
            question__assessment=self,
        )

    def get_right_choices(self):
        return AssessmentChoice.objects.filter(
            is_valid=True,
            question__assessment=self,
        )

    def get_student_result(self, student_id):
        # get right answers for multiple questions
        set_multiple_choice_ids = set(AssessmentChoice.objects.filter(
            answers__student=student_id,
            question__assessment=self,
            is_valid=True,
        ).values_list('id', flat=True))

        multiple_questions = self.questions.all()

        right_choices_count = 0
        for question in multiple_questions:
            set_right_choice_ids = set(question.choices.filter(
                is_valid=True).values_list('id', flat=True))
            intersection = set_right_choice_ids.intersection(
                set_multiple_choice_ids)
            if intersection == set_right_choice_ids:
                right_choices_count += 1
        question_count = self.questions.count()

        return {
            'right_answers': right_choices_count,
            'all_question': question_count,
        }


class AssessmentQuestion(TimedModel):
    assessment = models.ForeignKey(
        'Assessment', related_name='questions',
        on_delete=models.CASCADE,
        null=True, blank=True,
    )
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(
        null=True, blank=True,
        verbose_name='Question Description',
    )
    enabled = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Questions'
        verbose_name = 'Question'

    def save(self, *args, **kwargs):
        if not self.id:
            max_order = self.assessment.questions.aggregate(Max('order'))
            max_order = max_order['order__max']
            if max_order is not None:
                self.order = max_order + 1
            else:
                self.order = 1
        super(AssessmentQuestion, self).save(*args, **kwargs)


class AssessmentChoice(TimedModel):
    question = models.ForeignKey(
        'AssessmentQuestion', related_name='choices',
        on_delete=models.CASCADE,
        null=True, blank=True,
    )
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField()
    is_valid = models.BooleanField(default=True, verbose_name='Correct')
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name_plural = 'Choices'
        verbose_name = 'Choice'

    def first_question(self):
        if self.question.order == 1:
            return True
        return False

    def last_question(self):
        questions_count = self.get_assessment().questions.count()
        if self.question.order == questions_count:
            return True
        return False

    def get_assessment(self):
        return self.question.assessment


class AssessmentAnswer(TimedModel):
    student = models.ForeignKey(
        'profiles.StudentProfile', related_name='answers',
        on_delete=models.CASCADE,
    )
    choice = models.ForeignKey(
        'AssessmentChoice', related_name='answers',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = 'Assessment Answers'

    def __str__(self):
        return f'student: {self.student} choice: {self.choice}'


class TestCourse(TimedModel):
    course = models.ForeignKey(
        'Course', related_name='testcourse',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='testcourse',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = 'Test Course'


class Session(TimedModel):
    id = models.CharField(
        max_length=40,
        primary_key=True,
        default=get_random_id,
        editable=False,
    )
    lecture = models.ForeignKey(
        to='Lecture',
        related_name='sessions',
        on_delete=models.CASCADE,
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    duration = models.IntegerField(
        null=False,
        validators=[MinValueValidator(1)],
        help_text='Minutes',
    )
    is_default = models.BooleanField(default=False)
    description = models.TextField(null=True)

    class Meta:
        ordering = ['end_date']
        verbose_name_plural = 'Course Lecture Sessions'

    def save(self, *args, **kwargs):
        self.duration = get_duration(self.start_date, self.end_date)
        if not self.lecture.sessions.filter(is_default=True).exists():
            self.is_default = True
        super(Session, self).save(*args, **kwargs)

    @property
    def can_join(self):
        current = now()
        # if lesson has already started, allow joining
        if self.start_date <= current:
            return True

        # allow joining some mins before the lesson starts
        mins_before_join = 20
        time = self.start_date - current
        return time.total_seconds() / 60 <= mins_before_join


class StudentScore(TimedModel):
    assessment = models.ForeignKey(
        'group_courses.Assessment', related_name='student_score',
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        'profiles.StudentProfile', related_name='student_score',
        on_delete=models.CASCADE,
    )
    score = models.IntegerField(
        null=False,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name_plural = 'Students Scores'
