# 🎯 병무청 육군 공지사항 크롤러

매일 밤 11시에 자동으로 병무청 육군 공지사항을 확인하고, 새로운 게시글이 있으면 요약과 함께 이메일로 알려드립니다.

## ✨ 주요 기능

- 📅 **매일 자동 실행**: 한국시간 오후 11시 (GitHub Actions)
- 🔍 **스마트 감지**: 당일 작성된 게시글만 선별
- 📄 **자동 요약**: AI 없이도 핵심 내용을 간단 요약
- 📧 **이메일 알림**: 깔끔한 HTML 이메일로 알림
- 💰 **완전 무료**: GitHub Actions 무료 할당량 활용

## 🚀 설정 방법

### 1. 리포지토리 포크/클론
```bash
git clone https://github.com/your-username/mma-board-crawler.git
cd mma-board-crawler
```

### 2. Gmail 설정
1. **Google 계정 → 보안 → 2단계 인증** 활성화
2. **앱 비밀번호 생성**:
   - 앱: 메일
   - 기기: 기타 (이름: "MMA Crawler")
   - 생성된 16자리 비밀번호 복사

### 3. GitHub Secrets 설정
**Settings → Secrets and variables → Actions → New repository secret**

| 이름 | 값 | 예시 |
|-----|----|---|
| `SENDER_EMAIL` | 발송용 Gmail 주소 | `your-email@gmail.com` |
| `SENDER_PASSWORD` | Gmail 앱 비밀번호 | `abcdefghijklmnop` |
| `RECIPIENT_EMAIL` | 수신용 이메일 | `notify@gmail.com` |

### 4. 배포
파일을 푸시하면 자동으로 GitHub Actions가 설정됩니다.

```bash
git add .
git commit -m "초기 설정 완료"
git push origin main
```

## 🎮 사용법

### 자동 실행
매일 한국시간 오후 11시에 자동 실행됩니다.

### 수동 실행
1. **Actions** 탭 이동
2. **병무청 육군 공지사항 크롤러** 선택
3. **Run workflow** 클릭

### 로그 확인
**Actions** 탭에서 실행 결과와 로그를 확인할 수 있습니다.

## 📧 알림 예시

```
🎯 병무청 육군 공지사항 알림

📅 2025-09-23 23:00:00 | 📝 새 게시글 1건

📌 게시글 1
제목: 2026년 1월 입영 「육군 기술행정병」 모집 안내
작성일: 2025-09-23

📋 요약:
2026년 1월 입영 육군 기술행정병 모집. 접수기간 9월 29일 14시부터 10월 2일 14시까지. 지원자격은 18세-28세 현역대상자...

🔗 원문 보기
```

## 🛠️ 커스터마이징

### 실행 시간 변경
`.github/workflows/crawler.yml`에서 cron 표현식 수정:
```yaml
# 매일 오후 10시로 변경 (UTC 13:00)
- cron: '0 13 * * *'
```

### 요약 길이 조정
`src/text_summarizer.py`에서 `max_length` 수정:
```python
summarizer = SimpleTextSummarizer(max_length=500)  # 500자로 확장
```

## 📊 비용

- **GitHub Actions**: 월 2,000분 무료 (하루 5분 × 30일 = 150분)
- **Gmail SMTP**: 무료
- **총 비용**: **₩0**

## ⚠️ 주의사항

- Gmail 2단계 인증과 앱 비밀번호가 필수입니다
- GitHub Secrets는 절대 공개하지 마세요
- 병무청 사이트 구조 변경 시 코드 수정이 필요할 수 있습니다

## 🔧 문제해결

**이메일이 오지 않을 때:**
1. Gmail 앱 비밀번호 재확인
2. GitHub Secrets 설정 확인
3. Actions 탭에서 에러 로그 확인

**크롤링이 안될 때:**
1. 병무청 사이트 접속 확인
2. 사이트 구조 변경 여부 확인

## 📄 라이센스

MIT License - 자유롭게 사용하세요!