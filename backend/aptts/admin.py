from django.contrib import admin
from .models import (
    User,
    Course,
    ExerciseCollection,
    Exercise,
    Submission,
    Feedback
)

admin.site.register(User)
admin.site.register(Course)
admin.site.register(ExerciseCollection)
admin.site.register(Exercise)
admin.site.register(Submission)
admin.site.register(Feedback)
