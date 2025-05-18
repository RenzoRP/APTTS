from django.db import models
from .exercise_collection import ExerciseCollection
from django.conf import settings

class Exercise(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    optimal_solution = models.TextField()
    test_cases = models.JSONField(default=list)
    print_based = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_exercises')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.difficulty})"