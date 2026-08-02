#!/usr/bin/env python3
"""
8,424개 전체 일본어 단어 프롬프트 재작성 스크립트 (V5)
=====================================================================
V4의 문제점 (실측 결과):
  - 8,424개 중 8,221개(97.6%)가 "Subject: An anime character interacting
    with {한국어 단어}. Visual metaphor: Clear central visual focus on
    {한국어 단어}." 라는 깨진 범용 템플릿으로 떨어짐.
  - 구체 명사는 모델이 알아서 그려주는 경우가 많아 티가 덜 났지만,
    추상/기능어(계간, 辛うじて, ご苦労様 등)는 시각적으로 그릴 수 없는
    단어 그 자체를 반복 입력하는 꼴이라 결과가 랜덤/오염됨.
  - 원인: audit_framework_v3.py에는 카테고리당 20~50개의 풍부한 판별
    키워드가 있었지만, 실제 생성 스크립트(V4)에는 카테고리당 4~9개의
    예시 키워드만 하드코딩되어 있어서 서로 연결되지 않았음.

V5에서 하는 일:
  1. audit_framework_v3.py의 classify_priority_tree()를 그대로 가져와
     23개 카테고리 전체(+미분류)를 우선순위 트리로 판별.
  2. 카테고리별로 실제로 그릴 수 있는 시각 메타포(subject/metaphor)를
     설계해서 매핑.
  3. 구체 명사/동사는 기존 방식(리터럴 서술)을 유지 — 실측상 구체어는
     문제가 없었음.
  4. 진짜 미분류(UNCLASSIFIED) 잔여어는, 최소한 "글자 반복" 대신
     "추상 개념임을 모델에게 명시하고 상징 아이콘으로 표현하라"는
     안전한 폴백 지시로 대체하고, 별도 리스트로 뽑아서 수동 검토
     대상으로 flag.
  5. 실행 후 카테고리별 통계 + 미분류 잔여 리스트를 CSV로 저장.

사용법:
  haru-nihonggo/ 디렉토리에서 실행:
    python3 utils/image_pipeline_v2/rebuild_all_master_prompts_v5.py

  --dry-run 플래그를 주면 캐시 파일에 실제로 쓰지 않고 통계만 출력.
"""

import json
import os
import re
import sys
import csv
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "expanded_tags_cache.json")
MASTER_FILE = os.path.join(BASE_DIR, "word_categories_all.json")
UNCLASSIFIED_REPORT = os.path.join(BASE_DIR, "v5_unclassified_review_needed.csv")
STATS_REPORT = os.path.join(BASE_DIR, "v5_rebuild_stats.json")


# ══════════════════════════════════════════════════════════════
# 1. 우선순위 판별 트리 (audit_framework_v3.py에서 그대로 가져옴)
# ══════════════════════════════════════════════════════════════

