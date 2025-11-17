# apps/community/posts/services/update.py
from __future__ import annotations

from typing import Optional, List

from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
    UnsupportedMediaType,
)

from apps.community.common import id_from_path_param, CATEGORY_KOR_ALLOWED
from apps.community.posts.models import Post, PostCategory, PostImage

MAX_IMAGES = 5


def _alive_qs():
    try:
        return Post.objects.alive()
    except AttributeError:
        return Post.objects.filter(is_deleted=False)


def _parse_bool(val: object) -> Optional[bool]:
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        s = val.strip().lower()
        if s in {"true", "1", "yes", "y"}:
            return True
        if s in {"false", "0", "no", "n"}:
            return False
    raise ValidationError({"image_delete": "boolean 형식이어야 합니다."})


def _parse_ids(raw: object) -> List[int]:
    """
    image_ids_delete가 배열(list) 또는 콤마구분 문자열("1,2,3")로 올 수 있음.
    없거나 빈값이면 [] 반환.
    """
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        out = []
        for v in raw:
            try:
                out.append(int(v))
            except (TypeError, ValueError):
                raise ValidationError({"image_ids_delete": "정수 배열이어야 합니다."})
        return out
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []
        try:
            return [int(x) for x in s.split(",") if x.strip() != ""]
        except ValueError:
            raise ValidationError({"image_ids_delete": "정수 목록 형식이 올바르지 않습니다."})
    raise ValidationError({"image_ids_delete": "list 또는 콤마구분 문자열이어야 합니다."})


def _ensure_author_or_403(request_user, post: Post) -> None:
    if not getattr(request_user, "is_authenticated", False):
        raise PermissionDenied("로그인이 필요합니다.")
    if post.author_id != request_user.id:
        raise PermissionDenied("본인 글만 수정할 수 있습니다.")


def _apply_category_if_provided(
    post: Post, cat_raw: object, include_category_field: bool
) -> bool:

    if not include_category_field:
        return False

    if cat_raw is None or (isinstance(cat_raw, str) and cat_raw.strip() == ""):
        if post.category_id is not None:
            post.category = None
            return True
        return False

    if not isinstance(cat_raw, str):
        raise ValidationError({"category": "카테고리는 문자열이어야 합니다."})

    cat = cat_raw.strip()
    if cat not in CATEGORY_KOR_ALLOWED:
        raise ValidationError({"category": f"허용되지 않는 카테고리입니다. {CATEGORY_KOR_ALLOWED} 중 선택하세요."})

    try:
        pc = PostCategory.objects.get(name=cat)
    except PostCategory.DoesNotExist:
        raise ValidationError({"category": "존재하지 않는 카테고리입니다. (사전 등록 필요)"})

    if post.category_id != pc.id:
        post.category = pc
        return True
    return False


def _ensure_lengths_if_provided(title: Optional[str], content: Optional[str]) -> None:
    if title is not None:
        if not isinstance(title, str):
            raise ValidationError({"title": "문자열이어야 합니다."})
        t = title.strip()
        if len(t) < 1 or len(t) > 100:
            raise ValidationError({"title": "길이는 1~100자여야 합니다."})

    if content is not None:
        if not isinstance(content, str):
            raise ValidationError({"content": "문자열이어야 합니다."})
        c = content.strip()
        if len(c) < 1 or len(c) > 20000:
            raise ValidationError({"content": "길이는 1~20000자여야 합니다."})


def _count_images(post: Post) -> int:
    """
    현재 보유 중인 전체 이미지 수(legacy 단일 + PostImage).
    """
    legacy = 1 if getattr(post, "image", None) else 0
    extra = PostImage.objects.filter(post=post).count()
    return legacy + extra


def _validate_total_after_change(current_total: int, add_count: int) -> None:
    total = current_total + add_count
    if total > MAX_IMAGES:
        raise ValidationError({"images": f"이미지는 최대 {MAX_IMAGES}장까지 업로드할 수 있습니다."})


