from rest_framework import viewsets, permissions, decorators, response, status
from ..models.exercise import Exercise
from ..models.exercise_collection import ExerciseCollection
from ..serializers.exercise_serializer import ExerciseSerializer

class IsCreatorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def by_collection(self, request):
        collection_id = request.query_params.get('collection_id')
        if not collection_id:
            return response.Response({'error': 'Missing collection_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = ExerciseCollection.objects.get(id=collection_id)
        except ExerciseCollection.DoesNotExist:
            return response.Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

        exercises = collection.exercises.all()
        serializer = self.get_serializer(exercises, many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_to_collection(self, request, pk=None):
        exercise = self.get_object()
        collection_id = request.data.get('collection_id')
        if not collection_id:
            return response.Response({'error': 'Missing collection_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = ExerciseCollection.objects.get(id=collection_id)
        except ExerciseCollection.DoesNotExist:
            return response.Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

        collection.exercises.add(exercise)
        return response.Response({'message': 'Exercise added to collection'})

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def remove_from_collection(self, request, pk=None):
        exercise = self.get_object()
        collection_id = request.data.get('collection_id')
        if not collection_id:
            return response.Response({'error': 'Missing collection_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = ExerciseCollection.objects.get(id=collection_id)
        except ExerciseCollection.DoesNotExist:
            return response.Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

        collection.exercises.remove(exercise)
        return response.Response({'message': 'Exercise removed from collection'})