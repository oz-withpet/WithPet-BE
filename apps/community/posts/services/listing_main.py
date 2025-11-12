# apps/community/posts/services/listing_main.py
from __future__ import annotations

from typing import Dict, Any, Tuple, Optional, Sequence, List
import base64
import binascii
import hashlib
from datetime import datetime, timezone as dt_timezone

from django.db import models
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.community.posts.models import Post
from apps.community.posts.serializers import PostListItemMainOut

# main 뷰에서 금지되는 파라미터
FORBIDDEN_ON_MAIN = {"page", "page_size", "category", "sort", "q", "search_in"}


# ---------- 커서/시간 유틸 ----------
def _safe_ms_from_dt(dt: datetime) -> int:
    """datetime → epoch milliseconds (예외 시 0)."""
    try:
        return int(dt.timestamp() * 1000)
    except (AttributeError, OSError, OverflowError, ValueError, TypeError):
        return 0


def _encode_cursor(dt: datetime, pk: int) -> str:
    ms = _safe_ms_from_dt(dt)
    raw = f"{ms}:{int(pk)}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_cursor(token: str) -> Tuple[int, int]:
    """urlsafe base64 → (epoch_ms, id)"""
    try:
        pad = "=" * ((4 - len(token) % 4) % 4)
        raw = base64.urlsafe_b64decode((token + pad).encode("ascii")).decode("utf-8")
        ms_str, id_str = raw.split(":", 1)
        return int(ms_str), int(id_str)
    except (ValueError, TypeError, binascii.Error):
        raise ValidationError(detail={"code": "BAD_CURSOR", "message": "유효하지 않은 after 커서입니다."})


def _key_for_etag(obj: Optional[Post]) -> str:
    """ETag 키(created_at_ms:id). 없으면 빈 문자열."""
    if not obj:
        return ""
    return f"{_safe_ms_from_dt(obj.created_at)}:{obj.id}"


def _slice_with_has_next(items: Sequence[Post], limit: int) -> Tuple[List[Post], bool]:
    """limit+1 규칙으로 page/has_next 계산."""
    has_next = len(items) > limit
    return list(items[:limit]), has_next


def _make_etag_main(limit: int, after_token: Optional[str], page: Sequence[Post]) -> str:
    first_key = _key_for_etag(page[0] if page else None)
    last_key = _key_for_etag(page[-1] if page else None)
    etag_src = f"main:{limit}:{after_token or ''}:{first_key}:{last_key}"
    return f'W/"{hashlib.md5(etag_src.encode()).hexdigest()}"'


# ---------- 파라미터 파싱 ----------
def _parse_params(qp) -> Dict[str, Any]:
    v = qp.get("view")
    if v is not None and v != "main":
        raise ValidationError(detail={"code": "BAD_VIEW", "message": "view=main만 허용됩니다."})

    bad = sorted(set(qp.keys()) & FORBIDDEN_ON_MAIN)
    if bad:
        raise ValidationError(detail={"code": "BAD_COMBINATION", "message": f"main view에서는 {bad} 파라미터를 허용하지 않습니다."})

    try:
        limit = int(qp.get("limit", 12))  # 기본 12, 범위 1~50
    except ValueError:
        raise ValidationError({"limit": "정수여야 합니다."})
    if not (1 <= limit <= 50):
        raise ValidationError({"limit": "1~50 범위여야 합니다."})

    after = qp.get("after")
    return {"limit": limit, "after": after}


# ---------- 메인 리스트 ----------
def main_list(request):
    params = _parse_params(request.query_params)

    # 안정 정렬: 최신순 우선(-created_at, -id)
    qs: models.QuerySet = (
        Post.objects
        .select_related("category")
        .filter(is_deleted=False)
        .order_by("-created_at", "-id")
    )

    # after 커서 적용: (created_at DESC, id DESC)의 다음 배치
    after_token = params["after"]
    if after_token:
        cursor_ms, cursor_last_id = _decode_cursor(after_token)
        cursor_dt = datetime.fromtimestamp(cursor_ms / 1000.0, tz=dt_timezone.utc)
        qs = qs.filter(Q(created_at__lt=cursor_dt) | Q(created_at=cursor_dt, id__lt=cursor_last_id))

    # limit+1로 has_next 판별
    limit = params["limit"]
    rows = list(qs[: limit + 1])
    page, has_next = _slice_with_has_next(rows, limit)

    next_after: Optional[str] = None
    if has_next and page:
        tail = page[-1]
        next_after = _encode_cursor(tail.created_at, tail.id)

    ser = PostListItemMainOut(page, many=True, context={"request": request})
    data = {"posts": ser.data, "has_next": has_next, "next_after": next_after}

    # ===== ETag / Cache-Control =====
    etag_val = _make_etag_main(limit, after_token, page)

    # 조건부 요청 처리
    if request.META.get("HTTP_IF_NONE_MATCH") == etag_val:
        return Response(status=status.HTTP_304_NOT_MODIFIED)

    resp = Response(data, status=status.HTTP_200_OK)
    resp["ETag"] = etag_val
    resp["Cache-Control"] = "public, max-age=30"
    return resp
