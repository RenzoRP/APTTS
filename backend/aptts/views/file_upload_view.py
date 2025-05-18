from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models.exercise import Exercise
from ..models.exercise_collection import ExerciseCollection
from django.core.exceptions import ValidationError
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_exercise_file(request):
    file = request.FILES.get('file')
    collection_id = request.data.get('collection_id')

    if not file or not collection_id:
        return Response({'error': 'Missing file or collection_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        collection = ExerciseCollection.objects.get(id=collection_id, course__instructor=request.user)
    except ExerciseCollection.DoesNotExist:
        return Response({'error': 'Collection not found or not owned by user'}, status=status.HTTP_403_FORBIDDEN)

    try:
        content = file.read().decode('utf-8')
        lines = content.splitlines()
        title = lines[0].strip()
        description = '\n'.join(lines[1:]).strip()

        # Placeholder test cases and solution
        Exercise.objects.create(
            title=title,
            description=description,
            difficulty='easy',
            optimal_solution='def solution(x): return x',
            test_cases=[{"input": 1, "output": 1}],
            collection=collection,
            created_by=request.user
        )

        return Response({'message': 'Exercise created from file.'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)