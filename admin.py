from django.contrib import admin
from django.forms import Textarea
from django.db import models
from random import choice
import nested_admin

from edutailors.apps.group_courses.models import (
    Course, Lecture, Enrollment,
    Material, Assessment, Rating, AssessmentQuestion,
    AssessmentChoice, Session, StudentScore,
)
from edutailors.apps.big_blue_button.models import MeetingRoom


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'start_date', 'end_date', 'duration', 'is_default', 'lecture',
    )
    actions = ['get_assistant_bbb_link', 'get_tutor_bbb_link']
    readonly_fields = ['duration']

    def generate_password(size=32):
        return ''.join(
            [choice('abcdefghijklmnopqrstuvwxyz0123456789%*-')
             for i in range(size)],
        )

    def get_url(translation, course, user):
        full_name = user.get_full_name()
        if user == course.teacher.user:
            full_name = 'Teacher: ' + full_name
            password = translation.moderator_password
        elif user == course.assistant.user:
            full_name = 'Assistant: ' + full_name
            password = translation.moderator_password
        else:
            password = translation.attendee_password
        return translation.join_url(full_name, password)

    def get_translation_url(role, queryset):
        if queryset.count() != 1:
            raise Exception('You can select only 1 session')
        session = queryset.first()
        course = session.lecture.course
        translation_id = session.id
        defaults = {'name': '{}: {}'.format(
            course.teacher.user.get_full_name(),
            session.lecture.title),
            'attendee_password': SessionAdmin.generate_password(),
            'moderator_password': SessionAdmin.generate_password()}
        translation, created = MeetingRoom.objects.get_or_create(
            meeting_id=translation_id,
            defaults=defaults,
            lesson_type=MeetingRoom.GROUP_COURSE,
            group_session=session)
        if role == 'assistant':
            url = SessionAdmin.get_url(
                translation, course, session.lecture.course.assistant.user)
        else:
            url = SessionAdmin.get_url(
                translation, course, session.lecture.course.teacher.user)
        return url

    def get_assistant_bbb_link(self, request, queryset):
        params = {
            'role': 'assistant',
            'queryset': queryset,
        }
        url = SessionAdmin.get_translation_url(**params)
        self.message_user(request, f'Assistants link: {url}')

    def get_tutor_bbb_link(self, request, queryset):
        url = SessionAdmin.get_translation_url('teacher', queryset)
        self.message_user(request, f'Tutors link: {url}')


class SessionInline(nested_admin.NestedTabularInline):
    model = Session
    extra = 1
    exclude = ['description']
    readonly_fields = ['duration']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 6, 'cols': 50})},
    }


class LectureInline(nested_admin.NestedTabularInline):
    model = Lecture
    extra = 1
    inlines = [
        SessionInline,
    ]
    exclude = ['enabled']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    }


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    exclude = ['enabled']
    list_display = ('student', 'id', 'course', 'created', 'updated')
    list_filter = ['course']


class MaterialInline(nested_admin.NestedTabularInline):
    model = Material
    extra = 1
    exclude = ['file_path_within_bucket', 'enabled']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    }


class AssessmentChoiceInline(nested_admin.NestedTabularInline):
    model = AssessmentChoice
    extra = 0
    exclude = ['description', 'enabled']


class AssessmentQuestionInline(nested_admin.NestedTabularInline):
    model = AssessmentQuestion
    extra = 1
    exclude = ['type']
    inlines = [
        AssessmentChoiceInline,
    ]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    }


class AssessmentInline(nested_admin.NestedTabularInline):
    model = Assessment
    extra = 1
    exclude = ['enabled']
    readonly_fields = ['duration']
    ordering_field = 'assessment_type'
    inlines = [
        AssessmentQuestionInline,
    ]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    }


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = (
        'course', 'rating_weight', 'id', 'description',
    )
    list_filter = ['course']
    search_fields = ['description']
    exclude = ['enabled']


@admin.register(Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        'title', 'id', 'slug', 'description',
        'image', 'start_date', 'end_date', 'cost',
        'capacity', 'created',
        'updated', 'teacher', 'assistant',
    )
    readonly_fields = ['status']
    search_fields = ['title', 'description', 'status']
    list_filter = ['status', 'cost', 'capacity']
    exclude = ['enabled']
    inlines = [
        LectureInline,
        MaterialInline,
        AssessmentInline,
    ]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 6, 'cols': 100})},
    }

    class Media:
        css = {
            'all': ('base.css', 'forms.css'),
        }


@admin.register(StudentScore)
class StudentScoreAdmin(admin.ModelAdmin):
    list_display = (
        'assessment', 'student', 'score',
    )
    list_filter = ['assessment', 'assessment__course']
    search_fields = ['score', 'assessment__title', 'student__user__email']
