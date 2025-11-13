from django.db.models import Q
from apps.maps.models import Store


class StoreFilterService:
    @staticmethod
    def filter_stores(province=None, district=None, neighborhood=None,
                      category=None, keyword=None):
        queryset = Store.objects.all()
        if any([province, district, neighborhood]):
            queryset = Store.objects.filter_location(
                province=province,
                district=district,
                neighborhood=neighborhood
            )

        if category:
            queryset = queryset.filter(category__name=category)

        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) |
                Q(full_address__icontains=keyword)
            )

        return queryset.order_by('name')