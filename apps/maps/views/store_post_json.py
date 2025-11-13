from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import StoreSerializer
from ..services.store_filter import StoreFilterService
from ..utils.locations_mapper import to_korean_province, to_korean_district


class StoreSearchAPIView(APIView):
    def post(self, request):
        search = request.data.get('keyword') or request.data.get('search')
        province_eng = request.data.get('province')
        district_eng = request.data.get('district')
        neighborhood = request.data.get('neighborhood')
        category = request.data.get('category')
        category_code = request.data.get('category_code')

        page = request.data.get('page', 1)
        size = request.data.get('size', 20)

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

            total = stores.count()
            start = (page - 1) * size
            end = start + size
            paginated_stores = stores[start:end]

            serializer = StoreSerializer(paginated_stores, many=True)

            return Response({
                'success': True,
                'page': page,
                'size': size,
                'total': total,
                'total_pages': (total + size - 1) // size,
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)