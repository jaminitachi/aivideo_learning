# VideoEngAI - AI Video Avatar English Learning Platform

<div align="center">

![VideoEngAI Logo](https://img.shields.io/badge/VideoEngAI-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

AI 비디오 아바타와 실시간으로 대화하며 영어를 학습하는 플랫폼입니다.

[데모 보기](#) · [문제 신고하기](https://github.com/yourusername/videoengai/issues) · [기능 요청하기](https://github.com/yourusername/videoengai/issues)

</div>

---

## ✨ 주요 기능

- 🎥 **실시간 비디오 아바타**: AI가 생성한 아바타와 자연스러운 대화
- 🗣️ **음성 인식**: OpenAI Whisper를 사용한 정확한 음성 인식
- ✅ **즉각적인 교정**: 문법, 발음, 어휘 실시간 피드백
- 🔄 **반복 학습**: 틀린 부분을 집중적으로 연습
- 📊 **진도 추적**: 학습 통계 및 약점 분석
- 🎯 **맞춤형 학습**: 개인의 수준에 맞는 대화

## 🎬 데모

![Demo Screenshot](https://via.placeholder.com/800x450?text=VideoEngAI+Demo)

## 🚀 빠른 시작

### 사전 준비

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+ (또는 Docker)
- API 키: OpenAI, ElevenLabs, D-ID

### Docker로 실행 (권장)

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/videoengai.git
cd videoengai

# 2. 환경 변수 설정
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# .env 파일들을 열어 API 키를 입력하세요

# 3. Docker Compose로 실행
docker-compose up -d

# 4. 데이터베이스 마이그레이션
docker-compose exec backend prisma migrate dev

# 5. 브라우저에서 접속
# http://localhost:3000
```

### 로컬 개발 환경

**백엔드:**
```bash
cd backend
./setup.sh  # 또는 수동으로 설정
uvicorn app.main:app --reload
```

**프론트엔드:**
```bash
cd frontend
./setup.sh  # 또는 npm install
npm run dev
```

자세한 설정 방법은 [SETUP_GUIDE.md](./SETUP_GUIDE.md)를 참고하세요.

## 📚 문서

- [설정 가이드](./SETUP_GUIDE.md) - 상세한 설치 및 설정 방법
- [아키텍처 문서](./ARCHITECTURE.md) - 시스템 구조 및 기술 스택
- [API 문서](http://localhost:8000/docs) - Swagger UI (서버 실행 후)

## 🏗️ 프로젝트 구조

```
videoengai/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py            # FastAPI 앱 진입점
│   │   ├── config.py          # 설정 관리
│   │   ├── database.py        # DB 연결
│   │   ├── models/            # Pydantic 모델
│   │   ├── routers/           # API 라우터
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   └── progress.py
│   │   ├── services/          # 비즈니스 로직
│   │   │   ├── stt_service.py      # 음성 인식
│   │   │   ├── llm_service.py      # 대화 생성
│   │   │   ├── tts_service.py      # 음성 합성
│   │   │   ├── avatar_service.py   # 비디오 생성
│   │   │   └── correction_service.py
│   │   └── websocket/         # WebSocket 핸들러
│   ├── prisma/
│   │   └── schema.prisma      # DB 스키마
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/               # App Router
│   │   │   ├── page.tsx       # 홈페이지
│   │   │   └── learning/[sessionId]/
│   │   │       └── page.tsx   # 학습 페이지
│   │   ├── components/        # React 컴포넌트
│   │   │   ├── VideoPlayer.tsx
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── CorrectionFeedback.tsx
│   │   │   └── RepeatPractice.tsx
│   │   ├── lib/               # 유틸리티
│   │   │   ├── websocket.ts
│   │   │   └── audioRecorder.ts
│   │   └── types/             # TypeScript 타입
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── SETUP_GUIDE.md
├── ARCHITECTURE.md
└── README.md
```

## 🛠️ 기술 스택

### 백엔드
- **프레임워크**: FastAPI
- **데이터베이스**: PostgreSQL + Prisma ORM
- **실시간 통신**: WebSocket
- **언어**: Python 3.11+

### 프론트엔드
- **프레임워크**: Next.js 14 (App Router)
- **UI**: React + TypeScript
- **스타일링**: Tailwind CSS
- **상태 관리**: React Hooks

### AI/ML 서비스
- **음성 인식 (STT)**: OpenAI Whisper API
- **대화 생성**: OpenAI GPT-4
- **음성 합성 (TTS)**: ElevenLabs
- **비디오 아바타**: D-ID API
- **발음 평가**: Azure Speech Services (선택)

## 🎯 로드맵

- [x] 기본 대화 기능
- [x] 실시간 교정 피드백
- [x] 학습 진도 추적
- [x] 반복 학습 모드
- [ ] 사용자 인증 시스템
- [ ] 발음 점수 시각화
- [ ] 레벨별 커리큘럼
- [ ] 모바일 앱 (React Native)
- [ ] 멀티플레이어 모드
- [ ] AI 기반 약점 분석

## 🤝 기여하기

기여는 언제나 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 👏 감사의 말

- [OpenAI](https://openai.com/) - Whisper 및 GPT-4 API
- [ElevenLabs](https://elevenlabs.io/) - 고품질 음성 합성
- [D-ID](https://www.d-id.com/) - AI 비디오 아바타 기술
- [FastAPI](https://fastapi.tiangolo.com/) - 빠르고 현대적인 웹 프레임워크
- [Next.js](https://nextjs.org/) - React 프레임워크

## 📧 연락처

프로젝트 관리자 - [@yourname](https://twitter.com/yourname)

프로젝트 링크: [https://github.com/yourusername/videoengai](https://github.com/yourusername/videoengai)

---

<div align="center">

**[⬆ 맨 위로](#videoengai---ai-video-avatar-english-learning-platform)**

Made with ❤️ by [Your Name](https://github.com/yourusername)

</div>
