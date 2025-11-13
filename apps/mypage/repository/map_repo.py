
from django.db.models import QuerySet
from apps.maps.models.store_interest import StoreInterest


class MapActivityRepository:
    def get_my_liked_stores(self, user_id: int) -> QuerySet[StoreInterest]:
        # 나의 관심 장소 + select_related
        return StoreInterest.objects.select_related('store__category').filter(user_id=user_id).order_by('-created_at', '-id')