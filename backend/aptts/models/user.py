from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (INSTRUCTOR, 'Instructor'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    institution = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"