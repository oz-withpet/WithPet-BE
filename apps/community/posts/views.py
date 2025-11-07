from rest_framework.views import APIView
from apps.community.posts.services.listing import community_list

class PostsListView(APIView):
    # GET /posts  (view 기본 community)
    def get(self, request, *args, **kwargs):
        return community_list(request)