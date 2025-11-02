#!/bin/bash

# VideoEngAI 프론트엔드 설정 스크립트

echo "🚀 VideoEngAI 프론트엔드 설정을 시작합니다..."

# .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사합니다..."
    cp .env.example .env
    echo "✅ .env 파일이 생성되었습니다."
fi

# 의존성 설치
echo "📥 의존성을 설치합니다..."
npm install

echo "✅ 프론트엔드 설정이 완료되었습니다!"
echo ""
echo "개발 서버를 시작하려면:"
echo "  npm run dev"
echo ""
echo "프로덕션 빌드를 하려면:"
echo "  npm run build"
echo "  npm start"
