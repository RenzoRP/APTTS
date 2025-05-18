from rest_framework import viewsets, permissions, decorators, response, status
from ..models.exercise_collection import ExerciseCollection
from ..models.course import Course
from ..models.exercise import Exercise
from ..serializers.exercise_collection_serializer import ExerciseCollectionSerializer
from ..serializers.exercise_serializer import ExerciseSerializer

class IsInstructorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user

class ExerciseCollectionViewSet(viewsets.ModelViewSet):
    queryset = ExerciseCollection.objects.all()
    serializer_class = ExerciseCollectionSerializer
    permission_classes = [IsInstructorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def by_course(self, request):
        course_id = request.query_params.get('course_id')
        if not course_id:
            return response.Response({'error': 'Missing course_id parameter'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return response.Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        collections = ExerciseCollection.objects.filter(courses=course)
        serializer = self.get_serializer(collections, many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def exercises(self, request, pk=None):
        collection = self.get_object()
        exercises = collection.exercises.all()
        serializer = ExerciseSerializer(exercises, many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_exercise(self, request, pk=None):
        collection = self.get_object()
        exercise_id = request.data.get('exercise_id')
        if not exercise_id:
            return response.Response({'error': 'Missing exercise_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            exercise = Exercise.objects.get(id=exercise_id)
        except Exercise.DoesNotExist:
            return response.Response({'error': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

        collection.exercises.add(exercise)
        return response.Response({'message': 'Exercise added to collection'}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def remove_exercise(self, request, pk=None):
        collection = self.get_object()
        exercise_id = request.data.get('exercise_id')
        if not exercise_id:
            return response.Response({'error': 'Missing exercise_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            exercise = Exercise.objects.get(id=exercise_id)
        except Exercise.DoesNotExist:
            return response.Response({'error': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

        collection.exercises.remove(exercise)
        return response.Response({'message': 'Exercise removed from collection'}, status=status.HTTP_200_OK)
    
    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_course(self, request, pk=None):
        collection = self.get_object()
        course_id = request.data.get("course_id")

        if not course_id:
            return response.Response({"error": "Missing course_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return response.Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        collection.courses.add(course)
        return response.Response({"message": "Course added to collection"}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def remove_course(self, request, pk=None):
        collection = self.get_object()
        course_id = request.data.get("course_id")

        if not course_id:
            return response.Response({"error": "Missing course_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return response.Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        collection.courses.remove(course)
        return response.Response({"message": "Course removed from collection"}, status=status.HTTP_200_OK)