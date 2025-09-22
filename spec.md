# 병무청 육군 공지사항 크롤러 - GitHub Actions 배포판

## 📁 프로젝트 구조

```
mma-board-crawler/
├── .github/
│   └── workflows/
│       └── crawler.yml
├── src/
│   ├── crawler.py
│   ├── email_sender.py
│   └── text_summarizer.py
├── README.md
├── requirements.txt
└── .gitignore
```

## 🚀 설정 및 배포 가이드

### 1단계: GitHub 리포지토리 생성
1. GitHub에서 새 리포지토리 생성 (`mma-board-crawler`)
2. 리포지토리를 로컬로 클론

### 2단계: Gmail 앱 비밀번호 설정
1. **Google 계정 → 보안**
2. **2단계 인증 활성화**
3. **앱 비밀번호 생성**
   - 앱 선택: 메일
   - 기기 선택: 기타 (맞춤 이름 입력: "MMA Crawler")
   - 생성된 16자리 비밀번호 복사 (예: `abcd efgh ijkl mnop`)

### 3단계: GitHub Secrets 설정
리포지토리 → Settings → Secrets and variables → Actions → New repository secret

```
SENDER_EMAIL: your-email@gmail.com
SENDER_PASSWORD: abcdefghijklmnop (앱 비밀번호)
RECIPIENT_EMAIL: recipient@gmail.com
```

## 📄 파일별 코드

### requirements.txt
```txt
requests==2.31.0
beautifulsoup4==4.12.2
```

### .gitignore
```
__pycache__/
*.py[cod]
*$py.class
*.log
.env
.DS_Store
```

### .github/workflows/crawler.yml
```yaml
name: 병무청 육군 공지사항 크롤러

on:
  schedule:
    # 매일 UTC 14:00 (한국시간 23:00)
    - cron: '0 14 * * *'
  workflow_dispatch: # 수동 실행 가능

jobs:
  crawl-and-notify:
    runs-on: ubuntu-latest
    
    steps:
    - name: 코드 체크아웃
      uses: actions/checkout@v4
    
    - name: Python 설정
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: 의존성 설치
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: 크롤러 실행
      env:
        SENDER_EMAIL: ${{ secrets.SENDER_EMAIL }}
        SENDER_PASSWORD: ${{ secrets.SENDER_PASSWORD }}
        RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
      run: |
        python src/crawler.py
```

