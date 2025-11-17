from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from ..models import Store
from ..services.location_filter import LocationService



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


class LocationProvinceAPIView(APIView):
    def get(self, request):
        provinces = LocationService.get_provinces()
        return Response(provinces)


class LocationDistrictAPIView(APIView):
    def get(self, request, province_code):
        try:
            province_code = int(province_code)
        except ValueError:
            return Response(
                {'detail': '올바른 province_code 형식이 아닙니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        province = LocationService.get_province_by_code(province_code)
        if not province:
            return Response(
                {'detail': '해당 시/도를 찾을 수 없습니다'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 구/군 목록
        districts = LocationService.get_districts(province_code)
        return Response(districts)


class LocationNeighborhoodAPIView(APIView):
    def get(self, request, province_code, district_code):
        try:
            province_code = int(province_code)
            district_code = int(district_code)
        except ValueError:
            return Response(
                {'detail': '올바른 코드 형식이 아닙니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        district = LocationService.get_district_by_code(district_code)
        if not district or district['province_code'] != province_code:
            return Response(
                {'detail': '해당 구/군을 찾을 수 없습니다'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 동/읍/면 목록
        neighborhoods = LocationService.get_neighborhoods(
            province_code=province_code,
            district_code=district_code
        )
        return Response(neighborhoods)