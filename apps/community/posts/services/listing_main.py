# apps/community/posts/services/listing_main.py
from __future__ import annotations
from typing import Dict, Any, Tuple
import base64
from django.db.models import Q
from datetime import datetime, timezone as dt_timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.community.posts.models import Post
from apps.community.posts.serializers import PostListItemMainOut

# main 뷰에서 금지되는 파라미터
FORBIDDEN_ON_MAIN = {"page", "page_size", "category", "sort", "q", "search_in"}


# --- 커서 토큰: (epoch_ms, id) → urlsafe base64 ---
def _encode_cursor(dt, pk: int) -> str:
    ts_ms = int(dt.timestamp() * 1000)
    raw = f"{ts_ms}:{int(pk)}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

def _decode_cursor(token: str) -> Tuple[int, int]:
    try:
        pad = "=" * ((4 - len(token) % 4) % 4)
        raw = base64.urlsafe_b64decode((token + pad).encode("ascii")).decode("utf-8")
        ts_ms_str, id_str = raw.split(":", 1)
        return int(ts_ms_str), int(id_str)
    except Exception:
        raise ValidationError(detail={"code": "BAD_CURSOR", "message": "유효하지 않은 after 커서입니다."})


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


def main_list(request):
    params = _parse_params(request.query_params)

    # 안정 정렬: 최신순 우선(-created_at, -id)
    qs = (
        Post.objects
        .select_related("category")
        .filter(is_deleted=False)
        .order_by("-created_at", "-id")
    )

    # after 커서 적용: (created_at DESC, id DESC)의 다음 배치
    after = params["after"]
    if after:
        ts_ms, last_id = _decode_cursor(after)
        ts = datetime.fromtimestamp(ts_ms / 1000.0, tz=dt_timezone.utc)
        qs = qs.filter(Q(created_at__lt=ts) | Q(created_at=ts, id__lt=last_id))

    # limit+1로 has_next 판별
    rows = list(qs[: params["limit"] + 1])
    has_next = len(rows) > params["limit"]
    page = rows[: params["limit"]]

    next_after = _encode_cursor(page[-1].created_at, page[-1].id) if has_next else None

    ser = PostListItemMainOut(page, many=True, context={"request": request})
    data = {"posts": ser.data, "has_next": has_next, "next_after": next_after}
    return Response(data, status=status.HTTP_200_OK)
