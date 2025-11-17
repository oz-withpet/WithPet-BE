from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError

from apps.mypage import user_service, post_activity_service, map_activity_service

from apps.mypage.serializers import (
  MyProfileUpdateSerializer,
  PasswordChangeSerializer,
  WithdrawSerializer,
  MyReportPostOut,
  LikedStoreOut,
)
from apps.community.posts.serializers import PostListItemCommunityOut
from apps.common.exceptions import (
  NicknameConflictError, InvalidPasswordError, NicknameMismatchError,
  ApiSuccessWrapper, ApiErrorWrapper,
)


class ProfileView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    # 프로필 조회
    profile_data = user_service.get_profile(request.user.id)
    return Response(ApiSuccessWrapper(data=profile_data).to_dict(), status=status.HTTP_200_OK)

  def patch(self, request):
    # 프로필 수정
    serializer = MyProfileUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
      user_service.update_profile(request.user.id, serializer.validated_data)
      return Response(ApiSuccessWrapper(message="프로필이 수정되었습니다.").to_dict(), status=status.HTTP_200_OK)
    except NicknameConflictError as e:
      return Response(ApiErrorWrapper(code="CONFLICT", message=str(e)).to_dict(), status=status.HTTP_409_CONFLICT)
    except Exception:
      return Response(ApiErrorWrapper(code="SERVER_ERROR", message="프로필 업데이트 실패").to_dict(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NicknameCheckView(APIView):
  permission_classes = [AllowAny]

  def get(self, request):
    # 닉네임 중복 검사
    nickname = request.query_params.get('nickname')

    temp_serializer = MyProfileUpdateSerializer(data={'nickname': nickname})
    if not temp_serializer.is_valid(raise_exception=False):
      return Response(ApiErrorWrapper(code="BAD_REQUEST", message="닉네임 형식이 올바르지 않습니다.").to_dict(), status=status.HTTP_400_BAD_REQUEST)

    is_available = user_service.check_nickname_availability(nickname)

    return Response({
      "success": True,
      "is_available": is_available
    }, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request):
    # 비밀번호 변경
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})

    if not serializer.is_valid():
      return Response(ApiErrorWrapper(code="BAD_REQUEST", message="비밀번호 확인에 실패했습니다.").to_dict(), status=status.HTTP_400_BAD_REQUEST)

    new_password = serializer.validated_data['new_password']
    confirm_password = serializer.validated_data['new_password_confirm']

    try:
      user_service.change_password(request.user.id, new_password, confirm_password)
      return Response(ApiSuccessWrapper(message="비밀번호가 변경되었습니다.").to_dict(), status=status.HTTP_200_OK)
    except InvalidPasswordError as e:
      return Response(ApiErrorWrapper(code="PASSWORD_MISMATCH", message=str(e)).to_dict(), status=status.HTTP_403_FORBIDDEN)
    except Exception:
      return Response(ApiErrorWrapper(code="SERVER_ERROR", message="비밀번호 변경 실패").to_dict(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WithdrawView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request):
    # 회원 탈퇴
    serializer = WithdrawSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    nickname_input = serializer.validated_data.get('nickname')

    try:
      user_service.withdraw_user(request.user.id, nickname_input)
      return Response(status=status.HTTP_204_NO_CONTENT)
    except NicknameMismatchError as e:
      return Response(ApiErrorWrapper(code="NICKNAME_MISMATCH", message=str(e)).to_dict(), status=status.HTTP_403_FORBIDDEN)
    except Exception:
      return Response(ApiErrorWrapper(code="SERVER_ERROR", message="회원 탈퇴 처리 실패").to_dict(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 활동 목록 조회

def _get_paginated_response(result: dict, serializer_class, request, list_key="posts"):

  serializer = serializer_class(result['items'], many=True, context={'request': request})

  response_data = {
    list_key: serializer.data,
    "page": result.get('page', 1),
    "page_size": result.get('page_size', 20),
    "total": result.get('total'),
  }

  if result.get('next_after'):
    response_data['next_after'] = result['next_after']
    response_data['has_next'] = result['has_next']

  return Response(response_data, status=status.HTTP_200_OK)


class MyPostsView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    # 작성한 게시글 조회
    params = request.query_params.dict()
    result = post_activity_service.get_my_posts_list(request.user.id, params)

    return _get_paginated_response(result, PostListItemCommunityOut, request, list_key="posts")


class MyLikesView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    # 좋아요 게시글 조회
    params = request.query_params.dict()
    result = post_activity_service.get_my_liked_posts_list(request.user.id, params)

    return _get_paginated_response(result, PostListItemCommunityOut, request, list_key="posts")


class MyReportsView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    # 신고한 게시글 조회
    params = request.query_params.dict()

    try:
      result = post_activity_service.get_my_reported_list(request.user.id, params)

      serializer = MyReportPostOut(result['items'], many=True, context={'request': request})

      return Response({
        "reports": serializer.data,
        "page": result.get('page', 1),
        "page_size": result.get('page_size', 20),
        "total": result.get('total'),
      }, status=status.HTTP_200_OK)
    except Exception as e:
      import traceback
      print(f"!!! MYPAGE REPORTS ERROR: {e}")
      traceback.print_exc()

      return Response(ApiErrorWrapper(code="SERVER_ERROR", message="신고 목록 조회 실패").to_dict(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyFavoritePlacesView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    # 관심 장소 조회
    params = request.query_params.dict()

    try:
      result = map_activity_service.get_my_liked_stores_list(request.user.id, params)

      serializer = LikedStoreOut(result['items'], many=True, context={'request': request})

      response_data = {
        "liked_stores": serializer.data,
        "page": result.get('page', 1),
        "page_size": result.get('page_size', 20),
        "total": result.get('total'),
      }

      if result.get('next_after'):
        response_data['next_after'] = result['next_after']
        response_data['has_next'] = result['has_next']

      return Response(response_data, status=status.HTTP_200_OK)

    except ValidationError as e:
      return Response(ApiErrorWrapper(code="BAD_REQUEST", message="요청 파라미터 오류").to_dict(), status=status.HTTP_400_BAD_REQUEST)
    except Exception:
      return Response(ApiErrorWrapper(code="SERVER_ERROR", message="관심 장소 조회 실패").to_dict(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)