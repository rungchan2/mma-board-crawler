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