### src/text_summarizer.py
```python
"""
텍스트 요약기 - 외부 API 없이 간단한 추출 요약
"""
import re
from typing import Optional

class SimpleTextSummarizer:
    def __init__(self, max_length: int = 300):
        self.max_length = max_length
    
    def summarize(self, text: str) -> str:
        """
        간단한 텍스트 요약
        - 중요한 정보가 포함된 문장 추출
        - 날짜, 기간, 절차 등 핵심 정보 우선
        """
        if not text:
            return "내용을 불러올 수 없습니다."
        
        # 텍스트 전처리
        text = self._preprocess_text(text)
        
        # 문장 단위로 분할
        sentences = self._split_sentences(text)
        
        if not sentences:
            return text[:self.max_length] + "..." if len(text) > self.max_length else text
        
        # 중요한 문장 추출
        important_sentences = self._extract_important_sentences(sentences)
        
        # 요약문 생성
        summary = self._build_summary(important_sentences)
        
        return summary
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 연속된 공백, 탭, 줄바꿈 정리
        text = re.sub(r'\s+', ' ', text)
        # 특수 문자 정리
        text = re.sub(r'[■●○▶▷◆◇★☆]', '', text)
        return text.strip()
    
    def _split_sentences(self, text: str) -> list:
        """문장 단위로 분할"""
        # 한국어 문장 구분
        sentences = re.split(r'[.!?]\s+|(?<=[다음양함임됨니다])\s+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _extract_important_sentences(self, sentences: list) -> list:
        """중요한 문장 추출"""
        important_keywords = [
            # 날짜/기간 관련
            r'\d{4}[\-\.]\d{1,2}[\-\.]\d{1,2}',  # 날짜
            r'\d{1,2}월\s*\d{1,2}일',  # 한국식 날짜
            r'접수기간|마감|신청|모집',
            
            # 중요 정보
            r'지원자격|모집인원|선발기준',
            r'합격|발표|결과',
            r'제출|준비|구비',
            r'입영|훈련|복무',
            
            # 주의사항
            r'유의|주의|반드시|필수',
            r'제외|불가|금지'
        ]
        
        scored_sentences = []
        
        for sentence in sentences[:20]:  # 처음 20개 문장만 분석
            score = 0
            
            # 키워드 점수 계산
            for keyword_pattern in important_keywords:
                if re.search(keyword_pattern, sentence):
                    score += 2
            
            # 문장 길이 보정 (너무 짧거나 긴 문장 페널티)
            if 20 <= len(sentence) <= 100:
                score += 1
            elif len(sentence) > 200:
                score -= 1
            
            # 숫자 포함 문장 우대 (날짜, 인원수 등)
            if re.search(r'\d+', sentence):
                score += 1
            
            scored_sentences.append((sentence, score))
        
        # 점수순 정렬하여 상위 문장 선택
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sentence for sentence, score in scored_sentences[:5] if score > 0]
    
    def _build_summary(self, sentences: list) -> str:
        """요약문 구성"""
        if not sentences:
            return "주요 내용을 추출할 수 없습니다."
        
        summary = ""
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) > self.max_length:
                break
            summary += sentence + " "
            current_length += len(sentence)
        
        summary = summary.strip()
        
        if len(summary) > self.max_length:
            summary = summary[:self.max_length] + "..."
        
        return summary if summary else "요약할 수 있는 내용이 없습니다."


# 사용 예시
if __name__ == "__main__":
    summarizer = SimpleTextSummarizer(max_length=200)
    
    sample_text = """
    2026년 1월 입영 (25-10회차) 육군 기술행정병을 다음과 같이 모집하오니, 많은 지원 바랍니다.
    ■ 접수기간: '25. 9. 29.(월) 14:00 ~ '25. 10. 2.(목) 14:00
    ○ 지원서 접수: 군지원(입영신청)안내→ 지원서 작성/수정/취소→ [통합지원서 작성]
    ■ 지원자격
    ○ 지원서 접수연도 기준 18세~28세 ('97년~'07년 출생자)
    ○ 병역판정(신체)검사 결과 1~4급 현역대상
    """
    
    print(summarizer.summarize(sample_text))
```

