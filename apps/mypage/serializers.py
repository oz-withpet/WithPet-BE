from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.community.reports.models import Report
from apps.community.posts.serializers import PostListItemCommunityOut
from apps.maps.serializers.store import StoreSerializer
from apps.maps.models.store import LikePlace

User = get_user_model()

# 프로필 조회
class MyProfileSerializer(serializers.ModelSerializer):
  user_id = serializers.IntegerField(source="pk", read_only=True)
  gender = serializers.CharField(allow_null=True)

  # 타입 변환
  has_pet = serializers.SerializerMethodField()

  class Meta:
    model = User
    fields = ('user_id', 'email', 'nickname', 'username', 'gender', 'has_pet', 'created_at')
    read_only_fields = ('email', 'username', 'created_at')

  @staticmethod
  def get_has_pet(obj):
    return bool(getattr(obj, 'pet_type', None))

# 프로필 수정
class MyProfileUpdateSerializer(serializers.Serializer):
  nickname = serializers.CharField(max_length=30, min_length=2, required=False)
  gender = serializers.ChoiceField(choices=['male', 'female'], required=False)

  # ex) true -> dog 등으로 변환 로직 필요
  pet_type = serializers.CharField(required=False, max_length=20, allow_null=True)

# 비밀번호 변경
class PasswordChangeSerializer(serializers.Serializer):
  new_password = serializers.CharField(min_length=8)
  new_password_confirm = serializers.CharField(min_length=8)

# 회원 탈퇴
class WithdrawSerializer(serializers.Serializer):
  nickname = serializers.CharField(required=True, max_length=30)

# 관심 장소
class LikedStoreOut(serializers.ModelSerializer):
  like_place_id = serializers.IntegerField(source="pk", read_only=True)
  store = StoreSerializer(read_only=True)

  class Meta:
    model = LikePlace
    fields = ('like_place_id', 'store', 'created_at')

# 신고 게시글
class MyReportPostOut(serializers.ModelSerializer):
  report_id = serializers.IntegerField(source="pk", read_only=True)
  post = PostListItemCommunityOut(source='target', read_only=True)
  reason = serializers.CharField(source='reason_label', read_only=True)

  class Meta:
    model = Report
    fields = ("report_id", "post", "reason", "detail", "status", "created_at")