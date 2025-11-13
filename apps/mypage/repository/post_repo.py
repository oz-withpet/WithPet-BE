from django.db.models import QuerySet, Exists, OuterRef
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

# 다른 앱 모델 import
from apps.community.posts.models import Post
from apps.community.likes.models import Like
from apps.community.reports.models import Report

User = get_user_model()


class PostActivityRepository:

  def __init__(self):
    self.post_content_type = ContentType.objects.get_for_model(Post)

  def _get_posts_base_qs(self) -> QuerySet[Post]:
    """목록 조회 시 공통 쿼리셋 (N+1, 삭제 제외)"""
    return Post.objects.alive().select_related("category", "author")

  def _annotate_is_liked_by_me(self, qs: QuerySet[Post], user_id: int) -> QuerySet[Post]:
    """게시글 목록에 좋아요 여부 추가"""
    return qs.annotate(
      is_liked_by_me=Exists(
        Like.objects.filter(
          user_id=user_id,
          content_type=self.post_content_type,
          object_id=OuterRef("id"),
        )
      )
    )

  def get_my_written_posts(self, user_id: int) -> QuerySet[Post]:
    """내가 작성한 글 + 삭제 되지 않은 게시글"""
    qs = self._get_posts_base_qs()
    qs = qs.filter(author_id=user_id).order_by('-created_at', '-id')
    return self._annotate_is_liked_by_me(qs, user_id)

  # 💡 [좋아요 수정] Post ID 리스트를 이용해 필터링 (DB Query 오류 회피)
  def get_my_liked_posts(self, user_id: int) -> QuerySet[Post]:
    """내가 좋아요한 글 + 삭제되지 않은 게시글"""

    # 1. 좋아요(Like) 객체에서 Post ID 목록을 가져옵니다.
    post_ids_with_likes = Like.objects.filter(
      user_id=user_id,
      content_type=self.post_content_type
    ).values_list('object_id', flat=True).order_by('-created_at') # 좋아요 시점 정렬

    # 2. Post 객체를 ID 리스트를 이용해 필터링하고, 좋아요 상태를 annotate 합니다.
    qs = self._get_posts_base_qs()
    qs = qs.filter(id__in=post_ids_with_likes)

    # NOTE: 이 방식으로는 좋아요 시점 정렬(like__created_at)을 할 수 없습니다.
    # Post의 created_at으로 대신 정렬하여 쿼리 오류를 회피합니다.
    qs = qs.order_by('-created_at', '-id')

    return self._annotate_is_liked_by_me(qs, user_id)

  # 신고 내역은 그대로 유지합니다. (이미 성공했으므로)
  def get_my_reported_items(self, user_id: int) -> QuerySet[Report]:
    """내가 신고한 게시글 + 최신순 ( target 역참조 )"""

    return Report.objects.filter(
      user_id=user_id,
      content_type=self.post_content_type
    ).select_related('user').order_by('-created_at', '-id')