### src/email_sender.py
```python
"""
Gmail SMTP를 이용한 이메일 발송
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        # 환경변수 검증
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            raise ValueError("이메일 설정이 완료되지 않았습니다. GitHub Secrets를 확인해주세요.")
    
    def send_notification(self, posts: List[Dict]) -> bool:
        """
        새 게시글 알림 이메일 발송
        """
        if not posts:
            logger.info("발송할 게시글이 없습니다.")
            return True
        
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = self._create_subject(posts)
            
            # HTML과 텍스트 버전 모두 생성
            text_body = self._create_text_body(posts)
            html_body = self._create_html_body(posts)
            
            # 메시지에 추가
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"✅ 이메일 발송 완료: {len(posts)}건")
            return True
            
        except Exception as e:
            logger.error(f"❌ 이메일 발송 실패: {e}")
            return False
    
    def _create_subject(self, posts: List[Dict]) -> str:
        """이메일 제목 생성"""
        today = datetime.now().strftime('%m/%d')
        return f"🚨 [병무청] 육군 공지 {len(posts)}건 업데이트 ({today})"
    
    def _create_text_body(self, posts: List[Dict]) -> str:
        """텍스트 이메일 본문 생성"""
        body = f"""
🎯 병무청 육군 공지사항 알림

📅 확인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📝 새 게시글: {len(posts)}건

{'='*60}
"""
        
        for i, post in enumerate(posts, 1):
            body += f"""
📌 게시글 {i}

제목: {post['title']}
작성일: {post['date']}
링크: {post['url']}

📋 요약:
{post.get('summary', '요약 정보가 없습니다.')}

{'='*60}
"""
        
        body += """

🔗 병무청 육군 공지사항: https://www.mma.go.kr/board/boardList.do?gesipan_id=69&mc=usr0000127

※ 이 메일은 GitHub Actions를 통해 자동 발송되었습니다.
※ 중요한 내용은 반드시 원문을 확인해주세요.
"""
        return body
    
    def _create_html_body(self, posts: List[Dict]) -> str:
        """HTML 이메일 본문 생성"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .content {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .post {{ background: white; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .post-title {{ color: #007bff; font-weight: bold; font-size: 16px; margin-bottom: 10px; }}
        .post-meta {{ color: #6c757d; font-size: 14px; margin-bottom: 15px; }}
        .post-summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; font-size: 14px; }}
        .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; }}
        .link-button {{ display: inline-block; background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🎯 병무청 육군 공지사항 알림</h2>
        <p>📅 {current_time} | 📝 새 게시글 {len(posts)}건</p>
    </div>
    
    <div class="content">
"""
        
        for i, post in enumerate(posts, 1):
            html += f"""
        <div class="post">
            <div class="post-title">📌 {post['title']}</div>
            <div class="post-meta">
                작성일: {post['date']} | 
                <a href="{post['url']}" class="link-button" target="_blank">📖 원문 보기</a>
            </div>
            <div class="post-summary">
                <strong>📋 요약:</strong><br>
                {post.get('summary', '요약 정보가 없습니다.').replace('\n', '<br>')}
            </div>
        </div>
"""
        
        html += """
    </div>
    
    <div class="footer">
        <p>
            <a href="https://www.mma.go.kr/board/boardList.do?gesipan_id=69&mc=usr0000127" target="_blank">
                🔗 병무청 육군 공지사항 바로가기
            </a>
        </p>
        <p>※ 이 메일은 GitHub Actions를 통해 자동 발송되었습니다.</p>
        <p>※ 중요한 내용은 반드시 원문을 확인해주세요.</p>
    </div>
</body>
</html>
"""
        return html
```

