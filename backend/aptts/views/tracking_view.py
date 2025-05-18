from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models.submission import Submission

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tracking_history(request):
    user = request.user

    submissions = Submission.objects.filter(user=user).order_by('-timestamp')

    results = []
    for s in submissions:
        results.append({
            'submission_id': s.id,
            'exercise_id': s.exercise.id,
            'exercise_title': s.exercise.title,
            'timestamp': s.timestamp.isoformat(),
            'attempts': s.attempt_number,
            'passed': s.score == 1.0,
        })

    return Response(results, status=status.HTTP_200_OK)