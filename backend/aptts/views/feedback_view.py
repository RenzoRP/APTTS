from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.feedback import Feedback
from ..serializers.feedback_serializer import FeedbackSerializer
from ..models.exercise import Exercise
from ..models.submission import Submission
from django.shortcuts import get_object_or_404
from ..services.ai_service import generate_openai_feedback

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='start_hint')
    def start_hint(self, request):
        exercise_id = request.data.get('exercise_id') or request.data.get('exercise')
        if not exercise_id:
            return Response({'error': 'exercise_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        exercise = get_object_or_404(Exercise, id=exercise_id)

        existing_hint = Feedback.objects.filter(exercise=exercise, type='start_hint', submission__isnull=True).first()
        if existing_hint:
            return Response({'content': existing_hint.content}, status=status.HTTP_200_OK)

        prompt = f"Give a student an idea of how to start solving this Python exercise:\n\n{exercise.description}"
        content = generate_openai_feedback(prompt)

        Feedback.objects.create(
            exercise=exercise,
            type='start_hint',
            content=content
        )
        return Response({'content': content}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='middle_hint')
    def middle_hint(self, request):
        exercise_id = request.data.get('exercise_id')
        if not exercise_id:
            return Response({'error': 'exercise_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        exercise = get_object_or_404(Exercise, id=exercise_id)

        prompt = f"A student is stuck midway through this exercise:\n\n{exercise.description}\n\nGive a next-step hint."
        content = generate_openai_feedback(prompt)

        feedback = Feedback.objects.create(
            user=request.user,
            exercise=exercise,
            type='middle_hint',
            content=content
        )
        return Response({'text': content}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='submission_help')
    def submission_help(self, request):
        print(request.data)
        exercise_id = request.data.get('exercise_id')
        submission_id = request.data.get('submission_id')
        error = request.data.get('error')

        if not exercise_id or not submission_id or not error:
            return Response({'error': 'exercise_id, submission_id, and error are required'}, status=status.HTTP_400_BAD_REQUEST)

        exercise = get_object_or_404(Exercise, id=exercise_id)
        submission = get_object_or_404(Submission, id=submission_id)
        
        prompt = (
            f"A student was tasked with coding a solution to:\n\n{exercise.description}\n\n"
            f"The student submitted the following Python code for an exercise:\n\n{submission.code}\n\n"
            f"It failed with this feedback or error:\n{error}\n\n"
            f"Help the student understand what went wrong and suggest specific improvements."
        )
        content = generate_openai_feedback(prompt)

        Feedback.objects.create(
            user=request.user,
            exercise=exercise,
            type='submission_help',
            content=content
        )
        return Response({'text': content}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='post_success_feedback')
    def post_success_feedback(self, request):
        print(request)
        exercise_id = request.data.get('exercise_id')
        submission_id = request.data.get('submission_id')

        if not exercise_id or not submission_id:
            return Response({'error': 'exercise_id and submission_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        exercise = get_object_or_404(Exercise, id=exercise_id)
        submission = get_object_or_404(Submission, id=submission_id)

        prompt = (
            f"A student was tasked with coding a solution to:\n\n{exercise.description}\n\n"
            f"The student submitted the following correct Python solution:\n\n{submission.code}\n\n"
            f"The optimal solution is:\n\n{exercise.optimal_solution}\n\n"
            f"Praise the student and suggest improvements to make their code closer to the optimal one."
        )
        content = generate_openai_feedback(prompt)

        Feedback.objects.create(
            user=request.user,
            exercise=exercise,
            type='post_success_feedback',
            content=content,
            submission=submission
        )
        return Response({'text': content}, status=status.HTTP_201_CREATED)