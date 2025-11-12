# apps/community/reports/constants.py

# API 입출력(한글 라벨) <-> 저장 코드 매핑
REASON_LABEL_TO_CODE = {
    "혐오 및 차별": "HATE",
    "욕설 및 비방": "ABUSE",
    "불법 정보": "ILLEGAL",
    "스팸 및 홍보성 게시물": "SPAM",
    "개인정보 침해": "PRIVACY",
    "저작권/지적재산권 침해": "IP",
    "청소년 유해 정보": "YOUTH",
    "기타": "OTHER",
}

# 역매핑이 필요하면 사용(예: 조회 응답 시)
REASON_CODE_TO_LABEL = {v: k for k, v in REASON_LABEL_TO_CODE.items()}
