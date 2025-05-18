from rest_framework import serializers
from ..models.exercise_collection import ExerciseCollection
from ..models.course import Course
from ..models.exercise import Exercise

class ExerciseCollectionSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Course.objects.all(),
        required=False
    )
    exercises = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Exercise.objects.all(),
        required=False
    )

    class Meta:
        model = ExerciseCollection
        fields = '__all__'
        read_only_fields = ['created_by']