def classify_priority_tree(w: dict) -> str:
    """
    우선순위 판별 트리에 따른 분류.
    충돌 시: 문법 기능 > 의미적 뉘앙스
    (audit_framework_v3.py와 100% 동일 — 감사 결과와 생성 결과가
    어긋나지 않도록 로직을 분리하지 않고 그대로 재사용한다.)
    """
    kanji = w.get('kanji', '')
    kana = w.get('hiragana', '')
    ko = w.get('korean', '')
    en = w.get('english', '').lower()
    cat = w.get('_category', '')

    # Layer 0: 구체적 단어 제외
    if cat not in ['abstract_nouns', 'adverbs_functional', 'adjectives_states']:
        if cat == 'action_verbs':
            abs_verb_ko = ['생각하', '깨닫', '이해하', '믿다', '의심', '판단', '추측', '예상',
                           '기억', '잊다', '상상', '인식', '닮다', '비슷하', '다르다', '같다',
                           '변하다', '바뀌다', '증가', '감소', '의지하', '결심']
            if not any(k in ko for k in abs_verb_ko):
                return None
        elif cat == 'concrete_nouns':
            return None

    # Layer 1: 의문사
    interrogative_kanji_starts = ['何', '誰', '幾']
    interrogative_kana_exact = [
        'なに', 'なん', 'だれ', 'いつ', 'どこ', 'なぜ', 'どう', 'どれ',
        'どの', 'どちら', 'いくつ', 'いくら', 'どなた'
    ]
    if any(kanji.startswith(k) for k in interrogative_kanji_starts) or kana in interrogative_kana_exact:
        return 'CAT-03: 의문사'
    if any(k in ko for k in ['무엇', '누구', '어디', '언제', '왜', '어째서', '어느', '어떻게', '어떤', '몇']):
        return 'CAT-03: 의문사'

    # Layer 2: 지시어/대명사
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

    # Layer 3: 접속사/논리연결어
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

    # Layer 4: 부사류
    degree_ko = ['매우', '꽤', '상당히', '대단히', '조금', '약간', '아주', '몹시', '극히',
                 '다소', '충분히', '너무', '겨우', '간신히', '별로', '그다지', '얼마나',
                 '대체로', '꽤나', '그렇게', '이렇게', '저렇게', '더', '덜', '가장', '제일',
                 '한층', '한결', '훨씬', '많이']
    if any(k in ko for k in degree_ko):
        return 'CAT-01: 정도부사'

    time_freq_ko = ['가끔', '자주', '항상', '언제나', '요즘', '드디어', '마침내', '미리',
                    '곧', '이제', '아직', '벌써', '일찍', '늦게', '나중에', '금방', '방금',
                    '점차', '차차', '이따금', '종종', '늘', '줄곧', '수시로', '때때로',
                    '매번', '한번', '다시', '또', '여전히', '변함없이', '지금', '먼저', '우선']
    if any(k in ko for k in time_freq_ko):
        return 'CAT-06: 시간/빈도 부사'

    manner_ko = ['열심히', '천천히', '빨리', '서둘러', '조용히', '몰래', '살짝',
                 '대충', '꼼꼼히', '조심스럽게', '무심코', '억지로', '기꺼이',
                 '마지못해', '슬쩍', '번갈아', '잔뜩', '이윽고', '문득',
                 '무심결에', '그대로', '푹', '쭉', '확', '탁', '딱', '뚝',
                 '방긋', '생긋', '깜짝', '벌떡', '꾸벅', '흠뻑', '차분히']
    if any(k in ko for k in manner_ko):
        return 'CAT-09: 동작양태 부사'

    modality_ko = ['아마', '혹시', '확실히', '틀림없이', '분명히', '설마', '반드시', '꼭',
                   '물론', '당연히', '결코', '절대로', '전혀', '도저히', '과연', '역시',
                   '차라리', '만약', '만일', '어쨌든', '어차피', '아무래도', '어쩐지',
                   '마치', '이를테면', '다만', '단지', '그저', '마침', '우연히', '갑자기',
                   '순간', '일부러', '부디', '아무쪼록', '모름지기', '도대체', '대관절',
                   '정말로', '참으로', '한마디로', '한편', '사실', '실은', '실제로',
                   '어쩌면', '오히려', '오로지', '한결같이']
    if any(k in ko for k in modality_ko):
        return 'CAT-06b: 양태/확신 부사'

    # Layer 5: 비교/관계
    if any(k in ko for k in ['닮다', '비슷하', '다르다', '같다', '비교', '대조', '반대', '상대', '맞먹', '관련']):
        return 'CAT-02: 비교/관계'

    # Layer 6: 감정 vs 관계
    relation_ko = ['짝사랑', '사랑', '우정', '이별', '재회', '약속', '신뢰', '배신',
                   '화해', '갈등', '협력', '경쟁', '대립', '동료', '동갑', '서로',
                   '함께', '남녀공학', '상호', '교류', '연대', '유대', '혼인', '결혼', '이혼']
    if any(k in ko for k in relation_ko):
        return 'CAT-08: 관계/대인 추상어'

    emotion_ko = ['기쁨', '기쁘', '슬픔', '슬프', '분노', '화나', '불안', '걱정', '후회',
                  '감사', '질투', '부끄러', '수치', '자존심', '자신감', '용기', '두려움',
                  '공포', '희망', '절망', '만족', '불만', '외로움', '고독', '향수', '동정',
                  '동감', '흥분', '우울', '짜증', '허탈', '감동', '안심', '긴장', '초조',
                  '침착', '차분', '설렘', '기대', '안도', '놀라움', '경악', '당혹', '분함',
                  '기쁘다', '슬프다', '즐겁', '괴롭', '아쉬움', '아쉽', '후련']
    if any(k in ko for k in emotion_ko):
        return 'CAT-07: 감정/심리 추상어'

    # Layer 7: 명사류 하위분류
    time_noun_ko = ['아침', '저녁', '낮', '밤', '새벽', '오전', '오후', '정오', '자정',
                    '주말', '평일', '내일', '어제', '모레', '글피', '올해', '작년', '내년',
                    '이번', '지난', '다음', '과거', '미래', '현재', '당시', '최근', '이전',
                    '이후', '기간', '시간', '순간', '시기', '시대', '세기', '시절', '예전',
                    '옛날', '다다음', '재래', '연대', '황혼', '해질녘']
    if any(k in ko for k in time_noun_ko):
        return 'CAT-10: 시간대/기간 명사'

    logic_ko = ['원인', '결과', '영향', '효과', '관계', '근거', '증거', '논리', '이론',
                '원리', '법칙', '개념', '정의', '분류', '구조', '체계', '과정', '방법',
                '수단', '대책', '해결', '문제', '상황', '조건', '전제', '가설', '결론',
                '분석', '평가', '기준', '가치', '의미', '목적', '이유', '본질', '특징',
                '성질', '기능', '역할', '차이', '공통', '유형', '종류', '관점', '시점',
                '입장', '측면', '가능성', '필연', '우연', '인과']
    if any(k in ko for k in logic_ko):
        return 'CAT-12: 논리/학술 추상명사'

    comm_ko = ['말하다', '전하다', '알리다', '보고', '설명', '발표', '주장', '반론',
               '답변', '질문', '의논', '상담', '협의', '논의', '토론', '소개', '언급',
               '지적', '비판', '칭찬', '격려', '위로', '비난', '고백', '선언', '요청',
               '부탁', '명령', '지시', '제안', '권유', '충고', '경고', '허락', '험담',
               '악담', '욕설', '인사', '감사 인사', '사과', '변명', '해명']
    if any(k in ko for k in comm_ko):
        return 'CAT-11: 발화/커뮤니케이션'

    abs_adj_ko = ['중요', '필요', '적절', '충분', '불가능', '가능', '확실', '불확실',
                  '명확', '애매', '모호', '당연', '귀중', '소중', '사소', '긴급', '급한',
                  '곤란', '편리', '불편', '적당', '부적절', '정확', '미묘']
    if any(k in ko for k in abs_adj_ko):
        return 'CAT-13: 추상 형용사'

    attitude_ko = ['결심', '각오', '의지', '다짐', '노력', '끈기', '인내', '포기', '체념',
                   '신중', '대담', '겸손', '오만', '성실', '태도', '자세', '근면', '의욕', '열정',
                   '충실', '희생', '헌신']
    if any(k in ko for k in attitude_ko):
        return 'CAT-14: 의지/태도 표현'

    society_ko = ['법', '권리', '의무', '자유', '평등', '정의', '민주', '사회', '정치',
                  '경제', '문화', '교육', '종교', '전통', '관습', '제도', '정책', '규칙',
                  '규정', '법률', '헌법', '조약', '외교', '선거', '투표', '여론', '규범',
                  '사법', '행정', '입법']
    if any(k in ko for k in society_ko):
        return 'CAT-15: 사회/제도 추상명사'

    econ_ko = ['가격', '비용', '요금', '수입', '지출', '이익', '손해', '세금', '급여',
               '월급', '연봉', '예산', '저축', '투자', '할인', '판매', '구매', '거래',
               '수출', '무역', '수지', '적자', '흑자', '인플레', '물가', '환율']
    if any(k in ko for k in econ_ko):
        return 'CAT-16: 경제/거래 추상어'

    result_ko = ['성공', '실패', '달성', '완성', '완료', '종료', '시작', '착수', '도전',
                 '극복', '승리', '패배', '합격', '불합격', '채용', '해고', '취업', '퇴직',
                 '졸업', '입학', '결석', '출석']
    if any(k in ko for k in result_ko):
        return 'CAT-17: 결과/성취 추상어'

    counter_ko = ['권', '장', '개', '마리', '명', '번', '회', '벌', '대', '병', '잔',
                  '자루', '세는', '단위', '번째', '학점']
    if any(k in ko for k in counter_ko):
        return 'CAT-18: 수량사/단위'
    if re.search(r'〜|ずつ|counter|counting', kanji + kana + en):
        return 'CAT-18: 수량사/단위'

    quant_ko = ['정도', '한도', '한계', '수준', '범위', '비율', '분량', '용량', '최소',
                '최대', '평균', '합계', '전부', '모두', '일부', '절반', '전체', '나머지',
                '대부분', '소수', '다수', '각각', '각자', '각기', '여러', '다양']
    if any(k in ko for k in quant_ko):
        return 'CAT-19: 정도/양적 개념'

    direction_ko = ['위', '아래', '옆', '앞', '뒤', '안', '밖', '속', '겉', '사이',
                    '중간', '중심', '가운데', '주변', '근처', '부근', '맞은편', '건너편',
                    '방향', '쪽', '편', '이편', '저편', '도중', '반대쪽']
    if any(k in ko for k in direction_ko):
        return 'CAT-20: 방향/위치'

    if any(k in en for k in ['honorific', 'humble', 'polite']):
        return 'CAT-21: 경어/기능어'
    polite_ko = ['인사', '존경', '겸양', '예의', '실례', '사양', '정중']
    if any(k in ko for k in polite_ko):
        return 'CAT-21: 경어/기능어'

    change_ko = ['되다', '변하다', '바뀌다', '증가', '감소', '늘다', '줄다', '강해지다',
                 '약해지다', '악화', '향상', '저하', '발전', '쇠퇴', '진행', '진전']
    if any(k in ko for k in change_ko):
        return 'CAT-22: 상태변화 동사'

    cognition_ko = ['생각하', '깨닫', '이해하', '알다', '모르다', '믿다', '의심', '판단',
                    '추측', '예상', '기억', '잊다', '연상', '상상', '인식', '성찰', '반성',
                    '착각', '오해']
    if any(k in ko for k in cognition_ko):
        return 'CAT-23: 인지/사고 동사'

    # Layer 8: 미분류 잔여
    if cat in ['abstract_nouns', 'adverbs_functional', 'adjectives_states']:
        return 'UNCLASSIFIED: 미분류 추상어'

    return None


