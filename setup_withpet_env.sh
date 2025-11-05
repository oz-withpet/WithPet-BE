#!/bin/bash
# ==================================================
# 🐾 WithPet-BE 개발환경 완전 자동 세팅 스크립트 (서버 자동 실행 포함)
# ==================================================
# 실행 위치: 프로젝트 루트 (WithPet-BE/)
# 실행 명령: bash setup_withpet_env.sh
# ==================================================

echo ""
echo "🐾 WithPet-BE 환경 설정을 시작합니다..."
echo "--------------------------------------------"

# --- 1️⃣ Python 버전 확인 ---
PYTHON_VERSION=$(python3 -V 2>&1)
echo "🐍 현재 Python 버전: $PYTHON_VERSION"

# --- 2️⃣ 가상환경 생성 ---
if [ ! -d "venv" ]; then
  echo "📦 가상환경(venv) 생성 중..."
  python3 -m venv venv
else
  echo "✅ 가상환경이 이미 존재합니다. (venv)"
fi

# --- 3️⃣ 가상환경 활성화 ---
echo "🔗 가상환경 활성화 중..."
source venv/bin/activate

# --- 4️⃣ pip 최신화 ---
echo "⬆️  pip 업그레이드 중..."
pip install --upgrade pip

# --- 5️⃣ .editorconfig 설정 ---
cat <<'EOF' > .editorconfig
root = true
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4
EOF
echo "✅ .editorconfig 생성 완료"

# --- 6️⃣ .gitattributes 설정 ---
cat <<'EOF' > .gitattributes
* text=auto eol=lf
EOF
echo "✅ .gitattributes 생성 완료"

# --- 7️⃣ requiremen

