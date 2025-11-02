# VideoEngAI 설정 가이드

## 📋 사전 준비사항

### 필수 소프트웨어
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+ (또는 Docker)
- Git

### API 키 준비
다음 서비스들의 API 키가 필요합니다:

1. **OpenAI** (필수)
   - https://platform.openai.com/api-keys
   - Whisper API (STT)와 GPT-4 (대화 및 교정)에 사용

2. **ElevenLabs** (필수)
   - https://elevenlabs.io/
   - 음성 합성(TTS)에 사용

3. **D-ID** (필수)
   - https://www.d-id.com/
   - AI 비디오 아바타 생성에 사용

4. **Azure Speech Services** (선택)
   - https://azure.microsoft.com/ko-kr/services/cognitive-services/speech-services/
   - 발음 평가에 사용 (없으면 생략 가능)

## 🚀 빠른 시작 (Docker 사용)

### 1. 저장소 클론 및 환경 변수 설정

```bash
cd videoengai
```

### 2. 환경 변수 파일 생성

**백엔드 환경 변수** (`backend/.env`):
```bash
cp backend/.env.example backend/.env
```

`.env` 파일을 열고 API 키들을 입력하세요:
```env
DATABASE_URL=postgresql://videoengai:videoengai_password@postgres:5432/videoengai
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
DID_API_KEY=your_did_api_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region
SECRET_KEY=your_secret_key_here
FRONTEND_URL=http://localhost:3000
```

**프론트엔드 환경 변수** (`frontend/.env`):
```bash
cp frontend/.env.example frontend/.env
```

### 3. Docker로 실행

```bash
docker-compose up -d
```

이 명령어는:
- PostgreSQL 데이터베이스 시작
- 백엔드 FastAPI 서버 시작 (http://localhost:8000)
- 프론트엔드 Next.js 앱 시작 (http://localhost:3000)

### 4. 데이터베이스 마이그레이션

```bash
docker-compose exec backend prisma migrate dev
```

### 5. 접속

브라우저에서 http://localhost:3000 으로 접속하세요!

## 🛠️ 로컬 개발 환경 설정 (Docker 없이)

### 1. 데이터베이스 설정

PostgreSQL을 설치하고 데이터베이스를 생성하세요:

```sql
CREATE DATABASE videoengai;
CREATE USER videoengai WITH PASSWORD 'videoengai_password';
GRANT ALL PRIVILEGES ON DATABASE videoengai TO videoengai;
```

### 2. 백엔드 설정

```bash
cd backend

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# Prisma 클라이언트 생성
prisma generate

# 데이터베이스 마이그레이션
prisma migrate dev

# 서버 실행
uvicorn app.main:app --reload
```

백엔드가 http://localhost:8000 에서 실행됩니다.

### 3. 프론트엔드 설정

새 터미널에서:

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

## 📊 데이터베이스 관리

### Prisma Studio 실행

데이터베이스를 GUI로 확인하려면:

```bash
cd backend
prisma studio
```

http://localhost:5555 에서 Prisma Studio가 열립니다.

### 마이그레이션 생성

스키마를 변경한 후:

```bash
prisma migrate dev --name migration_name
```

## 🧪 테스트

### 백엔드 테스트

```bash
cd backend
pytest
```

### 프론트엔드 테스트

```bash
cd frontend
npm test
```

## 🚨 문제 해결

### 일반적인 문제들

#### 1. WebSocket 연결 오류
- 백엔드 서버가 실행 중인지 확인
- CORS 설정 확인
- 방화벽 설정 확인

#### 2. 마이크 권한 오류
- 브라우저에서 마이크 권한 허용
- HTTPS 연결 필요 (로컬에서는 localhost 허용됨)

#### 3. API 키 오류
- `.env` 파일의 API 키가 올바른지 확인
- API 키에 충분한 크레딧이 있는지 확인

#### 4. 데이터베이스 연결 오류
- PostgreSQL이 실행 중인지 확인
- DATABASE_URL이 올바른지 확인
- 데이터베이스 사용자 권한 확인

## 📝 개발 팁

### 핫 리로드

개발 모드에서는 코드 변경 시 자동으로 서버가 재시작됩니다:
- 백엔드: `--reload` 플래그로 실행
- 프론트엔드: Next.js의 Fast Refresh 기능

### 로그 확인

**백엔드 로그:**
```bash
docker-compose logs -f backend
```

**프론트엔드 로그:**
```bash
docker-compose logs -f frontend
```

**데이터베이스 로그:**
```bash
docker-compose logs -f postgres
```

### API 문서

백엔드 API 문서는 다음 주소에서 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🌟 다음 단계

1. 더 많은 연습 문장 추가
2. 사용자 인증 구현
3. 발음 평가 기능 추가
4. 학습 통계 대시보드 개선
5. 모바일 앱 개발

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해주세요.
