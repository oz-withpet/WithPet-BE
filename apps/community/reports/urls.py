from django.urls import path
from .views import PostReportView

urlpatterns = [
    path("posts/<int:post_id>/report", PostReportView.as_view(), name="post-report"),
]
