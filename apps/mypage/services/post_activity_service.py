from typing import Dict, Any, Optional
from django.db.models import QuerySet, Q
from django.core.paginator import Paginator, EmptyPage
from rest_framework.exceptions import ValidationError
from apps.community.reports.models import Report
from apps.community.common.reports import reason_code_to_label

# 커서 방식 util 재사용 (protected 멤버 접근 경고 무시 가능)
from apps.community.posts.services.listing_main import (
    _encode_cursor,  # noqa
    _decode_cursor,  # noqa
    _slice_with_has_next,  # noqa
)

# Repository를 명확하게 import합니다.
from apps.mypage.repository.post_repo import PostActivityRepository


class PostActivityService:
    def __init__(self, repo: PostActivityRepository):
        self.repo = repo

    def _apply_pagination(
        self,
        qs: QuerySet,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        페이지네이션 (Page/Page_Size) 또는 커서 기반 (After/Limit)을 적용하고
        metadata 포함된 dict 형태로 결과 반환.
        """
        # 기본값
        page_size = params.get("page_size") or params.get("limit") or 20
        try:
            page_size = int(page_size)
        except (TypeError, ValueError):
            page_size = 20

        # --- 커서 기반 처리 ---
        if params.get('after') or params.get('limit'):
            limit = params.get('limit', page_size)
            try:
                limit = int(limit)
            except (TypeError, ValueError):
                limit = page_size

            after_token = params.get('after')
            if after_token:
                try:
                    cursor_ms, cursor_last_id = _decode_cursor(after_token)  # noqa
                    from datetime import datetime, timezone as dt_timezone
                    cursor_dt = datetime.fromtimestamp(cursor_ms / 1000.0, tz=dt_timezone.utc)

                    qs = qs.filter(
                        Q(created_at__lt=cursor_dt) |
                        Q(created_at=cursor_dt, id__lt=cursor_last_id)
                    )
                except Exception as e:
                    raise ValidationError({"after": f"유효하지 않은 after 커서입니다: {e}"})

            # limit + 1 로 가져와서 다음 여부 판단
            rows = list(qs[: limit + 1])
            page_items, has_next = _slice_with_has_next(rows, limit)  # noqa

            next_after: Optional[str] = None
            if has_next and page_items:
                tail = page_items[-1]
                next_after = _encode_cursor(tail.created_at, tail.id)  # noqa

            total = qs.count()
            return {
                "items": page_items,
                "page": params.get('page', 1),
                "page_size": limit,
                "total": total,
                "has_next": has_next,
                "next_after": next_after,
            }

        # --- 페이지번호 기반 처리 ---
        page_num = params.get("page", 1)
        try:
            page_num = int(page_num)
        except (TypeError, ValueError):
            page_num = 1

        paginator = Paginator(qs, page_size)
        try:
            page_obj = paginator.page(page_num)
        except EmptyPage:
            # 빈 페이지 반환: items 빈 리스트
            page_obj = []

        # 페이지 객체 has_next 처리 안전하게
        has_next = False
        if hasattr(page_obj, "has_next"):
            try:
                has_next = page_obj.has_next()
            except Exception:
                has_next = False

        return {
            "items": list(page_obj),
            "page": page_num,
            "page_size": page_size,
            "total": getattr(paginator, "count", 0),
            "has_next": has_next,
        }

    # --- 서비스 메서드들 ---
    def get_my_posts_list(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """내가 작성한 게시글 목록 조회 및 페이징."""
        qs = self.repo.get_my_written_posts(user_id)
        return self._apply_pagination(qs, params)

    def get_my_liked_posts_list(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """내가 좋아요한 게시글 목록 조회 및 페이징."""
        qs = self.repo.get_my_liked_posts(user_id)
        return self._apply_pagination(qs, params)

    def get_my_reported_list(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """내가 신고한 게시글(Report 객체) 목록 조회 및 페이징."""
        qs: QuerySet[Report] = self.repo.get_my_reported_items(user_id)
        result = self._apply_pagination(qs, params)

        # Report 객체 → Serializer 처리용으로 reason_label 추가
        for report in result["items"]:
            # report.reason 은 코드이므로 레이블로 변환
            report.reason_label = reason_code_to_label(report.reason)
        return result