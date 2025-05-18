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
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

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

            output, error = self.run_code_with_timeout(code, input_data)
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

        # If we reached here, the code passed validation and can be saved
        attempt_count = Submission.objects.filter(user=user, exercise=exercise).count()
        submission = serializer.save(user=user, attempt_number=attempt_count + 1, score=score)

        Feedback.objects.create(
            submission=submission,
            content=feedback_text,
            exercise=exercise,
            user=user,
            type='submission_help'
        )

        return Response({
            'message': 'Submission created successfully',
            'score': submission.score,
            'passed': submission.score == 1.0,
            'feedback': feedback_text
        }, status=status.HTTP_201_CREATED)

    def run_code_with_timeout(self, code, input_data, timeout=2):
        manager = Manager()
        return_dict = manager.dict()
        process = Process(target=execute_user_code, args=(code, input_data, return_dict))
        process.start()
        process.join(timeout)
        if process.is_alive():
            process.terminate()
            return None, 'Execution timed out'
        return return_dict.get('output'), return_dict.get('error')