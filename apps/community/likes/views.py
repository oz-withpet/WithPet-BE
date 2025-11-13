from rest_framework.views import APIView
from .services import status as like_status, on as like_on, off as like_off

class PostLikeView(APIView):
    def get(self, request, post_id: str, *args, **kwargs):
        return like_status(request, post_id)

    def put(self, request, post_id: str, *args, **kwargs):
        return like_on(request, post_id)

    def delete(self, request, post_id: str, *args, **kwargs):
        return like_off(request, post_id)
