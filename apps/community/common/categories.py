from typing import Optional

CATEGORY_ALL_KOR = "전체"
CATEGORY_KOR_ALLOWED = ["자유게시판", "정보공유", "질문게시판"]

ALLOWED_SORT = {"latest", "views", "likes"}
ALLOWED_SEARCH_IN = {"title", "content", "title_content"}

def is_all_category(cat: Optional[str]) -> bool:
    return cat is None or cat == "" or cat == CATEGORY_ALL_KOR

def normalize_category_input(cat: Optional[str]) -> Optional[str]:
    return None if is_all_category(cat) else cat

def default_sort_for_category(_cat: Optional[str]) -> str:
    return "latest"
