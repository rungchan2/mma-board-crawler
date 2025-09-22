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