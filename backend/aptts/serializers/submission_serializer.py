from rest_framework import serializers 
from ..models.submission import Submission

class SubmissionSerializer(serializers.ModelSerializer):
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            'id', 'exercise', 'exercise_title', 'code', 'timestamp',
            'score', 'attempt_number', 'status', 'username'
        ]
        read_only_fields = [
            'id', 'timestamp', 'score', 'attempt_number',
            'exercise_title', 'status', 'username'
        ]

    def get_status(self, obj):
        return "Passed" if obj.score == 1.0 else "Failed"

    def create(self, validated_data):
        return Submission.objects.create(**validated_data)
