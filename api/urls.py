# api/urls.py
from django.urls import path
from .views import RegisterView, ProfileView, MyGeneratedImagesView, AuditLogListView, ForensicRequestCreateView, ForensicApproveView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# frontend
from .views import generate_forensic_sketch, edit_forensic_sketch

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # login -> JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('my-images/', MyGeneratedImagesView.as_view(), name='my_images'),
    path('audit-logs/', AuditLogListView.as_view(), name='audit_logs'),
    path('forensic-requests/', ForensicRequestCreateView.as_view(), name='forensic_requests'),
    path('forensic-requests/<int:pk>/approve/', ForensicApproveView.as_view(), name='forensic_approve'),
    path("forensic/generate/", generate_forensic_sketch),
    path("forensic/edit/", edit_forensic_sketch),
]

