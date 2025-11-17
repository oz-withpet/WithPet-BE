import django_filters
from django.db import models
from ..models import Store


class StoreFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category_code')
    category_name = django_filters.CharFilter(field_name='category_name', lookup_expr='icontains')
    province = django_filters.CharFilter(lookup_expr='exact')
    district = django_filters.CharFilter(lookup_expr='exact')
    neighborhood = django_filters.CharFilter(lookup_expr='exact')
    province_code = django_filters.NumberFilter(field_name='province_code')
    district_code = django_filters.NumberFilter(field_name='district_code')
    neighborhood_code = django_filters.NumberFilter(field_name='neighborhood_code')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Store
        fields = [
            'category',
            'province',
            'district',
            'neighborhood',
            'province_code',
            'district_code',
            'neighborhood_code'
        ]

    def filter_search(self, queryset, name, value):

        return queryset.filter(
            models.Q(store_name__icontains=value) |
            models.Q(road_address__icontains=value)
        )