#!/usr/bin/env python3
"""
병무청 육군 공지사항 크롤러 - GitHub Actions 버전
"""
import os
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
    
    def get_latest_posts(self, count: int = 1) -> List[Dict]:
        """
        최신 게시글 목록 조회 (수동 테스트용)
        """
        posts = []
        
        try:
            logger.info(f"🔍 최신 게시글 {count}개 크롤링: {self.base_url + self.board_url}")
            
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
            
            for idx, row in enumerate(rows[:count]):  # 최신 N개만
                cells = row.select('td')
                
                logger.debug(f"행 {idx}: 셀 개수 = {len(cells)}")
                
                # 최소 4개 셀이 있어야 함 (제목, 첨부, 작성일, 조회수)
                if len(cells) < 4:
                    logger.debug(f"행 {idx}: 셀 부족 (최소 4개 필요)")
                    continue
                
                try:
                    # 각 셀의 내용 로깅
                    for i, cell in enumerate(cells[:4]):
                        logger.debug(f"  셀 {i}: {cell.get_text(strip=True)[:30]}")
                    
                    # 제목과 링크 추출 (첫 번째 셀)
                    title_cell = cells[0]
                    title_link = title_cell.select_one('a')
                    
                    if title_link and title_link.get('href'):
                        post = {
                            'title': title_link.get_text(strip=True),
                            'url': self._build_full_url(title_link.get('href')),
                            'date': cells[2].get_text(strip=True),  # 세 번째 셀이 날짜
                            'number': str(idx + 1)  # 번호는 인덱스로 대체
                        }
                        posts.append(post)
                        logger.info(f"✅ 게시글 발견: {post['title']}")
                    else:
                        logger.debug(f"행 {idx}: 링크 없음")
                
                except (ValueError, AttributeError) as e:
                    logger.debug(f"행 {idx}: 파싱 오류 - {e}")
                    continue
            
            logger.info(f"🎯 최신 게시글 {len(posts)}건 수집 완료")
            
        except requests.RequestException as e:
            logger.error(f"❌ 네트워크 오류: {e}")
        except Exception as e:
            logger.error(f"❌ 크롤링 오류: {e}")
        
        return posts
    
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
            
            for row_idx, row in enumerate(rows):
                cells = row.select('td')
                
                # 최소 4개 셀이 있어야 함 (제목, 첨부, 작성일, 조회수)
                if len(cells) < 4:
                    continue
                
                try:
                    # 작성일 추출 및 파싱 (세 번째 셀)
                    date_text = cells[2].get_text(strip=True)
                    
                    # 날짜 형식 확인 (YYYY-MM-DD)
                    post_date = datetime.strptime(date_text, '%Y-%m-%d').date()
                    
                    # 오늘 날짜와 비교
                    if post_date == today:
                        # 제목과 링크 추출 (첫 번째 셀)
                        title_cell = cells[0]
                        title_link = title_cell.select_one('a')
                        
                        if title_link and title_link.get('href'):
                            post = {
                                'title': title_link.get_text(strip=True),
                                'url': self._build_full_url(title_link.get('href')),
                                'date': date_text,
                                'number': str(row_idx + 1)
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
            # 상대 URL에 필요한 파라미터 추가
            if 'boardView.do' in relative_url and 'pageIndex=' not in relative_url:
                # pageIndex와 기타 필수 파라미터 추가
                if '?' in relative_url:
                    relative_url += '&pageIndex=1&searchCondition=&searchKeyword=&pageUnit=10&mc=usr0000127&jbc_gonggibodo=0'
                else:
                    relative_url += '?pageIndex=1&searchCondition=&searchKeyword=&pageUnit=10&mc=usr0000127&jbc_gonggibodo=0'
            
            return self.base_url + '/board/' + relative_url
    
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
        
        # 수동 실행 모드 확인 (GitHub Actions workflow_dispatch)
        is_manual = os.getenv('MANUAL_MODE', 'false').lower() == 'true'
        
        try:
            if is_manual:
                # 수동 실행: 최신 게시글 1개
                logger.info("🔧 수동 실행 모드: 최신 게시글 1개 조회")
                posts = self.get_latest_posts(1)
                
                if not posts:
                    logger.info("❌ 게시글을 찾을 수 없습니다.")
                    return
            else:
                # 자동 실행: 오늘 작성된 게시글
                logger.info("⏰ 자동 실행 모드: 오늘 작성된 게시글 조회")
                posts = self.get_today_posts()
                
                if not posts:
                    logger.info("ℹ️  오늘 작성된 새 게시글이 없습니다.")
                    return
            
            # 2. 게시글 내용 크롤링 및 요약
            processed_posts = self.process_posts(posts)
            
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