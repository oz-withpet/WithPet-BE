from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Store
from django.db.models import Count
from ..utils.locations_mapper import to_english_province


class ProvinceListAPIView(APIView):
    def get(self, request):
        try:
            provinces = Store.objects.filter(
                is_active=True
            ).values(
                'province'
            ).annotate(
                store_count=Count('id')
            ).order_by('province')

            data = [
                {
                    'name': p['province'],
                    'name_en': to_english_province(p['province']),
                    'store_count': p['store_count']
                }
                for p in provinces
            ]

            return Response({
                'count': len(data),
                'data': data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)