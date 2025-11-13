from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from ..models.store import Store
from ..utils.locations_mapper import to_korean_province, to_english_district


class DistrictListAPIView(APIView):
    def get(self, request, province):
        try:
            # 영문 → 한글 변환
            province_kor = to_korean_province(province)

            # 해당 시/도의 구/군 목록
            districts = Store.objects.filter(
                province=province_kor,
                is_active=True
            ).values(
                'district'
            ).annotate(
                store_count=Count('id')
            ).order_by('district')

            # 영문명 추가
            data = [
                {
                    'name': d['district'],
                    'name_en': to_english_district(d['district']),
                    'store_count': d['store_count']
                }
                for d in districts
            ]

            return Response({
                'province': province_kor,
                'province_en': province,
                'count': len(data),
                'data': data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)