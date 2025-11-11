from django.urls import path
from .views import PostLikeView

app_name = "likes"

urlpatterns = [
    path("posts/<str:post_id>/like", PostLikeView.as_view(), name="post-like"),
]
