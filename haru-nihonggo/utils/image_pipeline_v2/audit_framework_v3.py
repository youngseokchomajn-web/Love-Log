#!/usr/bin/env python3
"""
추상/기능어 프롬프트 오인 위험 — 실행 프레임워크 구현
======================================================

3가지 보강안을 모두 구현:
1. 서사 밀도(Narrative Density) 요소별 가산 채점 + TOP20 검증
2. 카테고리 분류 우선순위 판별 트리 (충돌 방지)
3. 미분류 2,491개 중 335개 무작위 표본 재검수

출력: abstract_framework_audit_result.json
"""

import json
import re
import random
from collections import defaultdict, OrderedDict

# ──────────────────────────────────────
# 데이터 로드
# ──────────────────────────────────────
with open('utils/image_pipeline_v2/word_categories_all.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

with open('utils/image_pipeline_v2/expanded_tags_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

all_words = []
for cat_name, word_list in categories.items():
    for w in word_list:
        w['_category'] = cat_name
        all_words.append(w)

print(f"총 단어 수: {len(all_words)}")

# ══════════════════════════════════════════════════════════════
# 1. 서사 밀도 채점 시스템 (Narrative Density Scoring v2)
# ══════════════════════════════════════════════════════════════

# 요소별 가산 키워드 사전
SCORING_RUBRIC = {
    'seasonal_nature': {
        'description': '계절/자연 배경',
        'weight': 1,
        'keywords': [
            'cherry blossom', 'sakura', 'autumn leaves', 'falling leaves', 'maple',
            'snow', 'snowfall', 'snowy', 'spring morning', 'summer breeze',
            'winter', 'autumn', 'spring', 'sunflower', 'fireflies',
            'rainy', 'rain', 'rainbow', 'starry sky', 'moonlight',
            'sunset', 'sunrise', 'twilight', 'golden hour', 'dusk', 'dawn',
            'windy', 'stormy', 'cloudy', 'foggy', 'misty',
            'blooming', 'petals', 'wildflower', 'green meadow',
        ]
    },
    'specific_place': {
        'description': '구체적 장소',
        'weight': 1,
        'keywords': [
            'train station', 'railway', 'platform', 'school', 'classroom',
            'kitchen', 'bedroom', 'living room', 'bathroom', 'office',
            'library', 'bookstore', 'cafe', 'restaurant', 'bakery',
            'hospital', 'church', 'temple', 'shrine', 'park',
            'garden', 'backyard', 'porch', 'balcony', 'rooftop',
            'market', 'shop', 'store', 'mall', 'airport',
            'bus stop', 'bridge', 'tunnel', 'alley', 'street corner',
            'village', 'countryside', 'town', 'city', 'Tokyo',
            'beach', 'mountain', 'forest', 'river', 'lake',
            'campus', 'dormitory', 'gymnasium', 'stadium',
            'courthouse', 'police station', 'fire station',
            'workshop', 'studio', 'attic', 'basement', 'cellar',
        ]
    },
    'relationship_narrative': {
        'description': '등장인물 관계성 서사',
        'weight': 1,
        'keywords': [
            'reunion', 'farewell', 'goodbye', 'waving goodbye', 'parting',
            'meeting again', 'recognizing', 'childhood friend',
            'family', 'mother', 'father', 'grandmother', 'grandfather',
            'sister', 'brother', 'son', 'daughter', 'parent',
            'couple', 'lover', 'dating', 'wedding', 'marriage',
            'friendship', 'best friend', 'classmate', 'teammate',
            'caring', 'protecting', 'comforting', 'supporting',
            'quarrel', 'argument', 'reconciliation', 'forgiveness',
            'domestic love', 'family warmth',
        ]
    },
    'emotional_prop': {
        'description': '감정 유발 소품',
        'weight': 1,
        'keywords': [
            'scarf', 'letter', 'photograph', 'photo album', 'diary',
            'locket', 'pendant', 'ring', 'bracelet', 'gift',
            'wrapped present', 'bouquet', 'flower arrangement',
            'teddy bear', 'stuffed animal', 'music box',
            'handkerchief', 'umbrella', 'ticket', 'postcard',
            'love letter', 'farewell letter', 'promise',
            'candle', 'lantern', 'lamp glow', 'warm fireplace',
            'old toy', 'broken toy', 'worn book',
            'compass', 'pocket watch', 'vintage watch',
        ]
    },
    'multi_person_interaction': {
        'description': '인물 수 ≥ 2 + 상호작용',
        'weight': 1,
        'keywords': [
            'hugging', 'hug', 'embrace', 'holding hands',
            'shaking hands', 'high five', 'fist bump',
            'sharing', 'together', 'side by side',
            'whispering', 'chatting', 'talking', 'conversation',
            'playing together', 'walking together', 'running together',
            'group of', 'crowd', 'gathering',
            'helping', 'teaching', 'showing',
            'waving', 'beckoning', 'calling',
            'feeding', 'cooking together', 'eating together',
            '1boy and 1girl', 'boys and girls', 'friends',
        ]
    },
    'time_of_day': {
        'description': '시간대 묘사',
        'weight': 1,
        'keywords': [
            'morning light', 'morning sun', 'early morning',
            'afternoon', 'noon', 'midday',
            'evening', 'night', 'midnight', 'late night',
            'dusk', 'dawn', 'twilight',
            'golden hour', 'blue hour',
            'breakfast', 'lunch', 'dinner', 'supper',
        ]
    },
}


def score_narrative_density(prompt: str) -> dict:
    """
    프롬프트의 서사 밀도를 요소별로 채점.
    Returns: {
        'total': int,
        'breakdown': {요소명: (점수, 매칭된 키워드들)}
    }
    """
    if not prompt:
        return {'total': 0, 'breakdown': {}, 'risk_level': 'low'}
    
    prompt_lower = prompt.lower()
    breakdown = {}
    total = 0
    
    for element_key, element_def in SCORING_RUBRIC.items():
        matched = [kw for kw in element_def['keywords'] if kw in prompt_lower]
        score = element_def['weight'] if matched else 0
        breakdown[element_def['description']] = {
            'score': score,
            'matched': matched[:5]  # 상위 5개만
        }
        total += score
    
    if total >= 4:
        risk_level = 'HIGH'
    elif total >= 2:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
    
    return {
        'total': total,
        'breakdown': breakdown,
        'risk_level': risk_level
    }


# ══════════════════════════════════════════════════════════════
# 2. 카테고리 분류 우선순위 판별 트리 (Priority Decision Tree)
# ══════════════════════════════════════════════════════════════

def classify_priority_tree(w: dict) -> str:
    """
    우선순위 판별 트리에 따른 분류.
    충돌 시: 문법 기능 > 의미적 뉘앙스
    """
    kanji = w.get('kanji', '')
    kana = w.get('hiragana', '')
    ko = w.get('korean', '')
    en = w.get('english', '').lower()
    cat = w.get('_category', '')
    
    # ────────────────────────────
    # Layer 0: 구체적 단어 제외
    # ────────────────────────────
    if cat not in ['abstract_nouns', 'adverbs_functional', 'adjectives_states']:
        # action_verbs, concrete_nouns은 대부분 구체적
        # 다만 일부 추상 동사도 여기 있을 수 있으므로 후속 체크
        if cat == 'action_verbs':
            # 추상적 동사인지 체크
            abs_verb_ko = ['생각하', '깨닫', '이해하', '믿다', '의심', '판단', '추측', '예상', 
                           '기억', '잊다', '상상', '인식', '닮다', '비슷하', '다르다', '같다',
                           '변하다', '바뀌다', '증가', '감소', '의지하', '결심']
            if not any(k in ko for k in abs_verb_ko):
                return None  # 구체적 동사 → 수정 불필요
        elif cat == 'concrete_nouns':
            return None  # 구체적 명사 → 수정 불필요
    
    # ────────────────────────────
    # Layer 1: 의문사 (최우선)
    # ────────────────────────────
    interrogative_kanji_starts = ['何', '誰', '幾']
    interrogative_kana_exact = [
        'なに', 'なん', 'だれ', 'いつ', 'どこ', 'なぜ', 'どう', 'どれ',
        'どの', 'どちら', 'いくつ', 'いくら', 'どなた'
    ]
    if any(kanji.startswith(k) for k in interrogative_kanji_starts) or kana in interrogative_kana_exact:
        return 'CAT-03: 의문사'
    if any(k in ko for k in ['무엇', '누구', '어디', '언제', '왜', '어째서', '어느', '어떻게', '어떤', '몇']):
        return 'CAT-03: 의문사'
    
    # ────────────────────────────
    # Layer 2: 지시어/대명사
    # ────────────────────────────
    demonstrative_exact = [
        'これ', 'それ', 'あれ', 'ここ', 'そこ', 'あそこ',
        'こちら', 'そちら', 'あちら', 'こっち', 'そっち', 'あっち',
        'こう', 'そう', 'ああ', 'この', 'その', 'あの',
        'こんな', 'そんな', 'あんな', 'こんなに', 'そんなに', 'あんなに',
        'どんな', 'どんなに'
    ]
    if kana in demonstrative_exact or kanji in demonstrative_exact:
        return 'CAT-04: 지시어/대명사'
    if any(k in ko for k in ['이것', '저것', '그것', '여기', '거기', '저기', '이쪽', '저쪽', '그쪽', '이런', '저런', '그런']):
        return 'CAT-04: 지시어/대명사'

    # ────────────────────────────
    # Layer 3: 접속사/논리연결어
    # ────────────────────────────
    conjunction_exact = [
        'しかし', 'だから', 'そして', 'すると', 'ところが', 'ところで',
        'それで', 'それに', 'つまり', 'なぜなら', 'けれども', 'もしくは',
        'または', 'および', 'なお', 'ただし', 'ちなみに', 'むしろ',
        'すなわち', 'それでも', 'したがって', 'ゆえに', 'そこで',
        'さて', 'では', 'じゃ', 'じゃあ', 'それとも', 'あるいは',
        'もっとも', '要するに', 'ただ', 'ならびに', 'もしも'
    ]
    if kana in conjunction_exact:
        return 'CAT-05: 접속사/논리연결어'
    if any(k == ko for k in ['하지만', '그러므로', '그리고', '그런데', '즉', '따라서', '게다가', '요컨대', '또한', '그래서', '그럼', '그러면']):
        return 'CAT-05: 접속사/논리연결어'

    # ────────────────────────────
    # Layer 4: 부사류 판별 트리 (핵심 충돌 해소)
    # ────────────────────────────
    
    # 4-A: 정도부사 (양적 크기/정도 수식)
    degree_ko = ['매우', '꽤', '상당히', '대단히', '조금', '약간', '아주', '몹시', '극히',
                 '다소', '충분히', '너무', '겨우', '간신히', '별로', '그다지', '얼마나',
                 '대체로', '꽤나', '그렇게', '이렇게', '저렇게', '더', '덜', '가장', '제일',
                 '한층', '한결', '훨씬', '많이']
    if any(k in ko for k in degree_ko):
        return 'CAT-01: 정도부사'
    
    # 4-B: 시간/빈도 부사 (반복/시점)
    time_freq_ko = ['가끔', '자주', '항상', '언제나', '요즘', '드디어', '마침내', '미리',
                    '곧', '이제', '아직', '벌써', '일찍', '늦게', '나중에', '금방', '방금',
                    '점차', '차차', '이따금', '종종', '늘', '줄곧', '수시로', '때때로',
                    '매번', '한번', '다시', '또', '여전히', '변함없이', '지금', '먼저', '우선']
    if any(k in ko for k in time_freq_ko):
        return 'CAT-06: 시간/빈도 부사'
    
    # 4-C: 동작양태 부사 (방식/모습 수식) — 핵심: 동사를 직접 수식
    manner_ko = ['열심히', '천천히', '빨리', '서둘러', '조용히', '몰래', '살짝',
                 '대충', '꼼꼼히', '조심스럽게', '무심코', '억지로', '기꺼이',
                 '마지못해', '슬쩍', '번갈아', '잔뜩', '이윽고', '문득',
                 '무심결에', '그대로', '푹', '쭉', '확', '탁', '딱', '뚝',
                 '방긋', '생긋', '깜짝', '벌떡', '꾸벅', '흠뻑', '차분히']
    if any(k in ko for k in manner_ko):
        return 'CAT-09: 동작양태 부사'
    
    # 4-D: 양태/확신 부사 (화자의 판단/추측/태도)
    modality_ko = ['아마', '혹시', '확실히', '틀림없이', '분명히', '설마', '반드시', '꼭',
                   '물론', '당연히', '결코', '절대로', '전혀', '도저히', '과연', '역시',
                   '차라리', '만약', '만일', '어쨌든', '어차피', '아무래도', '어쩐지',
                   '마치', '이를테면', '다만', '단지', '그저', '마침', '우연히', '갑자기',
                   '순간', '일부러', '부디', '아무쪼록', '모름지기', '도대체', '대관절',
                   '정말로', '참으로', '한마디로', '한편', '사실', '실은', '실제로',
                   '어쩌면', '오히려', '오로지', '한결같이']
    if any(k in ko for k in modality_ko):
        return 'CAT-06b: 양태/확신 부사'
    
    # ────────────────────────────
    # Layer 5: 비교/관계 동사
    # ────────────────────────────
    if any(k in ko for k in ['닮다', '비슷하', '다르다', '같다', '비교', '대조', '반대', '상대', '맞먹', '관련']):
        return 'CAT-02: 비교/관계'

    # ────────────────────────────
    # Layer 6: 감정/심리 vs 관계/대인 (감정 주체 판별)
    # ────────────────────────────
    
    # 6-A: 관계/대인 추상어 (2인 이상 상호관계 명시)
    relation_ko = ['짝사랑', '사랑', '우정', '이별', '재회', '약속', '신뢰', '배신',
                   '화해', '갈등', '협력', '경쟁', '대립', '동료', '동갑', '서로',
                   '함께', '남녀공학', '상호', '교류', '연대', '유대', '혼인', '결혼', '이혼']
    if any(k in ko for k in relation_ko):
        return 'CAT-08: 관계/대인 추상어'
    
    # 6-B: 감정/심리 추상어 (1인 주관)
    emotion_ko = ['기쁨', '기쁘', '슬픔', '슬프', '분노', '화나', '불안', '걱정', '후회',
                  '감사', '질투', '부끄러', '수치', '자존심', '자신감', '용기', '두려움',
                  '공포', '희망', '절망', '만족', '불만', '외로움', '고독', '향수', '동정',
                  '동감', '흥분', '우울', '짜증', '허탈', '감동', '안심', '긴장', '초조',
                  '침착', '차분', '설렘', '기대', '안도', '놀라움', '경악', '당혹', '분함',
                  '기쁘다', '슬프다', '즐겁', '괴롭', '아쉬움', '아쉽', '후련']
    if any(k in ko for k in emotion_ko):
        return 'CAT-07: 감정/심리 추상어'

    # ────────────────────────────
    # Layer 7: 명사류 하위 분류
    # ────────────────────────────
    
    # 7-A: 시간대/기간 명사
    time_noun_ko = ['아침', '저녁', '낮', '밤', '새벽', '오전', '오후', '정오', '자정',
                    '주말', '평일', '내일', '어제', '모레', '글피', '올해', '작년', '내년',
                    '이번', '지난', '다음', '과거', '미래', '현재', '당시', '최근', '이전',
                    '이후', '기간', '시간', '순간', '시기', '시대', '세기', '시절', '예전',
                    '옛날', '다다음', '재래', '연대', '황혼', '해질녘']
    if any(k in ko for k in time_noun_ko):
        return 'CAT-10: 시간대/기간 명사'
    
    # 7-B: 논리/학술 추상명사
    logic_ko = ['원인', '결과', '영향', '효과', '관계', '근거', '증거', '논리', '이론',
                '원리', '법칙', '개념', '정의', '분류', '구조', '체계', '과정', '방법',
                '수단', '대책', '해결', '문제', '상황', '조건', '전제', '가설', '결론',
                '분석', '평가', '기준', '가치', '의미', '목적', '이유', '본질', '특징',
                '성질', '기능', '역할', '차이', '공통', '유형', '종류', '관점', '시점',
                '입장', '측면', '가능성', '필연', '우연', '인과']
    if any(k in ko for k in logic_ko):
        return 'CAT-12: 논리/학술 추상명사'
    
    # 7-C: 발화/커뮤니케이션
    comm_ko = ['말하다', '전하다', '알리다', '보고', '설명', '발표', '주장', '반론',
               '답변', '질문', '의논', '상담', '협의', '논의', '토론', '소개', '언급',
               '지적', '비판', '칭찬', '격려', '위로', '비난', '고백', '선언', '요청',
               '부탁', '명령', '지시', '제안', '권유', '충고', '경고', '허락', '험담',
               '악담', '욕설', '인사', '감사 인사', '사과', '변명', '해명']
    if any(k in ko for k in comm_ko):
        return 'CAT-11: 발화/커뮤니케이션'
    
    # 7-D: 추상 형용사
    abs_adj_ko = ['중요', '필요', '적절', '충분', '불가능', '가능', '확실', '불확실',
                  '명확', '애매', '모호', '당연', '귀중', '소중', '사소', '긴급', '급한',
                  '곤란', '편리', '불편', '적당', '부적절', '정확', '미묘', '곤란']
    if any(k in ko for k in abs_adj_ko):
        return 'CAT-13: 추상 형용사'
    
    # 7-E: 의지/태도 표현
    attitude_ko = ['결심', '각오', '의지', '다짐', '노력', '끈기', '인내', '포기', '체념',
                   '신중', '대담', '겸손', '오만', '성실', '태도', '자세', '근면', '의욕', '열정',
                   '충실', '희생', '헌신']
    if any(k in ko for k in attitude_ko):
        return 'CAT-14: 의지/태도 표현'
    
    # 7-F: 사회/제도 추상명사
    society_ko = ['법', '권리', '의무', '자유', '평등', '정의', '민주', '사회', '정치',
                  '경제', '문화', '교육', '종교', '전통', '관습', '제도', '정책', '규칙',
                  '규정', '법률', '헌법', '조약', '외교', '선거', '투표', '여론', '규범',
                  '사법', '행정', '입법']
    if any(k in ko for k in society_ko):
        return 'CAT-15: 사회/제도 추상명사'
    
    # 7-G: 경제/거래 추상어
    econ_ko = ['가격', '비용', '요금', '수입', '지출', '이익', '손해', '세금', '급여',
               '월급', '연봉', '예산', '저축', '투자', '할인', '판매', '구매', '거래',
               '수출', '무역', '수지', '적자', '흑자', '인플레', '물가', '환율']
    if any(k in ko for k in econ_ko):
        return 'CAT-16: 경제/거래 추상어'
    
    # 7-H: 결과/성취 추상어
    result_ko = ['성공', '실패', '달성', '완성', '완료', '종료', '시작', '착수', '도전',
                 '극복', '승리', '패배', '합격', '불합격', '채용', '해고', '취업', '퇴직',
                 '졸업', '입학', '결석', '출석']
    if any(k in ko for k in result_ko):
        return 'CAT-17: 결과/성취 추상어'
    
    # 7-I: 수량사/단위
    counter_ko = ['권', '장', '개', '마리', '명', '번', '회', '벌', '대', '병', '잔',
                  '자루', '세는', '단위', '번째', '학점']
    if any(k in ko for k in counter_ko):
        return 'CAT-18: 수량사/단위'
    if re.search(r'〜|ずつ|counter|counting', kanji + kana + en):
        return 'CAT-18: 수량사/단위'
    
    # 7-J: 정도/양적 개념
    quant_ko = ['정도', '한도', '한계', '수준', '범위', '비율', '분량', '용량', '최소',
                '최대', '평균', '합계', '전부', '모두', '일부', '절반', '전체', '나머지',
                '대부분', '소수', '다수', '각각', '각자', '각기', '여러', '다양']
    if any(k in ko for k in quant_ko):
        return 'CAT-19: 정도/양적 개념'
    
    # 7-K: 방향/위치
    direction_ko = ['위', '아래', '옆', '앞', '뒤', '안', '밖', '속', '겉', '사이',
                    '중간', '중심', '가운데', '주변', '근처', '부근', '맞은편', '건너편',
                    '방향', '쪽', '편', '이편', '저편', '도중', '반대쪽']
    if any(k in ko for k in direction_ko):
        return 'CAT-20: 방향/위치'
    
    # 7-L: 경어/기능어
    if any(k in en for k in ['honorific', 'humble', 'polite']):
        return 'CAT-21: 경어/기능어'
    polite_ko = ['인사', '존경', '겸양', '예의', '실례', '사양', '정중']
    if any(k in ko for k in polite_ko):
        return 'CAT-21: 경어/기능어'
    
    # 7-M: 상태변화 동사
    change_ko = ['되다', '변하다', '바뀌다', '증가', '감소', '늘다', '줄다', '강해지다',
                 '약해지다', '악화', '향상', '저하', '발전', '쇠퇴', '진행', '진전']
    if any(k in ko for k in change_ko):
        return 'CAT-22: 상태변화 동사'
    
    # 7-N: 인지/사고 동사
    cognition_ko = ['생각하', '깨닫', '이해하', '알다', '모르다', '믿다', '의심', '판단',
                    '추측', '예상', '기억', '잊다', '연상', '상상', '인식', '성찰', '반성',
                    '착각', '오해']
    if any(k in ko for k in cognition_ko):
        return 'CAT-23: 인지/사고 동사'
    
    # ────────────────────────────
    # Layer 8: 미분류 잔여
    # ────────────────────────────
    if cat in ['abstract_nouns', 'adverbs_functional', 'adjectives_states']:
        return 'UNCLASSIFIED: 미분류 추상어'
    
    return None  # 구체적 단어


# ══════════════════════════════════════════════════════════════
# 실행 및 결과 생성
# ══════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("  Phase 1: 서사 밀도 채점 v2 — TOP 20 검증")
print("=" * 70)

# 원본 리포트 TOP 20 (id → 원본 밀도 점수)
original_top20 = {
    'n1_1263': 6, 'n1_2098': 5, 'n1_0452': 4, 'n1_1910': 4,
    'n1_2401': 4, 'n1_3446': 4, 'n3_1186': 4, 'n1_1310': 4,
    'n1_2641': 4, 'n1_2874': 4, 'n3_1564': 4, 'n3_1657': 4,
    'n2_0949': 4, 'n3_1145': 4, 'n5_0374': 3, 'n5_0220': 3,
    'n5_0165': 3, 'n3_1057': 3, 'n5_0251': 3, 'n3_1559': 3,
}

print(f"\n{'ID':12s} {'원본':>4s} {'v2':>4s} {'차이':>4s} {'위험':>6s} | 요소별 분해")
print("-" * 90)

diffs = []
for w_id, orig_score in original_top20.items():
    prompt = cache.get(w_id, '')
    result = score_narrative_density(prompt)
    diff = result['total'] - orig_score
    diffs.append(abs(diff))
    
    # 요소별 분해 요약
    breakdown_str = ", ".join(
        f"{k}={v['score']}" for k, v in result['breakdown'].items() if v['score'] > 0
    )
    
    print(f"{w_id:12s} {orig_score:4d} {result['total']:4d} {diff:+4d} {result['risk_level']:>6s} | {breakdown_str}")

avg_diff = sum(diffs) / len(diffs)
max_diff = max(diffs)
within_1 = sum(1 for d in diffs if d <= 1)

print(f"\n검증 결과: 평균 오차 {avg_diff:.2f}, 최대 오차 {max_diff}, ±1 이내 {within_1}/{len(diffs)}개 ({within_1/len(diffs)*100:.0f}%)")


# ──────────────────────────────────────
# Phase 2: 전체 분류 실행
# ──────────────────────────────────────
print("\n" + "=" * 70)
print("  Phase 2: 우선순위 판별 트리 전체 분류")
print("=" * 70)

type_groups = defaultdict(list)
for w in all_words:
    stype = classify_priority_tree(w)
    if stype:
        type_groups[stype].append(w)

# 각 카테고리별 서사 밀도 통계
cat_stats = OrderedDict()
total_high = 0
total_medium = 0

for stype in sorted(type_groups.keys()):
    words = type_groups[stype]
    high_count = 0
    medium_count = 0
    
    for w in words:
        w_id = w.get('id', '')
        kanji = w.get('kanji', '')
        prompt = cache.get(w_id, cache.get(kanji, ''))
        result = score_narrative_density(prompt)
        if result['risk_level'] == 'HIGH':
            high_count += 1
        elif result['risk_level'] == 'MEDIUM':
            medium_count += 1
    
    total_high += high_count
    total_medium += medium_count
    cat_stats[stype] = {
        'total': len(words),
        'high_risk': high_count,
        'medium_risk': medium_count,
        'low_risk': len(words) - high_count - medium_count
    }
    
    flag = "🔴" if high_count > 5 else "🟡" if high_count > 0 else "🟢"
    print(f"  {flag} {stype:35s} 총 {len(words):4d}개 │ 🔴{high_count:3d} 🟡{medium_count:3d} 🟢{len(words)-high_count-medium_count:3d}")

classified = sum(len(v) for k, v in type_groups.items() if 'UNCLASSIFIED' not in k)
unclassified = len(type_groups.get('UNCLASSIFIED: 미분류 추상어', []))
total_abstract = classified + unclassified
concrete = len(all_words) - total_abstract

print(f"\n분류 커버리지: {classified}/{total_abstract} ({classified/total_abstract*100:.1f}%)")
print(f"미분류 잔여: {unclassified}개")
print(f"구체적 단어: {concrete}개")
print(f"\n전체 서사 위험: 🔴고위험 {total_high}개, 🟡경계 {total_medium}개")


# ──────────────────────────────────────
# Phase 3: 미분류 335개 무작위 표본 재검수
# ──────────────────────────────────────
print("\n" + "=" * 70)
print("  Phase 3: 미분류 무작위 335개 표본 재검수")
print("=" * 70)

unclassified_words = type_groups.get('UNCLASSIFIED: 미분류 추상어', [])
random.seed(2026)
sample_size = min(335, len(unclassified_words))
sample = random.sample(unclassified_words, sample_size)

sample_results = {'HIGH': [], 'MEDIUM': [], 'LOW': []}

for w in sample:
    w_id = w.get('id', '')
    kanji = w.get('kanji', '')
    prompt = cache.get(w_id, cache.get(kanji, ''))
    result = score_narrative_density(prompt)
    sample_results[result['risk_level']].append({
        'id': w_id,
        'kanji': kanji,
        'kana': w.get('hiragana', ''),
        'korean': w.get('korean', ''),
        'score': result['total'],
        'breakdown': result['breakdown'],
        'prompt_preview': (prompt or '')[:150]
    })

high_pct = len(sample_results['HIGH']) / sample_size * 100
medium_pct = len(sample_results['MEDIUM']) / sample_size * 100
low_pct = len(sample_results['LOW']) / sample_size * 100

print(f"표본 크기: {sample_size}개 (95% 신뢰수준, ±5% 오차범위)")
print(f"🔴 고위험 (≥4점): {len(sample_results['HIGH'])}개 ({high_pct:.1f}%)")
print(f"🟡 경계   (2~3점): {len(sample_results['MEDIUM'])}개 ({medium_pct:.1f}%)")
print(f"🟢 저위험 (0~1점): {len(sample_results['LOW'])}개 ({low_pct:.1f}%)")

# 모집단 추정
est_high = int(unclassified * high_pct / 100)
est_medium = int(unclassified * medium_pct / 100)
print(f"\n모집단 추정 ({unclassified}개 미분류 중):")
print(f"  🔴 고위험 추정: ~{est_high}개")
print(f"  🟡 경계 추정: ~{est_medium}개")
print(f"  🟢 저위험 추정: ~{unclassified - est_high - est_medium}개")

# 고위험 표본 TOP 10
print(f"\n미분류 고위험 표본 TOP 10:")
for item in sorted(sample_results['HIGH'], key=lambda x: -x['score'])[:10]:
    matched_elements = [k for k, v in item['breakdown'].items() if v['score'] > 0]
    print(f"  [{item['id']}] {item['kanji']}({item['kana']}) = {item['korean']} │ 점수:{item['score']}")
    print(f"    요소: {', '.join(matched_elements)}")
    print(f"    {item['prompt_preview'][:120]}...")


# ──────────────────────────────────────
# 최종 리포트 JSON 저장
# ──────────────────────────────────────
final_report = {
    'metadata': {
        'total_words': len(all_words),
        'total_abstract': total_abstract,
        'classified': classified,
        'unclassified': unclassified,
        'concrete': concrete,
        'scoring_version': 'v2_element_based',
    },
    'scoring_validation': {
        'avg_diff_from_original': round(avg_diff, 2),
        'max_diff': max_diff,
        'within_1_ratio': f"{within_1}/{len(diffs)}",
    },
    'category_stats': cat_stats,
    'unclassified_sample_audit': {
        'sample_size': sample_size,
        'confidence_level': '95%',
        'margin_of_error': '±5%',
        'high_risk_pct': round(high_pct, 1),
        'medium_risk_pct': round(medium_pct, 1),
        'low_risk_pct': round(low_pct, 1),
        'estimated_high_in_population': est_high,
        'estimated_medium_in_population': est_medium,
        'high_risk_samples': sorted(sample_results['HIGH'], key=lambda x: -x['score'])[:20],
    },
    'total_risk_summary': {
        'classified_high_risk': total_high,
        'classified_medium_risk': total_medium,
        'unclassified_estimated_high': est_high,
        'unclassified_estimated_medium': est_medium,
        'grand_total_high_risk': total_high + est_high,
        'grand_total_medium_risk': total_medium + est_medium,
    }
}

with open('utils/image_pipeline_v2/abstract_framework_audit_result.json', 'w', encoding='utf-8') as f:
    json.dump(final_report, f, ensure_ascii=False, indent=2, default=str)

print(f"\n💾 최종 리포트 저장: abstract_framework_audit_result.json")
print(f"\n{'=' * 70}")
print(f"  총 위험 단어 추정: 🔴 고위험 {total_high + est_high}개, 🟡 경계 {total_medium + est_medium}개")
print(f"{'=' * 70}")