# ══════════════════════════════════════════════════════════════
# 2. 카테고리별 시각 메타포 매핑 (subject, metaphor)
# ══════════════════════════════════════════════════════════════

CATEGORY_VISUALS = {
    'CAT-01: 정도부사': (
        "An anime character standing beside a vertical intensity gauge",
        "A minimalist glowing gauge bar (empty-to-full level indicator), no numbers"
    ),
    'CAT-02: 비교/관계': (
        "Two small anime-style objects placed on either side of a balance scale",
        "A minimalist balance scale or equals/differs icon between the two objects"
    ),
    'CAT-03: 의문사': (
        "A young 2D anime person with head tilted in thought, curious gentle expression",
        "A few small subtle floating pastel question marks (?) around the head"
    ),
    'CAT-04: 지시어/대명사': (
        "A charming 2D anime character pointing with an index finger towards a target",
        "A subtle glowing target/highlight ring icon where the finger points"
    ),
    'CAT-05: 접속사/논리연결어': (
        "Two small contrasting minimal scene panels placed side by side",
        "A subtle connecting arrow or chain-link icon bridging the two panels"
    ),
    'CAT-06: 시간/빈도 부사': (
        "An anime character glancing at a minimal round clock",
        "A subtle repeating dot-sequence or sandglass icon indicating frequency"
    ),
    'CAT-06b: 양태/확신 부사': (
        "An anime character with a thought bubble above their head",
        "The thought bubble rendered as dotted outline (uncertain) or solid outline (certain), empty of text"
    ),
    'CAT-07: 감정/심리 추상어': (
        "An anime character with an expressive close-up face showing emotion",
        "A subtle glowing mood-aura icon (color-coded warmth) above the head"
    ),
    'CAT-08: 관계/대인 추상어': (
        "Two young anime characters standing side by side in a balanced, warm composition",
        "A soft glowing connecting line or shared warm light between the two characters"
    ),
    'CAT-09: 동작양태 부사': (
        "An anime character performing a simple action (walking or reaching)",
        "Motion lines around the character whose density/softness reflects the manner"
    ),
    'CAT-10: 시간대/기간 명사': (
        "An anime character in a minimal scene lit to match a specific time of day",
        "A small sun, moon, or calendar-page icon indicating the specific time period"
    ),
    'CAT-11: 발화/커뮤니케이션': (
        "Two anime characters facing each other in conversation",
        "A minimal empty speech-bubble icon showing direction of communication, no text inside"
    ),
    'CAT-12: 논리/학술 추상명사': (
        "An anime character looking thoughtfully at a small floating diagram",
        "A minimal flow-diagram icon with a few connected nodes and arrows"
    ),
    'CAT-13: 추상 형용사': (
        "An anime character reacting with an expression matching the quality described",
        "A minimal symbolic icon (checkmark, star, or wavy question line) above the character"
    ),
    'CAT-14: 의지/태도 표현': (
        "An anime character with a determined, resolute expression, fist gently clenched",
        "A small glowing spark or flame icon representing resolve"
    ),
    'CAT-15: 사회/제도 추상명사': (
        "An anime character standing near a simple symbolic institutional silhouette",
        "A minimal icon such as a scale-of-justice, ballot box, or flag silhouette"
    ),
    'CAT-16: 경제/거래 추상어': (
        "An anime character holding a simple coin or looking at a price tag",
        "A minimal coin, price-tag, or wallet icon"
    ),
    'CAT-17: 결과/성취 추상어': (
        "An anime character in a triumphant or disappointed pose",
        "A minimal trophy icon or a simple checkmark/X icon"
    ),
    'CAT-18: 수량사/단위': (
        "A small neat row of identical simple objects matching the counted item",
        "Minimal numbered block icons beside the row, no readable digits"
    ),
    'CAT-19: 정도/양적 개념': (
        "An anime character next to a measuring container filled partway",
        "A minimal measuring-cup or ruler icon showing a partial fill level"
    ),
    'CAT-20: 방향/위치': (
        "An anime character positioned relative to a single simple object",
        "A minimal directional arrow icon showing the spatial relation"
    ),
    'CAT-21: 경어/기능어': (
        "An anime character bowing politely with a gentle, respectful expression",
        "A subtle soft glow around the character indicating politeness/formality"
    ),
    'CAT-22: 상태변화 동사': (
        "A single object shown mid-transformation, split into a faint before/after silhouette",
        "A minimal transformation arrow icon connecting the before and after states"
    ),
    'CAT-23: 인지/사고 동사': (
        "An anime character with a thoughtful expression, hand resting on chin",
        "A minimal lightbulb or thought-bubble icon above the head, empty of text"
    ),
}

