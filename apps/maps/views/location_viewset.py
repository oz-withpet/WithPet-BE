from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from ..models import Store


class ProvinceListAPIView(APIView):
#GET /api/provinces/
    def get(self, request):
        provinces = Store.objects.filter(
            is_active=True
        ).values(
            'province'
        ).annotate(
            count=Count('id')
        ).order_by('province')

        return Response([
            {
                'name': p['province'],
                'count': p['count']
            }
            for p in provinces
        ])


class DistrictListAPIView(APIView):
#GET /api/provinces/{province_name}/districts/
    def get(self, request, province_name):
        districts = Store.objects.filter(
            is_active=True,
            province=province_name
        ).values(
            'district'
        ).annotate(
            count=Count('id')
        ).order_by('district')

        return Response([
            {
                'name': d['district'],
                'count': d['count']
            }
            for d in districts
        ])