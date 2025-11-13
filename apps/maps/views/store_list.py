from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import StoreSerializer
from ..services import StoreFilterService
from ..utils.locations_mapper import to_korean_province, to_korean_district


class StoreListAPIView(APIView):
    def get(self, request):
        search = request.query_params.get('search')
        province_eng = request.query_params.get('province')
        district_eng = request.query_params.get('district')
        neighborhood = request.query_params.get('neighborhood')
        category = request.query_params.get('category')
        category_code = request.query_params.get('category_code')

        province = to_korean_province(province_eng) if province_eng else None
        district = to_korean_district(district_eng) if district_eng else None

        try:
            stores = StoreFilterService.filter_stores(
                province=province,
                district=district,
                neighborhood=neighborhood,
                category=category,
                category_code=category_code,
                keyword=search
            )

            serializer = StoreSerializer(stores, many=True)

            return Response({
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)