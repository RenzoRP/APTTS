from django.db import models
from django.conf import settings

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructed_courses'
    )

    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='enrolled_courses',
        blank=True
    )

    pending_requests = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='pending_courses',
        blank=True
    )

    public = models.BooleanField(default=False)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name