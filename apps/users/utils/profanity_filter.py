from better_profanity import profanity

# 기본 비속어 목록 로드 (영어 + 일부 다국어)
profanity.load_censor_words()

# 한글 커스텀 금칙어도 추가 가능
CUSTOM_PROFANITY = [
    "바보", "멍청이", "시발", "병신", "꺼져",
]

def contains_profanity(text: str) -> bool:
    """닉네임이나 이메일에 비속어가 포함되어 있는지 확인"""
    if not text:
        return False

    text = text.lower()
    # 기본 + 커스텀 둘 다 체크
    return profanity.contains_profanity(text) or any(word in text for word in CUSTOM_PROFANITY)
