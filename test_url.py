#!/usr/bin/env python3
"""
URL 빌딩 테스트
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 환경변수 임시 설정
os.environ['SENDER_EMAIL'] = 'test@test.com'
os.environ['SENDER_PASSWORD'] = 'test'
os.environ['RECIPIENT_EMAIL'] = 'test@test.com'

from crawler import MMABoardCrawler

def test_url_building():
    crawler = MMABoardCrawler()
    
    # 예시 상대 URL
    relative_url = "boardView.do?gesipan_id=69&gsgeul_no=1520532&pageI"
    
    # URL 빌딩 테스트
    full_url = crawler._build_full_url(relative_url)
    
    print("원본 상대 URL:")
    print(relative_url)
    print("\n생성된 전체 URL:")
    print(full_url)
    
    print("\n예상 URL:")
    print("https://www.mma.go.kr/board/boardView.do?gesipan_id=69&gsgeul_no=1520532&pageIndex=1&searchCondition=&searchKeyword=&pageUnit=10&mc=usr0000127&jbc_gonggibodo=0")

if __name__ == "__main__":
    test_url_building()