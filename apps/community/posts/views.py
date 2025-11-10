from rest_framework.views import APIView
from apps.community.posts.services.listing import community_list
from apps.community.posts.services.listing_main import main_list

class PostsListView(APIView):
    def get(self, request, *args, **kwargs):
        return main_list(request) if request.query_params.get("view") == "main" else community_list(request)
