from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

# GET 라우팅(메인/커뮤니티 분기)
from apps.community.posts.services.listing_router import list_posts
# POST 생성
from apps.community.posts.services.create import create_post


class PostsView(APIView):
    """
    GET  /posts  -> list_posts (view=main/community)
    POST /posts  -> create_post (JSON & multipart, 이미지 옵션)
    """
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_permissions(self):
        # GET은 공개, POST는 인증 필요
        return [IsAuthenticated()] if self.request.method == "POST" else [AllowAny()]

    # 뷰에 로직 작성 지양: 서비스 함수로 직접 바인딩
    get = list_posts
    post = create_post
