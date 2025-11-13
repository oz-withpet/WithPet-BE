from typing import Dict, Any, Optional
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from rest_framework.exceptions import ValidationError
from datetime import datetime, timezone as dt_timezone

from apps.community.posts.services.listing_main import (
    _encode_cursor,  # noqa
    _decode_cursor,  # noqa
    _slice_with_has_next,  # noqa
)

from apps.mypage.repository.map_repo import MapActivityRepository


class MapActivityService:
    def __init__(self, repo: MapActivityRepository):
        self.repo = repo

    def get_my_liked_stores_list(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        # 관심 장소 조회
        qs = self.repo.get_my_liked_stores(user_id)
        page_size = params.get("page_size") or params.get("limit") or 20

        # 커서 기반 처리
        if params.get('after') or params.get('limit'):
            limit = int(params.get('limit', 20))
            after_token = params.get('after')

            if after_token:
                try:
                    cursor_ms, cursor_last_id = _decode_cursor(after_token)  # noqa
                    cursor_dt = datetime.fromtimestamp(cursor_ms / 1000.0, tz=dt_timezone.utc)
                    qs = qs.filter(
                        Q(created_at__lt=cursor_dt) |
                        Q(created_at=cursor_dt, id__lt=cursor_last_id)
                    )
                except Exception as e:
                    raise ValidationError({"after": f"유효하지 않은 커서입니다: {e}"})

            rows = list(qs[: limit + 1])
            page_items, has_next = _slice_with_has_next(rows, limit)  # noqa

            next_after: Optional[str] = None
            if has_next and page_items:
                tail = page_items[-1]
                next_after = _encode_cursor(tail.created_at, tail.id)  # noqa

            return {
                "items": page_items,
                "page": params.get('page', 1),
                "page_size": limit,
                "total": qs.count(),
                "has_next": has_next,
                "next_after": next_after,
            }

        # 페이지 네이션
        page_num = int(params.get("page", 1))
        paginator = Paginator(qs, page_size)
        try:
            page_obj = paginator.page(page_num)
        except EmptyPage:
            page_obj = []

        return {
            "items": list(page_obj),
            "page": page_num,
            "page_size": page_size,
            "total": paginator.count,
            "has_next": page_obj.has_next() if hasattr(page_obj, "has_next") else False,
        }
