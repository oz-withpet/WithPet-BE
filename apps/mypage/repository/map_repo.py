from django.db.models import QuerySet
from apps.maps.models.store import LikePlace


class MapActivityRepository:
    def get_my_liked_stores(self, user_id: int) -> QuerySet[LikePlace]:
        # 관심 장소 목록 조회
        return LikePlace.objects.select_related('store').filter(user_id=user_id).order_by('-created_at', '-id')