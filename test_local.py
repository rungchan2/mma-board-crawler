#!/usr/bin/env python3
"""
로컬 테스트용 스크립트
GitHub Secrets 없이 로컬에서 크롤러 테스트
"""
import os
import sys
from datetime import datetime

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_crawler():
    """크롤러 테스트 (이메일 발송 제외)"""
    from crawler import MMABoardCrawler
    
    print("="*60)
    print("🧪 크롤러 로컬 테스트")
    print(f"📅 실행 시간: {datetime.now()}")
    print("="*60)
    
    # 환경변수 임시 설정 (실제 발송은 안됨)
    os.environ['SENDER_EMAIL'] = 'test@gmail.com'
    os.environ['SENDER_PASSWORD'] = 'test_password'
    os.environ['RECIPIENT_EMAIL'] = 'test@gmail.com'
    
    try:
        crawler = MMABoardCrawler()
        
        # 오늘 게시글 조회
        print("\n📋 오늘 작성된 게시글 조회 중...")
        posts = crawler.get_today_posts()
        
        if posts:
            print(f"\n✅ {len(posts)}개 게시글 발견:")
            for i, post in enumerate(posts, 1):
                print(f"\n[게시글 {i}]")
                print(f"  제목: {post['title']}")
                print(f"  날짜: {post['date']}")
                print(f"  URL: {post['url']}")
                
                # 첫 번째 게시글만 상세 내용 테스트
                if i == 1:
                    content = crawler.get_post_content(post['url'])
                    if content:
                        print(f"  내용 길이: {len(content)}자")
                        
                        # 요약 테스트
                        summary = crawler.summarizer.summarize(content)
                        print(f"  요약: {summary[:100]}...")
        else:
            print("\n⚠️  오늘 작성된 게시글이 없습니다.")
            print("\n💡 모든 게시글 확인 (상위 5개):")
            
            # 날짜 관계없이 최신 게시글 확인
            import requests
            from bs4 import BeautifulSoup
            
            response = crawler.session.get(
                crawler.base_url + crawler.board_url,
                timeout=30
            )
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.select_one('table')
            if table:
                rows = table.select('tbody tr')[:5]
                for row in rows:
                    cells = row.select('td')
                    if len(cells) >= 5:
                        title_cell = cells[1]
                        title_link = title_cell.select_one('a')
                        if title_link:
                            print(f"  - {title_link.get_text(strip=True)} ({cells[3].get_text(strip=True)})")
            
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def test_summarizer():
    """텍스트 요약기 단독 테스트"""
    from text_summarizer import SimpleTextSummarizer
    
    print("\n" + "="*60)
    print("🧪 텍스트 요약기 테스트")
    print("="*60)
    
    summarizer = SimpleTextSummarizer(max_length=200)
    
    sample_text = """
    2026년 1월 입영 (25-10회차) 육군 기술행정병을 다음과 같이 모집하오니, 많은 지원 바랍니다.
    ■ 접수기간: '25. 9. 29.(월) 14:00 ~ '25. 10. 2.(목) 14:00
    ○ 지원서 접수: 군지원(입영신청)안내→ 지원서 작성/수정/취소→ [통합지원서 작성]
    ■ 지원자격
    ○ 지원서 접수연도 기준 18세~28세 ('97년~'07년 출생자)
    ○ 병역판정(신체)검사 결과 1~4급 현역대상
    ○ 각 군 모집계획 공고일 기준, 현역병입영 대상자
    """
    
    summary = summarizer.summarize(sample_text)
    print(f"\n원문 길이: {len(sample_text)}자")
    print(f"요약 결과: {summary}")

if __name__ == "__main__":
    print("🚀 병무청 크롤러 로컬 테스트 시작\n")
    
    # 텍스트 요약기 테스트
    test_summarizer()
    
    # 메인 크롤러 테스트
    test_crawler()
    
    print("\n" + "="*60)
    print("✅ 테스트 완료!")
    print("="*60)