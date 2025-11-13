from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from apps.community.posts.services.listing_router import list_posts
from apps.community.posts.services.create import create_post
from apps.community.posts.services.detail import get_post_detail
from apps.community.posts.services.update import patch_post
from apps.community.posts.services.delete import delete_post


class PostsView(APIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == "POST" else [AllowAny()]

    def get(self, request, *args, **kwargs):
        return list_posts(request)

    def post(self, request, *args, **kwargs):
        return create_post(request)


class PostDetailView(APIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, post_id: str, *args, **kwargs):
        return get_post_detail(request, post_id)

    def patch(self, request, post_id: str, *args, **kwargs):
        return patch_post(request, post_id)

    def delete(self, request, post_id: str, *args, **kwargs):
        return delete_post(request, post_id)