UNCLASSIFIED_SUBJECT = (
    "An anime character with a neutral thoughtful expression, "
    "holding a single simple symbolic object that abstractly represents the concept "
    "(NOT a literal depiction of the word itself)"
)
UNCLASSIFIED_METAPHOR = (
    "A minimal symbolic icon (arrow, spark, ring, or gear — chosen to abstractly evoke the "
    "concept), avoiding any literal narrative scene"
)


def build_v4_anime_prompt(subject_desc, metaphor_desc):
    return (
        f"A clean minimalist 1:1 Japanese anime illustration for a mobile flashcard app. "
        f"Modern Japanese anime art style with clean line art, charming 2D anime character design, soft warm pastel colors. "
        f"- Subject: {subject_desc}. "
        f"- Visual metaphor: {metaphor_desc}. "
        f"- Background: Extremely minimal plain soft pastel background, NO buildings, NO scenery, NO clouds, NO complex environment. "
        f"- Style: Clean 2D anime graphic, smooth borders, minimal UI card design. "
        f"- Constraint: NO text, NO Korean, NO Japanese, NO written words."
    )


def build_prompt_for_word(w: dict):
    kanji = w.get('kanji', '')
    kana = w.get('hiragana', '')
    ko = w.get('korean', '')

    category = classify_priority_tree(w)

    if category is None:
        subject = f"An anime character interacting with {ko} ({kanji if kanji else kana})"
        metaphor = f"Clear central visual focus on {ko}"
        return build_v4_anime_prompt(subject, metaphor), 'CONCRETE', False

    if category == 'UNCLASSIFIED: 미분류 추상어':
        return build_v4_anime_prompt(UNCLASSIFIED_SUBJECT, UNCLASSIFIED_METAPHOR), category, True

    subject, metaphor = CATEGORY_VISUALS[category]
    return build_v4_anime_prompt(subject, metaphor), category, False


