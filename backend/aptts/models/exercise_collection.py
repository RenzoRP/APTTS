from django.db import models
from django.conf import settings

class ExerciseCollection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    courses = models.ManyToManyField('Course', related_name='collections', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='collections_created')
    exercises = models.ManyToManyField('Exercise',related_name='in_collections',blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title