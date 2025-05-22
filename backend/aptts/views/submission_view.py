from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models.submission import Submission
from ..serializers.submission_serializer import SubmissionSerializer
from ..models.exercise import Exercise
from ..models.feedback import Feedback
from ..serializers.feedback_serializer import FeedbackSerializer
from multiprocessing import Manager, Process
from aptts.services.code_runner_service import execute_user_code
import ast

class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Submission.objects.all()

        # Only let instructors see submissions to their exercises
        # And students see only their own
        if user.role == 'student':
            qs = qs.filter(user=user)
        elif user.role == 'instructor':
            qs = qs.filter(exercise__created_by=user)

        # Apply filtering by exercise ID from query param
        exercise_id = self.request.query_params.get('exercise')
        if exercise_id:
            qs = qs.filter(exercise__id=exercise_id)

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        exercise = serializer.validated_data['exercise']
        code = serializer.validated_data['code']

        try:
            ast.parse(code, filename="user_submission")
        except SyntaxError as e:
            print(e)
            return Response({
                "type": "syntax",
                "error": f"{e.msg} at line {e.lineno}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Run all test cases before creating submission
        test_cases = exercise.test_cases
        passed = 0
        feedback_lines = []

        for idx, case in enumerate(test_cases):
            input_data = case['input']
            expected_output = str(case['expected_output']).strip()

            output, error = self.run_code_with_timeout(code, input_data, exercise.print_based)
            if error:
                return Response({
                    "type": "runtime",
                    "error": f"Test {idx+1} error: {error}"
                }, status=status.HTTP_400_BAD_REQUEST)

            if output == expected_output:
                passed += 1
                feedback_lines.append(f"Test {idx+1} passed.")
            else:
                feedback_lines.append(f"Test {idx+1} failed: expected {expected_output}, got {output}")

        score = round(passed / len(test_cases), 2) if test_cases else 0.0
        feedback_text = "\n".join(feedback_lines)

        attempt_count = Submission.objects.filter(user=user, exercise=exercise).count()
        submission = serializer.save(user=user, attempt_number=attempt_count + 1, score=score)

        return Response({
            'message': 'Submission created successfully',
            'score': submission.score,
            'passed': submission.score == 1.0,
            'feedback': feedback_text,
            'submission_id': submission.id,
        }, status=status.HTTP_201_CREATED)

    def run_code_with_timeout(self, code, input_data, print_based, timeout=2):
        manager = Manager()
        return_dict = manager.dict()
        process = Process(target=execute_user_code, args=(code, input_data, print_based, return_dict))
        process.start()
        process.join(timeout)
        if process.is_alive():
            process.terminate()
            return None, 'Execution timed out'
        return return_dict.get('output'), return_dict.get('error')