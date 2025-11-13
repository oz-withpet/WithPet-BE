from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
  # 프로필 및 계정 관리
  path('profile', views.ProfileView.as_view(), name='profile'),
  path('profile/check-nickname', views.NicknameCheckView.as_view(), name='check-nickname'),
  path('password', views.PasswordChangeView.as_view(), name='password-change'),
  path('withdraw', views.WithdrawView.as_view(), name='withdraw'),

  # 활동 목록 조회
  path('posts', views.MyPostsView.as_view(), name='my-posts'),
  path('likes/posts', views.MyLikesView.as_view(), name='my-likes-posts'),
  path('reports', views.MyReportsView.as_view(), name='my-reports'),
  path('favorites/places', views.MyFavoritePlacesView.as_view(), name='my-favorites-places'),
]