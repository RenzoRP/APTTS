from rest_framework import viewsets, permissions, decorators, response, status
from django_filters.rest_framework import DjangoFilterBackend
from ..models.course import Course
from ..serializers.course_serializer import CourseSerializer

class IsInstructorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.instructor == request.user

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['instructor', 'students']

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructorOrReadOnly()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        course.students.add(request.user)
        return response.Response({'message': 'Enrolled successfully'}, status=status.HTTP_200_OK)
    
    @decorators.action(detail=True, methods=['get'], url_path='pending', permission_classes=[permissions.IsAuthenticated])
    def pending_requests(self, request, pk=None):
        course = self.get_object()
        if course.instructor != request.user:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        pending = course.pending_requests.all()
        return response.Response(UserSerializer(pending, many=True).data)

    @decorators.action(detail=True, methods=['post'], url_path='approve', permission_classes=[permissions.IsAuthenticated])
    def approve_request(self, request, pk=None):
        course = self.get_object()
        if course.instructor != request.user:
            return response.Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        if user in course.pending_requests.all():
            course.pending_requests.remove(user)
            course.students.add(user)
            return response.Response({'message': 'User approved and enrolled'}, status=status.HTTP_200_OK)
        return response.Response({'error': 'User not in pending list'}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=['post'], url_path='reject', permission_classes=[permissions.IsAuthenticated])
    def reject_request(self, request, pk=None):
        course = self.get_object()
        if course.instructor != request.user:
            return response.Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        if user in course.pending_requests.all():
            course.pending_requests.remove(user)
            return response.Response({'message': 'User request rejected'}, status=status.HTTP_200_OK)
        return response.Response({'error': 'User not in pending list'}, status=status.HTTP_400_BAD_REQUEST)