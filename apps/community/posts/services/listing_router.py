from rest_framework.exceptions import ValidationError

def list_posts(request):
    view = request.query_params.get("view", "community")
    if view == "main":
        # 지연 임포트로 순환 참조 방지
        from .listing_main import main_list
        return main_list(request)
    elif view == "community":
        from .listing import community_list
        return community_list(request)
    else:
        raise ValidationError({"view": "허용된 값: main | community"})
