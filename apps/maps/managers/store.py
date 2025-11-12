from django.db import models
from django.db.models import Q

class StoreManager(models.Manager):
    def filter_location(self, province=None, district=None, neighborhood=None):
        queryset = self.get_queryset()
        if province:
            queryset = queryset.filter(province=province)
        if district:
            queryset = queryset.filter(district=district)
        if neighborhood:
            queryset = queryset.filter(neighborhood=neighborhood)
        return queryset

    def filter_category(self, category_name=None):
        queryset = self.get_queryset()
        if category_name:
            queryset = queryset.filter(category__name=category_name)
        return queryset

    def filter_keyword(self, keyword=None):
        queryset = self.get_queryset()
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) |
                Q(full_address__icontains=keyword)
            )
        return queryset