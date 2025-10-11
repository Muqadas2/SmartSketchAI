# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('hello/', views.hello),
#     path('generate/', views.generate),
#     path('edit/', views.edit),
#     path('score/', views.score),
#     path('audit/', views.audit),
# ]

from django.urls import path
from .views import (
    HelloView,
    TrainingJobListView,
    TrainingJobCreateView,
    TrainingJobDetailView,
    GeneratedImageListView
)

urlpatterns = [
    path('hello/', HelloView.as_view(), name='hello'),

    # Training Job endpoints
    path('training/jobs/', TrainingJobListView.as_view(), name='training-jobs'),
    path('training/jobs/create/', TrainingJobCreateView.as_view(), name='training-create'),
    path('training/jobs/<uuid:job_id>/', TrainingJobDetailView.as_view(), name='training-detail'),

    # Generated Images endpoints
    path('images/', GeneratedImageListView.as_view(), name='generated-images'),
]
