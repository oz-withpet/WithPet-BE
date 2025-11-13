from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.maps.serializers import StoreSerializer
from apps.maps.services import StoreFilterService

#매장목록조회
class StoreListAPIView(APIView):
    def get(self, request):
        province = request.query_params.get('province')
        district = request.query_params.get('district')
        neighborhood = request.query_params.get('neighborhood')
        category = request.query_params.get('category')
        keyword = request.query_params.get('keyword')

        try:
            stores = StoreFilterService.filter_stores(
                province=province,
                district=district,
                neighborhood=neighborhood,
                category=category,
                keyword=keyword
            )

            serializer = StoreSerializer(stores, many=True)

            return Response({
                'success': True,
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)