@transaction.atomic
def patch_post(request, post_id: str) -> Response:
    # ------ 대상 조회 & 권한 ------
    pk = id_from_path_param(post_id)

    try:
        post = _alive_qs().select_related("author", "category").get(pk=pk)
    except Post.DoesNotExist:
        raise NotFound("게시글을 찾을 수 없습니다.")

    _ensure_author_or_403(request.user, post)

    # ------ 입력 파싱 ------
    is_multipart = (request.content_type or "").lower().startswith("multipart/")
    data = request.data
    included_keys = set(data.keys())

    # 단일 image는 multipart가 아니면 거부
    if not is_multipart and "image" in included_keys:
        raise UnsupportedMediaType(media_type=request.content_type or "application/json")

    # 다중 images[]는 multipart에서만 파일로 옴
    files_new = request.FILES.getlist("images") if is_multipart else []

    title = data.get("title", None)
    content = data.get("content", None)
    category_raw = data.get("category", None)
    image_delete_raw = data.get("image_delete", None)  # 전체 삭제 플래그
    image_file = request.FILES.get("image") if is_multipart else None  # 단일 교체(하위호환)

    # 부분 삭제용 ids (JSON에서도 허용)
    ids_to_delete = _parse_ids(data.get("image_ids_delete"))

    _ensure_lengths_if_provided(title, content)

    dirty = False

    # ------ 텍스트/카테고리 필드 ------
    if title is not None:
        t = title.strip()
        if post.title != t:
            post.title = t
            dirty = True

    if content is not None:
        c = content.strip()
        if post.content != c:
            post.content = c
            dirty = True

    if _apply_category_if_provided(post, category_raw, include_category_field=("category" in included_keys)):
        dirty = True

    # ------ 이미지 삭제/교체/추가 ------
    # 현재 총 장수
    current_total = _count_images(post)

    # 1) 전체 삭제(image_delete=true)
    if image_delete_raw is not None and _parse_bool(image_delete_raw):
        # legacy 제거
        if post.image:
            post.image.delete(save=False)
            post.image = None
            dirty = True
        # PostImage 전체 제거
        qs_all = PostImage.objects.filter(post=post)
        if qs_all.exists():
            for pi in qs_all:
                if pi.image:
                    pi.image.delete(save=False)
            qs_all.delete()
            # current_total 재계산
            current_total = 0

    # 2) 부분 삭제(image_ids_delete)
    if ids_to_delete:
        qs_del = PostImage.objects.filter(post=post, id__in=ids_to_delete)
        if qs_del.exists():
            for pi in qs_del:
                if pi.image:
                    pi.image.delete(save=False)
            deleted, _ = qs_del.delete()
            if deleted:
                current_total = _count_images(post)  # 다시 계산

    # 3) 단일 이미지 교체(legacy)
    if image_file is not None:
        # 기존 파일 있으면 실제 파일도 정리
        if post.image:
            post.image.delete(save=False)
        post.image = image_file
        dirty = True
        # 교체는 총 장수 변화 없음(없던 곳에 넣으면 +1)
        current_total = _count_images(post)

    # 4) 다중 이미지 추가(images[])
    if files_new:
        _validate_total_after_change(current_total, len(files_new))
        objs = []
        # 기본 order는 끝에 이어 붙이도록 현재 최대 order 조회
        max_order = (
            PostImage.objects.filter(post=post).order_by("-order").values_list("order", flat=True).first() or -1
        )
        start = max_order + 1
        for idx, f in enumerate(files_new):
            objs.append(PostImage(post=post, image=f, order=start + idx))
        PostImage.objects.bulk_create(objs, batch_size=50)
        # 총 장수 갱신
        current_total = _count_images(post)

    # ------ 저장 & 응답 ------
    if dirty:
        post.save()

    return Response(
        {
            "post_id": post.public_id,  # base64 공개 ID (A안 적용 전제: path는 숫자, 응답은 base64 유지 가능)
            "updated_at": post.updated_at.isoformat().replace("+00:00", "Z"),
        },
        status=status.HTTP_200_OK,
    )
