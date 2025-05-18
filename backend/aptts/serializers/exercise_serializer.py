from rest_framework import serializers
from ..models.exercise import Exercise

class ExerciseSerializer(serializers.ModelSerializer):
    in_collections = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Exercise
        fields = '__all__'
        read_only_fields = ['created_by']