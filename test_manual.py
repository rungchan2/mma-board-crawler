#!/usr/bin/env python3
"""
수동 테스트 - 최신 게시글 1개 크롤링 및 이메일 발송 테스트
"""
import os
import sys
from datetime import datetime

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_manual_mode():
    """수동 모드 테스트 (최신 게시글 1개)"""
    
    print("="*60)
    print("🧪 수동 모드 테스트 - 최신 게시글 1개 + 이메일 발송")
    print("="*60)
    
    # 환경변수 설정 (실제 값으로 변경 필요)
    print("\n⚠️  환경변수를 설정하세요:")
    print("export SENDER_EMAIL='your-email@gmail.com'")
    print("export SENDER_PASSWORD='16자리앱비밀번호'  # 띄어쓰기 없이!")
    print("export RECIPIENT_EMAIL='받을이메일@gmail.com'")
    print("export MANUAL_MODE='true'\n")
    
    # 환경변수 확인
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        print("❌ 환경변수가 설정되지 않았습니다!")
        print("\n실제 테스트를 원하면 다음 명령어 실행:")
        print("export SENDER_EMAIL='your-email@gmail.com'")
        print("export SENDER_PASSWORD='abcdefghijklmnop'  # 실제 16자리")
        print("export RECIPIENT_EMAIL='recipient@gmail.com'")
        print("export MANUAL_MODE='true'")
        print("python test_manual.py")
        return
    
    print(f"✅ 발신 이메일: {sender_email}")
    print(f"✅ 비밀번호 길이: {len(sender_password)}자")
    print(f"✅ 수신 이메일: {recipient_email}")
    
    # 수동 모드 설정
    os.environ['MANUAL_MODE'] = 'true'
    
    from crawler import MMABoardCrawler
    
    try:
        print("\n🚀 크롤러 실행 중...")
        crawler = MMABoardCrawler()
        crawler.run()
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual_mode()