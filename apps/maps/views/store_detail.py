from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Store
from ..serializers import StoreSerializer


class StoreDetailAPIView(APIView):
    def get(self, request, store_id):
        try:
            store = Store.objects.get(pk=store_id, is_active=True)
            serializer = StoreSerializer(store)

            return Response({
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Store.DoesNotExist:
            return Response({
                'error': '매장을 찾을 수 없습니다'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)