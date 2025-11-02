# VideoEngAI 아키텍처 문서

## 시스템 개요

VideoEngAI는 AI 비디오 아바타와 실시간 대화를 통해 영어를 학습하는 플랫폼입니다.

## 기술 스택

### 백엔드
- **프레임워크**: FastAPI (Python 3.11+)
- **데이터베이스**: PostgreSQL 16
- **ORM**: Prisma
- **실시간 통신**: WebSocket

### 프론트엔드
- **프레임워크**: Next.js 14 (App Router)
- **언어**: TypeScript
- **스타일링**: Tailwind CSS
- **상태 관리**: React Hooks + Zustand

### AI/ML 서비스
- **STT (음성 → 텍스트)**: OpenAI Whisper API
- **LLM (대화 및 교정)**: OpenAI GPT-4
- **TTS (텍스트 → 음성)**: ElevenLabs API
- **비디오 아바타**: D-ID API
- **발음 평가**: Azure Pronunciation Assessment (선택)

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                         Client (Browser)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Video Player│  │ Chat UI      │  │ Correction UI    │   │
│  │ (D-ID)      │  │ (Messages)   │  │ (Feedback)       │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
│         │                 │                    │             │
│         └─────────────────┴────────────────────┘             │
│                           │                                  │
│                    ┌──────▼──────┐                          │
│                    │  WebSocket  │                          │
│                    │  Connection │                          │
│                    └──────┬──────┘                          │
└───────────────────────────┼─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   FastAPI      │
                    │   Backend      │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼─────────┐
│  WebSocket     │  │  REST API   │  │   Database       │
│  Handler       │  │  Endpoints  │  │   (PostgreSQL)   │
└───────┬────────┘  └──────┬──────┘  └────────┬─────────┘
        │                   │                   │
┌───────▼───────────────────▼───────────────────▼─────────┐
│                    Service Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │   STT    │  │   LLM    │  │   TTS    │  │  Avatar ││
│  │ Service  │  │ Service  │  │ Service  │  │ Service ││
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘│
│       │             │              │              │     │
└───────┼─────────────┼──────────────┼──────────────┼─────┘
        │             │              │              │
┌───────▼─────┐ ┌────▼─────┐ ┌──────▼─────┐ ┌──────▼─────┐
│  OpenAI     │ │ OpenAI   │ │ ElevenLabs │ │   D-ID     │
│  Whisper    │ │  GPT-4   │ │    API     │ │    API     │
└─────────────┘ └──────────┘ └────────────┘ └────────────┘
```

## 데이터 플로우

### 1. 사용자 음성 입력 처리

```
User speaks → Browser captures audio → WebSocket sends audio data
  → STT Service (Whisper) → Text transcription
  → LLM Service (GPT-4) → Correction analysis + Response generation
  → TTS Service (ElevenLabs) → Audio generation
  → Avatar Service (D-ID) → Video generation
  → WebSocket sends response → Browser displays video + corrections
```

### 2. 교정 피드백 플로우

```
User text → LLM analyzes
  → Identifies errors (grammar, pronunciation, vocabulary)
  → Generates corrections with explanations
  → Suggests better expressions
  → Saves to database
  → Displays in UI
```

## 데이터베이스 스키마

### Users (사용자)
- id, email, name, password_hash
- 관계: sessions, progress

### Sessions (학습 세션)
- id, user_id, started_at, ended_at, duration
- 관계: user, conversations, corrections

### Conversations (대화)
- id, session_id, role, content, audio_url, video_url, timestamp
- 관계: session, corrections

### Corrections (교정)
- id, session_id, conversation_id, correction_type, original_text, corrected_text, explanation, severity
- 관계: session, conversation

### Progress (진도)
- id, user_id, total_sessions, total_duration, total_corrections, scores
- 관계: user

### PracticePhrases (연습 문장)
- id, category, difficulty, english_text, korean_text, example_audio

## API 엔드포인트

### WebSocket
- `WS /ws/conversation/{session_id}`: 실시간 대화 연결

### REST API

#### Users
- `POST /api/users`: 사용자 생성
- `GET /api/users/{user_id}`: 사용자 조회
- `GET /api/users/{user_id}/sessions`: 사용자 세션 목록

#### Conversations
- `POST /api/conversations/sessions`: 세션 생성
- `POST /api/conversations/sessions/{session_id}/end`: 세션 종료
- `GET /api/conversations/sessions/{session_id}`: 세션 조회
- `GET /api/conversations/sessions/{session_id}/conversations`: 대화 목록
- `GET /api/conversations/sessions/{session_id}/corrections`: 교정 목록

#### Progress
- `GET /api/progress/{user_id}`: 진도 조회
- `GET /api/progress/{user_id}/stats`: 통계 조회
- `GET /api/progress/{user_id}/weaknesses`: 약점 분석

## 보안

### API 키 관리
- 환경 변수로 관리
- `.env` 파일은 `.gitignore`에 포함
- 프로덕션에서는 시크릿 관리 서비스 사용 권장

### CORS
- 프론트엔드 URL만 허용
- 설정 가능한 환경 변수

### 데이터베이스
- Prisma ORM으로 SQL 인젝션 방지
- 패스워드 해싱 (bcrypt)

## 성능 최적화

### 캐싱
- API 응답 캐싱 (향후 구현)
- Prisma 쿼리 최적화

### 비동기 처리
- 비디오 생성은 백그라운드에서 처리
- WebSocket으로 완료 시 알림

### 데이터베이스 최적화
- 인덱스 적용 (session_id, user_id 등)
- 쿼리 최적화

## 확장성

### 수평 확장
- 백엔드: 로드 밸런서 뒤에 여러 인스턴스
- 데이터베이스: 읽기 복제본 추가

### 수직 확장
- 서버 리소스 증가
- 데이터베이스 성능 향상

## 모니터링 및 로깅

### 로깅
- 구조화된 로깅
- 에러 추적
- API 호출 로깅

### 모니터링
- 서버 상태 모니터링
- API 응답 시간 추적
- 에러율 모니터링

## 배포

### Docker
- Docker Compose로 로컬 개발
- 프로덕션은 Kubernetes 권장

### CI/CD
- GitHub Actions
- 자동 테스트
- 자동 배포

## 향후 개선 사항

1. **사용자 인증**
   - JWT 토큰 기반 인증
   - OAuth 소셜 로그인

2. **실시간 발음 평가**
   - Azure Pronunciation Assessment 통합
   - 발음 점수 시각화

3. **학습 커리큘럼**
   - 레벨별 학습 경로
   - 맞춤형 추천

4. **모바일 앱**
   - React Native
   - 오프라인 모드

5. **고급 분석**
   - 학습 패턴 분석
   - AI 기반 약점 진단

6. **멀티플레이어**
   - 다른 학습자와 대화 연습
   - 그룹 학습 세션
