from django.shortcuts import get_object_or_404

def get_post_model():
    # 프로젝트 구조에 맞춰 import 경로만 맞추세요.
    from apps.community.posts.models import Post
    return Post

def get_post_or_404(post_id: int):
    # ✅ 린터 대응: 대문자 대신 소문자 변수명 사용
    post_model = get_post_model()
    # PK 컬럼명이 id가 아니라면 여기만 맞춰주세요 (예: post_id=post_id)
    return get_object_or_404(post_model, id=post_id)
