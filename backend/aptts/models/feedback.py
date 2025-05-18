from django.db import models
from .submission import Submission
from .user import User
from .exercise import Exercise

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('start_hint', 'Start Hint'),
        ('middle_hint', 'Middle Hint'),
        ('submission_help', 'Submission Help'),
        ('post_success_feedback', 'Post Success Feedback'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=30, choices=FEEDBACK_TYPES)
    content = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)