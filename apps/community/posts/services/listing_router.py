from rest_framework.exceptions import ValidationError

def list_posts(request):
    view = request.query_params.get("view", "community")
    if view == "main":
        from .listing_main import main_list
        return main_list(request)
    if view == "community":
        from .listing import community_list
        return community_list(request)
    raise ValidationError({"view": "허용된 값: main | community"})