# ══════════════════════════════════════════════════════════════
# 3. 실행
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true',
                         help="캐시 파일에 쓰지 않고 통계만 출력")
    args = parser.parse_args()

    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master = json.load(f)

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    else:
        cache = {}

    from collections import Counter, OrderedDict
    stats = Counter()
    review_needed = []
    count = 0

    for cat_name, word_list in master.items():
        for w in word_list:
            w['_category'] = cat_name
            wid = w.get('id', '')
            kanji = w.get('kanji', '')
            kana = w.get('hiragana', '')

            prompt, category, needs_review = build_prompt_for_word(w)
            stats[category] += 1

            if needs_review:
                review_needed.append({
                    'id': wid,
                    'kanji': kanji,
                    'kana': kana,
                    'korean': w.get('korean', ''),
                })

            if not args.dry_run:
                cache[wid] = prompt
                if kanji:
                    cache[kanji] = prompt
                if kana:
                    cache[kana] = prompt

            count += 1

    if not args.dry_run:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print(f"💾 캐시 파일 갱신 완료: {CACHE_FILE}")
    else:
        print("🔍 --dry-run 모드 — 캐시 파일은 변경하지 않았습니다.")

    with open(UNCLASSIFIED_REPORT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'kanji', 'kana', 'korean'])
        writer.writeheader()
        writer.writerows(review_needed)

    stats_out = OrderedDict(sorted(stats.items(), key=lambda x: -x[1]))
    with open(STATS_REPORT, 'w', encoding='utf-8') as f:
        json.dump(stats_out, f, ensure_ascii=False, indent=2)

    print(f"\n총 {count}개 단어 처리 완료.\n")
    print(f"{'카테고리':40s} {'개수':>6s}")
    print("-" * 50)
    for k, v in stats_out.items():
        flag = "⚠️ " if k == 'UNCLASSIFIED: 미분류 추상어' else "  "
        print(f"{flag}{k:38s} {v:6d}")

    generic_before = 8221
    generic_after = stats.get('CONCRETE', 0) + stats.get('UNCLASSIFIED: 미분류 추상어', 0)
    print(f"\n전용 시각 메타포 적용: {count - generic_after}개 (V4 대비 {count - generic_after - (count - generic_before)}개 증가)")
    print(f"여전히 범용/미분류(수동 검토 필요): {stats.get('UNCLASSIFIED: 미분류 추상어', 0)}개")
    print(f"  → 상세 리스트: {UNCLASSIFIED_REPORT}")


if __name__ == '__main__':
    main()