### src/crawler.py
```python
#!/usr/bin/env python3
"""
병무청 육군 공지사항 크롤러 - GitHub Actions 버전
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import time
import logging
from typing import List, Dict, Optional

from text_summarizer import SimpleTextSummarizer
from email_sender import EmailSender

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MMABoardCrawler:
    def __init__(self):
        self.base_url = "https://www.mma.go.kr"
        self.board_url = "/board/boardList.do?gesipan_id=69&mc=usr0000127"
        
        # 세션 설정
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 컴포넌트 초기화
        self.summarizer = SimpleTextSummarizer(max_length=300)
        self.email_sender = EmailSender()
    
    def get_today_posts(self) -> List[Dict]:
        """
        오늘 작성된 게시글 목록 조회
        """
        posts = []
        today = date.today()
        
        try:
            logger.info(f"🔍 게시판 크롤링 시작: {self.base_url + self.board_url}")
            
            response = self.session.get(
                self.base_url + self.board_url, 
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 게시글 테이블 찾기
            table = soup.select_one('table')
            if not table:
                logger.warning("⚠️  게시글 테이블을 찾을 수 없습니다.")
                return posts
            
            # 테이블 행 추출
            rows = table.select('tbody tr')
            logger.info(f"📄 총 {len(rows)}개 행 발견")
            
            for row in rows:
                cells = row.select('td')
                
                # 최소 5개 셀이 있어야 함 (번호, 제목, 첨부, 작성일, 조회수)
                if len(cells) < 5:
                    continue
                
                try:
                    # 작성일 추출 및 파싱
                    date_text = cells[3].get_text(strip=True)
                    
                    # 날짜 형식 확인 (YYYY-MM-DD)
                    post_date = datetime.strptime(date_text, '%Y-%m-%d').date()
                    
                    # 오늘 날짜와 비교
                    if post_date == today:
                        # 제목과 링크 추출
                        title_cell = cells[1]
                        title_link = title_cell.select_one('a')
                        
                        if title_link and title_link.get('href'):
                            post = {
                                'title': title_link.get_text(strip=True),
                                'url': self._build_full_url(title_link.get('href')),
                                'date': date_text,
                                'number': cells[0].get_text(strip=True)
                            }
                            posts.append(post)
                            logger.info(f"✅ 새 게시글 발견: {post['title']}")
                
                except (ValueError, AttributeError) as e:
                    # 날짜 파싱 실패 또는 링크 없음 - 계속 진행
                    continue
            
            logger.info(f"🎯 오늘 작성된 게시글: {len(posts)}건")
            
        except requests.RequestException as e:
            logger.error(f"❌ 네트워크 오류: {e}")
        except Exception as e:
            logger.error(f"❌ 크롤링 오류: {e}")
        
        return posts
    
    def get_post_content(self, post_url: str) -> Optional[str]:
        """
        게시글 상세 내용 크롤링
        """
        try:
            logger.info(f"📖 게시글 내용 크롤링: {post_url}")
            
            # 요청 간격 조절
            time.sleep(1)
            
            response = self.session.get(post_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 게시글 내용 추출 (여러 패턴 시도)
            content_selectors = [
                'table tbody tr td',  # 기본 테이블 구조
                '.board-content',      # 클래스명 기반
                '#content',            # ID 기반
                'div.content',         # div 컨테이너
            ]
            
            content = None
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(separator='\n', strip=True)
                    if len(text) > 100:  # 충분한 길이의 텍스트
                        content = text
                        break
                if content:
                    break
            
            if content:
                logger.info(f"✅ 내용 추출 완료: {len(content)}자")
                return content
            else:
                logger.warning("⚠️  게시글 내용을 찾을 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"❌ 게시글 내용 크롤링 실패: {e}")
            return None
    
    def _build_full_url(self, relative_url: str) -> str:
        """상대 URL을 절대 URL로 변환"""
        if relative_url.startswith('http'):
            return relative_url
        elif relative_url.startswith('/'):
            return self.base_url + relative_url
        else:
            return self.base_url + '/' + relative_url
    
    def process_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        게시글 목록 처리 (내용 크롤링 및 요약)
        """
        processed_posts = []
        
        for post in posts:
            logger.info(f"🔄 게시글 처리 중: {post['title']}")
            
            # 게시글 내용 크롤링
            content = self.get_post_content(post['url'])
            
            # 내용 요약
            if content:
                summary = self.summarizer.summarize(content)
                post['summary'] = summary
                post['content_length'] = len(content)
            else:
                post['summary'] = "게시글 내용을 불러올 수 없습니다."
                post['content_length'] = 0
            
            processed_posts.append(post)
        
        return processed_posts
    
    def run(self):
        """
        크롤러 메인 실행 함수
        """
        logger.info("🚀 병무청 육군 공지사항 크롤러 시작")
        logger.info(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. 오늘 작성된 게시글 조회
            today_posts = self.get_today_posts()
            
            if not today_posts:
                logger.info("ℹ️  오늘 작성된 새 게시글이 없습니다.")
                return
            
            # 2. 게시글 내용 크롤링 및 요약
            processed_posts = self.process_posts(today_posts)
            
            # 3. 이메일 알림 발송
            success = self.email_sender.send_notification(processed_posts)
            
            if success:
                logger.info("🎉 크롤링 및 알림 발송 완료!")
            else:
                logger.error("❌ 알림 발송 실패")
                
        except Exception as e:
            logger.error(f"❌ 크롤러 실행 중 오류 발생: {e}")
            raise

def main():
    """메인 실행 함수"""
    try:
        crawler = MMABoardCrawler()
        crawler.run()
    except Exception as e:
        logger.error(f"❌ 프로그램 실행 실패: {e}")
        raise

if __name__ == "__main__":
    main()
```

### README.md
```markdown
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
|-----|----|----|
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
```

## 🎯 배포 체크리스트

- [ ] GitHub 리포지토리 생성
- [ ] Gmail 앱 비밀번호 생성  
- [ ] GitHub Secrets 3개 설정
- [ ] 모든 파일 업로드
- [ ] Actions 탭에서 수동 실행 테스트
- [ ] 이메일 수신 확인

이제 완전히 무료로 GitHub Actions에서 동작하는 병무청 크롤러가 준비되었습니다! 🚀