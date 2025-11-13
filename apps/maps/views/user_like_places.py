from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import Store, LikePlace
from ..serializers import StoreSerializer


class UserLikePlaceListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response({
                'error': '권한이 없습니다'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            likes = LikePlace.objects.filter(
                user_id=user_id
            ).select_related('store')

            data = [
                {
                    'like_place_id': like.id,
                    'store': StoreSerializer(like.store).data,
                    'created_at': like.created_at
                }
                for like in likes
            ]

            return Response({
                'count': len(data),
                'data': data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, user_id):
        if request.user.id != user_id:
            return Response({
                'error': '권한이 없습니다'
            }, status=status.HTTP_403_FORBIDDEN)

        store_id = request.data.get('store_id')

        if not store_id:
            return Response({
                'error': 'store_id는 필수입니다'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = Store.objects.get(pk=store_id)
            like, created = LikePlace.objects.get_or_create(
                user_id=user_id,
                store=store
            )

            if created:
                return Response({
                    'message': '찜 목록에 추가되었습니다',
                    'data': {
                        'like_place_id': like.id,
                        'store_id': store.id,
                        'created_at': like.created_at
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': '이미 찜한 장소입니다'
                }, status=status.HTTP_200_OK)

        except Store.DoesNotExist:
            return Response({
                'error': '가게를 찾을 수 없습니다'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLikePlaceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id, like_id):
        if request.user.id != user_id:
            return Response({
                'error': '권한이 없습니다'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            like = LikePlace.objects.get(pk=like_id, user_id=user_id)
            like.delete()

            return Response({
                'message': '찜 목록에서 삭제되었습니다'
            }, status=status.HTTP_200_OK)

        except LikePlace.DoesNotExist:
            return Response({
                'error': '찜을 찾을 수 없습니다'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)