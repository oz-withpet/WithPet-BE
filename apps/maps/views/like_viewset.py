from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import LikePlace, Store
from ..serializers import LikePlaceSerializer

# GET /api/likes/ 조회
# POST /api/likes/ 추가
# DELETE /api/likes/{id}/ 삭제
class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikePlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LikePlace.objects.filter(
            user=self.request.user
        ).select_related('store')

    def create(self, request):
        store_id = request.data.get('store_id')

        if not store_id:
            return Response(
                {'detail': 'store_id는 필수입니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            store = Store.objects.get(pk=store_id, is_active=True)
        except Store.DoesNotExist:
            return Response(
                {'detail': '매장을 찾을 수 없습니다'},
                status=status.HTTP_404_NOT_FOUND
            )

        if LikePlace.objects.filter(user=request.user, store=store).exists():
            return Response(
                {'detail': '이미 찜한 매장입니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        like = LikePlace.objects.create(user=request.user, store=store)
        serializer = self.get_serializer(like)

        return Response(serializer.data, status=status.HTTP_201_CREATED)