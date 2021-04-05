from django.db import models
from django.utils import timezone


class LectureQuerySet(models.QuerySet):
    def upcoming(self):
        from_ = timezone.now()
        until = from_ + timezone.timedelta(days=15)
        return self.filter(
            sessions__session_student__session__start_date__gte=from_,
            sessions__session_student__session__start_date__lte=until,
        )

    def past(self):
        from_ = timezone.now()
        return self.filter(
            sessions__session_student__session__end_date__lte=from_,
        )
