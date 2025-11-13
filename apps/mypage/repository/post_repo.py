from django.db.models import QuerySet, Exists, OuterRef
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from apps.community.posts.models import Post
from apps.community.likes.models import Like
from apps.community.reports.models import Report

class PostActivityRepository:

  def __init__(self):
    self.post_content_type = ContentType.objects.get_for_model(Post)

  def _get_posts_base_qs(self, user_id: int) -> QuerySet[Post]:
    # 목록 조회 시 n+1, 삭제 제외
    return Post.objects.alive().select_related("category", "author")

  def _annotate_is_liked_by_me(self, qs: QuerySet[Post], user_id: int) -> QuerySet[Post]:
    # 게시글 목록에 좋아요 여부 추가
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
    # 내가 작성한 글 + 삭제 되지 않은 게시글
    qs = self._get_posts_base_qs(user_id)
    qs = qs.filter(author_id=user_id).order_by('-created_at', '-id')
    return self._annotate_is_liked_by_me(qs, user_id)

  def get_my_liked_posts(self, user_id: int) -> QuerySet[Post]:
    # 내가 좋아요한 글 + 삭제되지 않은 게시글
    qs = self._get_posts_base_qs(user_id)

    qs = qs.filter(
      like__user_id=user_id,
      like__content_type=self.post_content_type
    ).order_by('-like__created_at', '-id').distinct()

    return qs

  def get_my_reported_items(self, user_id: int) -> QuerySet[Report]:
    # 내가 신고한 게시글 + 최신순 ( target 역참조 )
    return Report.objects.select_related('target', 'target__category', 'user').filter(
      user_id=user_id,
      content_type=self.post_content_type
    ).order_by('-created_at', '-id')