from rest_framework.views import APIView
from apps.community.posts.services.listing import community_list as _community_list

class PostsListView(APIView):
    # GET /posts  (view 기본 community)
    get = _community_list