from django_filters import rest_framework as filters

from edutailors.apps.group_courses.models import Course


class CourseFilterSet(filters.FilterSet):
    min_cost = filters.NumberFilter(
        field_name='cost',
        lookup_expr='gte',
    )
    max_cost = filters.NumberFilter(
        field_name='cost',
        lookup_expr='lte',
    )
    rating_gte = filters.NumberFilter(
        method='rating_filter',
        lookup_expr='gte',
    )
    level = filters.ChoiceFilter(
        field_name='level',
        choices=Course.LevelType.choices,
    )
    date = filters.DateFromToRangeFilter(method='availability')
    is_adaptive = filters.BooleanFilter()
    test_drive = filters.BooleanFilter()
    search = filters.CharFilter(method='search_filter')
    subject = filters.NumberFilter()

    def search_filter(self, queryset, name, value):
        return queryset.filter(title__icontains=value)

    def rating_filter(self, queryset, name, value):
        course_ids = [
            course.id for course in queryset
            if course.get_average_rating
            if course.get_average_rating >= value
        ]
        return queryset.filter(id__in=course_ids)

    def availability(self, queryset, name, value):
        start = value.start
        stop = value.stop
        filtered_courses = queryset.filter(
            start_date__gte=start,
            end_date__lte=stop)
        return filtered_courses

    class Meta:
        model = Course
        fields = [
            'min_cost', 'max_cost', 'rating_gte',
            'level', 'is_adaptive', 'test_drive',
        ]
