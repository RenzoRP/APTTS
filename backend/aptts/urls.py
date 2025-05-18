from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views.user_view import UserViewSet, register, login_view, logout_view, change_password, google_login
from .views.course_view import CourseViewSet
from .views.exercise_collection_view import ExerciseCollectionViewSet
from .views.exercise_view import ExerciseViewSet
from .views.submission_view import SubmissionViewSet
from .views.feedback_view import FeedbackViewSet
from .views.tracking_view import tracking_history
from .views.file_upload_view import upload_exercise_file

# Main router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'collections', ExerciseCollectionViewSet, basename='collection')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

router.register(r'exercises', ExerciseViewSet, basename='exercise')

# Nested router for exercises under collections
collections_router = NestedSimpleRouter(router, r'collections', lookup='collection')
collections_router.register(r'exercises', ExerciseViewSet, basename='collection-exercises')

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Core API endpoints
    path('api/', include(router.urls)),
    path('api/', include(collections_router.urls)),

    # Auth and user management
    path('api/auth/register/', register),
    path('api/auth/login/', login_view),
    path('api/auth/logout/', logout_view),
    path('api/auth/change-password/', change_password),
    path('api/auth/google-login/', google_login),

    # File upload
    path('api/utils/upload_exercise_file/', upload_exercise_file),

    # Tracking and analytics
    path('api/tracking/history/', tracking_history),
]
