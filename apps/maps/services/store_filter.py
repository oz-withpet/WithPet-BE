from django.db.models import Q
from ..models import Store


class StoreFilterService:

    @staticmethod
    def filter_stores(province=None, district=None, neighborhood=None,
                      category=None, category_code=None, keyword=None):

        queryset = Store.objects.active_only()

        if province:
            queryset = queryset.filter(province=province)
        if district:
            queryset = queryset.filter(district=district)
        if neighborhood:
            queryset = queryset.filter(neighborhood=neighborhood)

        if category_code:
            queryset = queryset.filter(category_code=category_code)
        elif category:
            queryset = queryset.filter(category_name=category)

        if keyword:
            queryset = queryset.filter(
                Q(store_name__icontains=keyword) |
                Q(road_address__icontains=keyword)
            )

        return queryset.order_by('store_name')