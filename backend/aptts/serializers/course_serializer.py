from rest_framework import serializers
from ..models.course import Course
from ..serializers.user_serializer import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField(read_only=True)
    students = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['instructor']