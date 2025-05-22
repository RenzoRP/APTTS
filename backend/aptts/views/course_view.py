from rest_framework import viewsets, permissions, decorators, response, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models.course import Course
from ..models.user import User
from ..serializers.course_serializer import CourseSerializer
from ..serializers.user_serializer import UserSerializer

class IsCourseParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Block access to retrieve unless instructor or enrolled student
        if view.action == "retrieve":
            return obj.instructor == request.user or request.user in obj.students.all()
        return True

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

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Course.objects.none()

        if user.role == 'instructor':
            return Course.objects.filter(instructor=user)

        if user.role == 'student':
            return Course.objects.filter(students=user)

        return Course.objects.none()

    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated(), IsCourseParticipant()]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructorOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        # Always allow access to the object, but restrict actions via permissions or inside views
        obj = Course.objects.get(pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        user = request.user

        if course.public is not True:
            return response.Response({'error': 'Cannot enroll directly in private courses'}, status=status.HTTP_403_FORBIDDEN)

        if user in course.students.all():
            return response.Response({'message': 'Already enrolled'}, status=status.HTTP_200_OK)

        course.students.add(user)
        return response.Response({'message': 'Enrolled successfully'}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=['post'], url_path='request', permission_classes=[permissions.IsAuthenticated])
    def request_access(self, request, pk=None):
        course = self.get_object()
        user = request.user

        if course.public:
            return response.Response({'error': 'No access request needed for public courses'}, status=status.HTTP_403_FORBIDDEN)

        if user in course.students.all():
            return response.Response({'message': 'Already enrolled'}, status=status.HTTP_200_OK)

        if user in course.pending_requests.all():
            return response.Response({'message': 'Already requested access'}, status=status.HTTP_200_OK)

        course.pending_requests.add(user)
        return response.Response({'message': 'Access request submitted'}, status=status.HTTP_200_OK)

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

    @decorators.action(detail=False, methods=['get'], url_path='public', permission_classes=[permissions.IsAuthenticated])
    def course_summary_list(self, request):
        user = request.user
        courses = Course.objects.prefetch_related("students", "pending_requests").all()

        result = []
        for c in courses:
            if c.instructor == user:
                status_str = "instructor"
            elif user in c.students.all():
                status_str = "enrolled"
            elif user in c.pending_requests.all():
                status_str = "pending"
            else:
                status_str = "not_enrolled"

            result.append({
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "public": c.public,
                "status": status_str
            })

        return response.Response(result, status=status.HTTP_200_OK)