from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from ..models import Store
from ..serializers import (
    StoreSerializer,
    StoreListSerializer,
    StoreNearbySerializer
)
from ..services import StoreFilter, DistanceCalculator


class StoreListAPIView(APIView):
    def get(self, request):
        queryset = Store.objects.filter(is_active=True)

        filterset = StoreFilter(request.query_params, queryset=queryset)
        if not filterset.is_valid():
            return Response(
                {'detail': '잘못된 필터 파라미터입니다', 'errors': filterset.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = filterset.qs
        ordering = request.query_params.get('ordering', 'store_name')
        queryset = queryset.order_by(ordering)


        serializer = StoreListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

    def post(self, request):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not latitude or not longitude:
            return Response(
                {'detail': 'latitude와 longitude는 필수입니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_lat = float(latitude)
            user_lng = float(longitude)
        except (ValueError, TypeError):
            return Response(
                {'detail': '올바른 좌표 형식이 아닙니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        radius_km = float(request.data.get('radius', 5))
        filters = request.data.get('filters', {})
        queryset = Store.objects.filter(is_active=True)
        filterset = StoreFilter(filters, queryset=queryset)
        if not filterset.is_valid():
            return Response(
                {'detail': '잘못된 필터 파라미터입니다', 'errors': filterset.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = filterset.qs

        stores_with_distance = []
        for store in queryset:
            distance = DistanceCalculator.calculate_distance(
                user_lat,
                user_lng,
                float(store.latitude),
                float(store.longitude)
            )

            if distance <= radius_km:
                store.distance = distance
                stores_with_distance.append(store)

        stores_with_distance.sort(key=lambda x: x.distance)

        paginator = PageNumberPagination()
        paginator.page_size = int(request.data.get('page_size', 0))

        page = paginator.paginate_queryset(stores_with_distance, request)
        if page is not None:
            serializer = StoreNearbySerializer(page, many=True)
            response = paginator.get_paginated_response(serializer.data)
            #사용자현재위치
            response.data['user_location'] = {
                'latitude': user_lat,
                'longitude': user_lng
            }
            response.data['radius_km'] = radius_km
            response.data['filters_applied'] = filters if filters else None

            return response

        serializer = StoreNearbySerializer(stores_with_distance, many=True)
        return Response({
            'user_location': {
                'latitude': user_lat,
                'longitude': user_lng
            },
            'radius_km': radius_km,
            'filters_applied': filters if filters else None,
            'count': len(stores_with_distance),
            'results': serializer.data
        })


class StoreDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            store = Store.objects.get(pk=pk, is_active=True)
        except Store.DoesNotExist:
            return Response(
                {'detail': '매장을 찾을 수 없습니다'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StoreSerializer(store)
        return Response(serializer.data)

    def post(self, request, pk):
        try:
            store = Store.objects.get(pk=pk, is_active=True)
        except Store.DoesNotExist:
            return Response(
                {'detail': '매장을 찾을 수 없습니다'},
                status=status.HTTP_404_NOT_FOUND
            )

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not latitude or not longitude:
            return Response(
                {'detail': 'latitude와 longitude는 필수입니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_lat = float(latitude)
            user_lng = float(longitude)

            # 거리 계산
            distance = DistanceCalculator.calculate_distance(
                user_lat,
                user_lng,
                float(store.latitude),
                float(store.longitude)
            )
            store.distance = distance

            serializer = StoreNearbySerializer(store)
            data = serializer.data
            data['user_location'] = {
                'latitude': user_lat,
                'longitude': user_lng
            }
            return Response(data)

        except (ValueError, TypeError):
            return Response(
                {'detail': '올바른 좌표 형식이 아닙니다'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoryListAPIView(APIView):
    def get(self, request):
        categories = Store.objects.filter(
            is_active=True
        ).values(
            'category_code',
            'category_name'
        ).annotate(
            count=Count('id')
        ).order_by('category_name')

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