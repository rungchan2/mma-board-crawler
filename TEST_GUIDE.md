# 🧪 테스트 가이드

## 1. 로컬 테스트 (이메일 발송 없이)

### 방법 1: 테스트 스크립트 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# 테스트 스크립트 실행
python test_local.py
```

이 스크립트는:
- 오늘 작성된 게시글 확인
- 첫 번째 게시글 내용 크롤링
- 텍스트 요약 기능 테스트
- 이메일 발송은 건너뜀

### 방법 2: 환경변수 설정 후 직접 실행
```bash
# 환경변수 임시 설정
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@gmail.com"

# 크롤러 실행
python src/crawler.py
```

## 2. GitHub Actions 수동 테스트

### GitHub에서 수동 실행
1. GitHub 리포지토리로 이동
2. **Actions** 탭 클릭
3. 좌측에서 **"병무청 육군 공지사항 크롤러"** 선택
4. 우측 **"Run workflow"** 버튼 클릭
5. **"Run workflow"** 확인

### 실행 상태 확인
- Actions 탭에서 실행 중인 workflow 클릭
- 각 단계별 로그 확인 가능
- 에러 발생 시 상세 메시지 확인

## 3. 테스트 체크리스트

### ✅ 로컬 테스트
- [ ] `pip install -r requirements.txt` 성공
- [ ] `python test_local.py` 실행 성공
- [ ] 게시글 목록 조회 확인
- [ ] 텍스트 요약 기능 확인

### ✅ GitHub Actions 테스트
- [ ] GitHub Secrets 설정 완료
  - SENDER_EMAIL
  - SENDER_PASSWORD
  - RECIPIENT_EMAIL
- [ ] Actions 수동 실행 성공
- [ ] 이메일 수신 확인

## 4. 문제 해결

### "No module named 'requests'" 에러
```bash
pip install requests beautifulsoup4
```

### 이메일 발송 실패
1. Gmail 2단계 인증 확인
2. 앱 비밀번호 정확히 입력 (공백 제거)
3. GitHub Secrets 설정 확인

### 크롤링 실패
- 병무청 사이트 접속 가능 여부 확인
- 네트워크 연결 상태 확인

## 5. 디버깅 팁

### 상세 로그 보기
```python
# src/crawler.py 에서 로그 레벨 변경
logging.basicConfig(
    level=logging.DEBUG,  # INFO → DEBUG로 변경
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### 특정 날짜 테스트
```python
# src/crawler.py의 get_today_posts() 메서드에서
today = date.today()  # 이 줄을
today = date(2025, 9, 23)  # 특정 날짜로 변경
```