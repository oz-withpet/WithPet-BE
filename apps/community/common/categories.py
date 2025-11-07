from typing import Optional

# 스펙: 실제 카테고리 3종 + 쿼리용 가상 "전체"
CATEGORY_ALL_KOR = "전체"
CATEGORY_KOR_ALLOWED = ["자유게시판", "정보공유", "질문게시판"]

# 커뮤니티 리스트(view=community)에서 허용되는 열거값
ALLOWED_SORT = {"latest", "views", "likes"}
ALLOWED_SEARCH_IN = {"title", "content", "title_content"}

def is_all_category(cat: Optional[str]) -> bool:
    return cat is None or cat == "" or cat == CATEGORY_ALL_KOR

def normalize_category_input(cat: Optional[str]) -> Optional[str]:
    """'전체'면 None으로 정규화하여 필터 미적용"""
    return None if is_all_category(cat) else cat

def default_sort_for_category(_cat: Optional[str]) -> str:
    """현재 정책: '전체' 포함 항상 최신순"""
    return "latest"
