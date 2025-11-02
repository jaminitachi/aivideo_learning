# 시작하기 - VideoEngAI

## 🎉 환영합니다!

VideoEngAI 프로젝트를 선택해 주셔서 감사합니다. 이 가이드는 처음 프로젝트를 시작하는 분들을 위한 단계별 안내입니다.

## 📋 체크리스트

시작하기 전에 다음 항목들을 확인하세요:

- [ ] Python 3.11 이상 설치됨
- [ ] Node.js 20 이상 설치됨
- [ ] PostgreSQL 설치됨 (또는 Docker)
- [ ] OpenAI API 키 발급받음
- [ ] ElevenLabs API 키 발급받음
- [ ] D-ID API 키 발급받음

## 🚀 3분 안에 시작하기

### 옵션 1: Docker 사용 (가장 쉬움)

```bash
# 1. 환경 변수 설정
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. API 키 입력 (텍스트 에디터로 .env 파일 편집)
# backend/.env 파일을 열어서:
# OPENAI_API_KEY=여기에_API키_입력
# ELEVENLABS_API_KEY=여기에_API키_입력
# DID_API_KEY=여기에_API키_입력

# 3. Docker로 실행
docker-compose up -d

# 4. 데이터베이스 초기화
docker-compose exec backend prisma migrate dev

# 5. 완료! 브라우저에서 http://localhost:3000 접속
```

### 옵션 2: 로컬 환경 사용

**백엔드 시작:**
```bash
cd backend
./setup.sh
# .env 파일 편집하여 API 키 입력
uvicorn app.main:app --reload
```

**프론트엔드 시작 (새 터미널):**
```bash
cd frontend
./setup.sh
# .env 파일 편집
npm run dev
```

## 🔑 API 키 발급받기

### 1. OpenAI API 키
1. https://platform.openai.com/signup 에서 회원가입
2. https://platform.openai.com/api-keys 에서 API 키 생성
3. 최소 $5 충전 (Whisper + GPT-4 사용)

### 2. ElevenLabs API 키
1. https://elevenlabs.io/sign-up 에서 회원가입
2. https://elevenlabs.io/app/settings/api 에서 API 키 확인
3. 무료 플랜: 월 10,000자 (테스트용으로 충분)

### 3. D-ID API 키
1. https://studio.d-id.com/account/settings 에서 회원가입
2. Settings > API 에서 API 키 생성
3. 무료 트라이얼: 20 크레딧 (약 20개 비디오)

### 4. Azure Speech Services (선택사항)
1. https://portal.azure.com 에서 계정 생성
2. Speech Services 리소스 생성
3. 키와 지역 확인
4. 무료 플랜: 월 500만자 STT

## 🎯 첫 번째 대화 시작하기

1. **브라우저에서 http://localhost:3000 접속**

2. **"지금 시작하기" 버튼 클릭**

3. **마이크 권한 허용**
   - 브라우저에서 마이크 권한을 요청하면 "허용" 클릭

4. **마이크 버튼 클릭하여 녹음 시작**
   - 빨간 버튼이 나타나면 영어로 말하기 시작
   - 예: "Hello, how are you today?"

5. **다시 클릭하여 녹음 종료**
   - AI가 음성을 인식하고 분석
   - 교정 피드백과 응답을 받음
   - 비디오 아바타가 대답함

## 📊 기능 살펴보기

### 실시간 대화
- 자연스러운 영어 대화 연습
- AI 선생님이 적절한 응답 제공
- 대화 내역 자동 저장

### 교정 피드백
- 문법 오류 실시간 감지
- 더 자연스러운 표현 제안
- 한국어로 설명 제공

### 반복 연습
- 자주 틀리는 문장 집중 연습
- 다양한 카테고리의 연습 문장
- 난이도별 학습 지원

### 진도 추적
- 총 학습 시간 기록
- 교정받은 항목 통계
- 약점 분석 및 개선 제안

## 🔧 문제 해결

### 문제: "데이터베이스 연결 오류"
**해결:**
```bash
# PostgreSQL이 실행 중인지 확인
# macOS:
brew services start postgresql

# Linux:
sudo systemctl start postgresql

# Docker:
docker-compose up -d postgres
```

### 문제: "마이크를 찾을 수 없습니다"
**해결:**
1. 브라우저 설정에서 마이크 권한 확인
2. 시스템 설정에서 마이크 권한 확인
3. HTTPS 연결 사용 (로컬에서는 localhost 자동 허용)

### 문제: "API 키 오류"
**해결:**
1. `.env` 파일이 올바른 위치에 있는지 확인
2. API 키에 공백이나 따옴표가 없는지 확인
3. API 키가 활성화되어 있고 잔액이 있는지 확인

### 문제: "비디오가 생성되지 않습니다"
**해결:**
1. D-ID API 크레딧이 남아있는지 확인
2. 네트워크 연결 확인
3. 백엔드 로그에서 에러 메시지 확인:
   ```bash
   docker-compose logs -f backend
   ```

## 💡 팁과 요령

### 효과적인 학습을 위한 팁
1. **천천히 또박또박 말하기**: 음성 인식 정확도 향상
2. **짧은 문장으로 시작**: 기초부터 탄탄히
3. **교정 피드백 반복 학습**: 같은 실수 방지
4. **매일 조금씩**: 꾸준한 연습이 중요

### 개발 팁
1. **API 문서 활용**: http://localhost:8000/docs
2. **Prisma Studio 사용**: `prisma studio`로 DB 확인
3. **로그 확인**: `docker-compose logs -f` 로 디버깅
4. **핫 리로드**: 코드 변경 시 자동 재시작

## 📚 다음 단계

프로젝트가 성공적으로 실행되었다면:

1. [ARCHITECTURE.md](./ARCHITECTURE.md) 읽어보기 - 시스템 구조 이해
2. [SETUP_GUIDE.md](./SETUP_GUIDE.md) 참고하기 - 상세 설정
3. 코드 커스터마이징하기 - 자신만의 기능 추가
4. 기여하기 - Pull Request 제출

## 🆘 도움이 필요하신가요?

- 📖 문서: [전체 문서 보기](./README.md)
- 🐛 버그 리포트: [Issues](https://github.com/yourusername/videoengai/issues)
- 💬 질문: [Discussions](https://github.com/yourusername/videoengai/discussions)
- 📧 이메일: your-email@example.com

## 🎓 학습 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Next.js 공식 문서](https://nextjs.org/docs)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [Prisma 문서](https://www.prisma.io/docs)

---

**즐거운 학습 되세요! 🚀**
