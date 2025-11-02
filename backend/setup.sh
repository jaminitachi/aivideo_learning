#!/bin/bash

# VideoEngAI 백엔드 설정 스크립트

echo "🚀 VideoEngAI 백엔드 설정을 시작합니다..."

# 가상 환경 생성
echo "📦 가상 환경을 생성합니다..."
python3 -m venv venv

# 가상 환경 활성화
echo "🔧 가상 환경을 활성화합니다..."
source venv/bin/activate

# 의존성 설치
echo "📥 의존성을 설치합니다..."
pip install -r requirements.txt

# .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사합니다..."
    cp .env.example .env
    echo "❗ .env 파일을 열어 API 키를 입력해주세요!"
    exit 1
fi

# Prisma 클라이언트 생성
echo "🗄️  Prisma 클라이언트를 생성합니다..."
prisma generate

# 데이터베이스 마이그레이션
echo "🔄 데이터베이스 마이그레이션을 실행합니다..."
prisma migrate dev

echo "✅ 백엔드 설정이 완료되었습니다!"
echo ""
echo "서버를 시작하려면:"
echo "  uvicorn app.main:app --reload"
