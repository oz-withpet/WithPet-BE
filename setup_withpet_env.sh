#!/bin/bash
# ==================================================
# WithPet-BE 개발환경 자동 설정 스크립트
# ==================================================

echo "🐾 WithPet-BE 환경 설정을 시작합니다..."

# --- 1. .editorconfig 생성 ---
cat <<'EOF' > .editorconfig
root = true
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.py]
max_line_length = 100

[*.{html,css,js}]
indent_size = 2

[*.{yml,yaml,json}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
EOF
echo "✅ .editorconfig 생성 완료"

# --- 2. .gitattributes 생성 ---
cat <<'EOF' > .gitattributes
# 자동으로 줄바꿈(LF) 통일
* text=auto eol=lf
EOF
echo "✅ .gitattributes 생성 완료"

# --- 3. requirements.txt 확인 및 보완 ---
echo "📦 requirements.txt 업데이트 중..."
cat <<'EOF' > requirements.txt
Django>=4.2
djangorestframework>=3.16
django-cors-headers
drf-yasg
drf-spectacular
EOF
echo "✅ requirements.txt 생성/갱신 완료"

# --- 4. 패키지 설치 ---
echo "📦 패키지 설치 중..."
pip install -r requirements.txt

# --- 5. 서버 체크 ---
echo "🔍 Django 설정 확인 중..."
python manage.py check

echo "🎉 WithPet-BE 개발환경 설정이 완료되었습니다!"
