from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.maps.models import Store
from apps.maps.serializers import StoreSerializer


class StoreDetailAPIView(APIView):
    """
    가게 상세 조회 API
    GET /api/stores/{id}/
    """

    def get(self, request, pk):
        """가게 상세 정보 조회"""
        try:
            store = Store.objects.get(pk=pk)
            serializer = StoreSerializer(store)

            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Store.DoesNotExist:
            return Response({
                'success': False,
                'error': '가게를 찾을 수 없습니다'
            }, status=status.HTTP_404_NOT_FOUND)