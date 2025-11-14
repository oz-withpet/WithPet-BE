from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Store
from ..serializers import StoreSerializer, StoreListSerializer
from ..services import StoreFilter


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.filter(is_active=True)
    serializer_class = StoreSerializer
    filterset_class = StoreFilter

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['store_name', 'road_address']
    ordering_fields = ['store_name', 'rating', 'created_at']
    ordering = ['store_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return StoreListSerializer
        return StoreSerializer

#/api/stores/categories/
    @action(detail=False, methods=['get'])
    def categories(self, request):
        from django.db.models import Count

        categories = Store.objects.filter(
            is_active=True
        ).values(
            'category_code',
            'category_name'
        ).annotate(
            count=Count('id')
        ).order_by('category_name')
        #중복 제거
        seen_codes = set()
        unique_categories = []

        for cat in categories:
            if cat['category_code'] not in seen_codes:
                seen_codes.add(cat['category_code'])
                unique_categories.append({
                    'code': cat['category_code'],
                    'name': cat['category_name'],
                    'count': cat['count']
                })

        return Response(unique_categories)