#!/usr/bin/env python3
"""
크롤러 디버깅 - HTML 구조 확인
"""
import requests
from bs4 import BeautifulSoup

def debug_html_structure():
    """HTML 구조 디버깅"""
    url = "https://www.mma.go.kr/board/boardList.do?gesipan_id=69&mc=usr0000127"
    
    print("🔍 병무청 게시판 HTML 구조 분석")
    print("="*60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 테이블 찾기
        tables = soup.find_all('table')
        print(f"\n📊 테이블 개수: {len(tables)}")
        
        for i, table in enumerate(tables):
            print(f"\n테이블 {i+1}:")
            
            # tbody 확인
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                print(f"  - tbody의 tr 개수: {len(rows)}")
                
                if rows and len(rows) > 0:
                    # 첫 번째 행 분석
                    first_row = rows[0]
                    cells = first_row.find_all('td')
                    print(f"  - 첫 번째 행의 td 개수: {len(cells)}")
                    
                    # 각 셀 내용 출력
                    for j, cell in enumerate(cells):
                        text = cell.get_text(strip=True)[:50]
                        print(f"    셀 {j}: {text}")
                        
                        # 링크 확인
                        link = cell.find('a')
                        if link:
                            print(f"      → 링크 발견: {link.get('href', 'href없음')[:50]}")
            
            # thead 확인 (헤더 구조 파악)
            thead = table.find('thead')
            if thead:
                print("  - thead 있음")
                th_cells = thead.find_all('th')
                headers = [th.get_text(strip=True) for th in th_cells]
                print(f"    헤더: {headers}")
        
        # 다른 방식으로도 확인
        print("\n🔍 CSS 선택자로 다시 확인:")
        
        # 방법 1: table tbody tr
        rows1 = soup.select('table tbody tr')
        print(f"'table tbody tr' 선택자: {len(rows1)}개")
        
        # 방법 2: 클래스나 ID가 있는지 확인
        board_table = soup.select('.board_list, .list_table, .table')
        print(f"게시판 관련 클래스 테이블: {len(board_table)}개")
        
        if rows1 and len(rows1) > 0:
            print("\n첫 번째 게시글 행 상세 분석:")
            first = rows1[0]
            tds = first.select('td')
            print(f"TD 개수: {len(tds)}")
            
            for idx, td in enumerate(tds):
                print(f"\nTD {idx}:")
                print(f"  텍스트: {td.get_text(strip=True)[:50]}")
                a_tag = td.select_one('a')
                if a_tag:
                    print(f"  링크 텍스트: {a_tag.get_text(strip=True)[:50]}")
                    print(f"  링크 href: {a_tag.get('href', 'None')[:50]}")
                    
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_html_structure()