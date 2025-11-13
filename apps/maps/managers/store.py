from django.db import models
from django.db.models import Q


class StoreManager(models.Manager):
    def active_only(self):
        return self.get_queryset().filter(is_active=True)

    def filter_by_location(self, province=None, district=None, neighborhood=None):
        queryset = self.active_only()

        if province:
            queryset = queryset.filter(province=province)
        if district:
            queryset = queryset.filter(district=district)
        if neighborhood:
            queryset = queryset.filter(neighborhood=neighborhood)

        return queryset

    def filter_by_category(self, category=None):
        queryset = self.active_only()

        if category:
            queryset = queryset.filter(
                Q(category_code=category) |
                Q(category_name=category)
            )

        return queryset

    def search(self, keyword=None):
        queryset = self.active_only()

        if keyword:
            queryset = queryset.filter(
                Q(store_name__icontains=keyword) |
                Q(road_address__icontains=keyword)
            )

        return queryset