# apps/community/posts/views.py
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from apps.community.posts.services.listing_router import list_posts
from apps.community.posts.services.create import create_post


class PostsView(APIView):
    """
    GET  /posts  -> list_posts (view=main/community)
    POST /posts  -> create_post (JSON & multipart, 이미지 옵션)
    """
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == "POST" else [AllowAny()]

    # ✅ 뷰에는 얇은 래퍼만 두고 서비스 호출
    def get(self, request, *args, **kwargs):
        return list_posts(request)

    def post(self, request, *args, **kwargs):
        return create_post(request)
