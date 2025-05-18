from django.db import models
from .user import User
from .exercise import Exercise

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    code = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    attempt_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Submission #{self.attempt_number} by {self.user.username} on {self.exercise.title}"