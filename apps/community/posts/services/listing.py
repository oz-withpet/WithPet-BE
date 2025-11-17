# apps/community/posts/services/listing.py
from typing import Dict, Any
from django.db.models import Q, Exists, OuterRef
from django.core.paginator import Paginator, EmptyPage
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import hashlib

from apps.community.posts.models import Post
from apps.community.posts.serializers import PostListItemCommunityOut
from apps.community.likes.models import Like  # Generic FK 기반 좋아요 모델

from apps.community.common import (
    ALLOWED_SORT,
    ALLOWED_SEARCH_IN,
    CATEGORY_KOR_ALLOWED,
    normalize_category_input,
)

# 허용 카테고리 집합 (스펙과 일치)
ALLOWED_CATEGORIES = {"전체", *CATEGORY_KOR_ALLOWED}


def _parse_params(qp) -> Dict[str, Any]:
    v = qp.get("view")
    if v is not None and v != "community":
        raise ValidationError(detail={"code": "BAD_VIEW", "message": "view 파라미터는 community만 허용됩니다."})

    if "after" in qp or "limit" in qp:
        raise ValidationError(detail={"code": "BAD_COMBINATION", "message": "community view에서 after/limit는 허용되지 않습니다."})

    # 기본값/파싱
    try:
        page = int(qp.get("page", 1))
        page_size = int(qp.get("page_size", 20))
    except ValueError:
        raise ValidationError({"page/page_size": "정수여야 합니다."})

    category = qp.get("category")
    sort = qp.get("sort", "latest")
    q = qp.get("q")
    search_in = qp.get("search_in", "title_content")

    # 검증
    if page < 1:
        raise ValidationError({"page": "1 이상이어야 합니다."})
    if not (1 <= page_size <= 100):
        raise ValidationError({"page_size": "1~100 범위여야 합니다."})
    if category and category not in ALLOWED_CATEGORIES:
        raise ValidationError({"category": f"허용된 값: {sorted(ALLOWED_CATEGORIES)}"})
    if sort not in ALLOWED_SORT:
        raise ValidationError({"sort": f"허용된 값: {sorted(ALLOWED_SORT)}"})
    if search_in not in ALLOWED_SEARCH_IN:
        raise ValidationError({"search_in": f"허용된 값: {sorted(ALLOWED_SEARCH_IN)}"})

    return {
        "page": page,
        "page_size": page_size,
        "category": category,
        "sort": sort,
        "q": q,
        "search_in": search_in,
    }


def community_list(request):
    params = _parse_params(request.query_params)

    qs = (
        Post.objects
        .select_related("category")
        .prefetch_related("images")              # ✅ 다중 이미지 N+1 방지
        .filter(is_deleted=False)
    )

    # 카테고리: "전체"는 필터 미적용
    cat = normalize_category_input(params["category"])  # "전체" → None
    if cat:
        qs = qs.filter(category__name=cat)

    # 검색
    kw = params["q"]
    if kw:
        si = params["search_in"]
        if si == "title":
            qs = qs.filter(title__icontains=kw)
        elif si == "content":
            qs = qs.filter(content__icontains=kw)
        else:  # title_content
            qs = qs.filter(Q(title__icontains=kw) | Q(content__icontains=kw))

    # 정렬 안정성
    st = params["sort"]
    if st == "latest":
        qs = qs.order_by("-created_at", "-id")
    elif st == "views":
        qs = qs.order_by("-view_count", "-id")
    else:  # likes
        qs = qs.order_by("-like_count", "-id")

    # ✅ 로그인 사용자라면 is_liked_by_me 주입
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        ct_post = ContentType.objects.get_for_model(Post)
        qs = qs.annotate(
            is_liked_by_me=Exists(
                Like.objects.filter(
                    user_id=user.id,
                    content_type=ct_post,
                    object_id=OuterRef("id"),
                )
            )
        )

    # 페이지네이션
    paginator = Paginator(qs, params["page_size"])
    try:
        page_obj = paginator.page(params["page"])
    except EmptyPage:
        page_obj = []

    # 직렬화 (request context 넘겨서 절대 URL 생성 지원)
    ser = PostListItemCommunityOut(page_obj, many=True, context={"request": request})

    data = {
        "posts": ser.data,
        "page": params["page"],
        "page_size": params["page_size"],
        "total": paginator.count if hasattr(paginator, "count") else 0,
    }

    # ETag 생성 (캐시)
    last_updated = None
    if page_obj:
        items = list(page_obj)
        last_updated = getattr(items[-1], "updated_at", None)

    etag_src = (
        f"community:{params['page']}:{params['page_size']}:{params['category']}:"
        f"{params['sort']}:{params['q']}:{last_updated and last_updated.isoformat()}"
    )
    etag = f'W/"{hashlib.md5(etag_src.encode()).hexdigest()}"'

    if request.META.get("HTTP_IF_NONE_MATCH") == etag:
        return Response(status=status.HTTP_304_NOT_MODIFIED)

    resp = Response(data, status=status.HTTP_200_OK)
    resp["ETag"] = etag
    resp["Cache-Control"] = "public, max-age=30"
    return resp
