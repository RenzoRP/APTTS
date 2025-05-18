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

        # Try to reuse an existing global hint (shared hint)
        existing_hint = Feedback.objects.filter(exercise=exercise, type='start_hint', submission__isnull=True).first()
        if existing_hint:
            return Response({'content': existing_hint.content}, status=status.HTTP_200_OK)

        # Generate with OpenAI
        prompt = self.build_prompt('start_hint', request.user, exercise, None)
        content = generate_openai_feedback(prompt)

        # Save without a user and submission for reuse
        Feedback.objects.create(
            exercise=exercise,
            type='start_hint',
            content=content
        )
        return Response({'content': content}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='middle_hint')
    def middle_hint(self, request):
        return self._create_feedback(request, type='middle_hint')

    @action(detail=False, methods=['post'], url_path='submission_help')
    def submission_help(self, request):
        return self._create_feedback(request, type='submission_help', require_submission=True)

    @action(detail=False, methods=['post'], url_path='post_success_feedback')
    def post_success_feedback(self, request):
        return self._create_feedback(request, type='post_success_feedback', require_submission=True, require_passing=True)

    def _create_feedback(self, request, type, require_submission=False, require_passing=False):
        exercise_id = request.data.get('exercise_id')
        submission_id = request.data.get('submission_id') if require_submission else None

        if not exercise_id:
            return Response({'error': 'exercise_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        exercise = get_object_or_404(Exercise, id=exercise_id)
        submission = None

        if submission_id:
            submission = get_object_or_404(Submission, id=submission_id, user=request.user)
            if require_passing and submission.score < 1.0:
                return Response({'error': 'Only passing submissions can receive this type of feedback'}, status=status.HTTP_400_BAD_REQUEST)

        prompt = self.build_prompt(type, request.user, exercise, submission)
        content = generate_openai_feedback(prompt)

        feedback = Feedback.objects.create(
            user=request.user,
            exercise=exercise,
            submission=submission,
            type=type,
            content=content
        )
        serializer = self.get_serializer(feedback)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def build_prompt(self, type, user, exercise, submission):
        if type == 'start_hint':
            return f"Give a student an idea of how to start solving this Python exercise:\n\n{exercise.description}"
        elif type == 'middle_hint':
            return f"A student is stuck midway through this exercise:\n\n{exercise.description}\n\nGive a next-step hint."
        elif type == 'submission_help' and submission:
            return f"A student submitted this code for an exercise:\n\n{submission.code}\n\nIt failed.\nHelp the student identify likely issues and suggest improvements."
        elif type == 'post_success_feedback' and submission:
            return f"A student submitted this correct solution:\n\n{submission.code}\n\nGive them praise and a short improvement suggestion compared to this optimal one:\n\n{exercise.optimal_solution}"
        return "Give helpful feedback."
