import os
import re

VIEWS_DIR = "apps/users/views"

def convert_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 이미 spectacular이면 건너뜀
    if "drf_spectacular" in content:
        print(f"✅ already converted: {path}")
        return

    # 1️⃣ import 교체
    content = re.sub(
        r"from\s+drf_yasg\.utils\s+import\s+swagger_auto_schema",
        "from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse",
        content,
    )
    content = re.sub(
        r"from\s+drf_yasg\s+import\s+openapi",
        "from rest_framework import serializers",
        content,
    )

    # 2️⃣ @swagger_auto_schema → @extend_schema 기본형 변환
    content = re.sub(
        r"@swagger_auto_schema\s*\((.*?)\)\s*\n\s*def",
        "@extend_schema(summary='API 설명을 추가하세요', responses={200: OpenApiResponse(description='성공')})\n    def",
        content,
        flags=re.S,
    )

    # 3️⃣ 안내 주석 추가
    header = (
        "# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular\n"
        "# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.\n\n"
    )
    content = header + content

    # 백업 & 덮어쓰기
    backup = path + ".bak"
    with open(backup, "w", encoding="utf-8") as f:
        f.write(content)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✨ converted: {path} (backup saved: {backup})")


def main():
    for root, _, files in os.walk(VIEWS_DIR):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                convert_file(path)


if __name__ == "__main__":
    main()
