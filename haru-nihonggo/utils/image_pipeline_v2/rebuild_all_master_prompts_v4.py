#!/usr/bin/env python3
"""
8,424개 전체 일본어 단어 프롬프트 100% 재작성 및 마스터 캐시 업데이트 스크립트 (V4)
=============================================================================
교훈 종합 반영:
1. Tone & Manner: Modern Japanese anime art style with clean line art, charming 2D anime character design, soft warm pastel colors
2. Anti-Overshadowing: Extremely minimal plain soft pastel background, NO buildings, NO scenery, NO clouds, NO complex environment
3. Visual Hero Metaphor: 의문사/지시어/접속사/부사/수량/상태별 명확한 기호 분리
4. Text Removal: NO text, NO Korean, NO Japanese, NO written words
5. 5단 표준 프롬프트 아키텍처 100% 통일
"""

import json
import os
import re

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo/utils/image_pipeline_v2"
CACHE_FILE = os.path.join(BASE_DIR, "expanded_tags_cache.json")
MASTER_FILE = os.path.join(BASE_DIR, "word_categories_all.json")

with open(CACHE_FILE, 'r', encoding='utf-8') as f:
    cache = json.load(f)

with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    master = json.load(f)

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

interrogative_exact_korean = ['무엇', '누구', '어디', '언제', '왜', '어느', '어떻게', '몇', '어째서', '어느쪽', '어느 것']

count = 0
for cat_name, word_list in master.items():
    for w in word_list:
        wid = w.get('id', '')
        kanji = w.get('kanji', '')
        kana = w.get('hiragana', '')
        ko = w.get('korean', '')
        
        is_interrogative = any(re.search(r'(?:^|[;,/\s・~～〜()（）])' + re.escape(ik) + r'(?:$|[;,/\s・~～〜()（）])', ko) for ik in interrogative_exact_korean) or kanji.startswith('何') or kanji.startswith('誰')
        
        if is_interrogative:
            subject = "A young 2D anime person with head tilted in thought, curious gentle expression, looking up slightly"
            metaphor = "A few small subtle floating pastel question marks (?) around head"
        elif any(k in ko for k in ['이것', '저것', '그것', '여기', '거기', '저기']):
            subject = "A charming 2D anime character pointing with index finger towards target"
            metaphor = "Subtle glowing target highlight ring icon"
        elif any(k in ko for k in ['하지만', '그러나', '그래서', '그럼']):
            subject = "Two contrasting side-by-side anime elements"
            metaphor = "A subtle transition arrow symbol"
        elif any(k in ko for k in ['매우', '조금', '꽤', '상당히']):
            subject = "An anime character observing a level gauge scale"
            metaphor = "A minimalist level indicator bar"
        elif any(k in ko for k in ['가끔', '자주', '요즘', '드디어']):
            subject = "An anime character looking at a minimal clock timeline"
            metaphor = "A subtle sandglass hour-marker icon"
        elif any(k in ko for k in ['몇 개', '몇 살', '수량', '하나', '둘']):
            subject = "Three bright red juicy apples lined up neatly on a table"
            metaphor = "Minimalist wooden blocks with numbers 1 2 3"
        elif any(k in ko for k in ['서로', '함께', '동갑', '친구']):
            subject = "Two young anime friends standing side by side in balanced composition"
            metaphor = "Warm caring friendly interaction"
        elif any(k in ko for k in ['기쁨', '슬픔', '걱정', '짝사랑', '행복']):
            subject = "An anime character with expressive emotion face close-up"
            metaphor = "Subtle glowing mood aura icon"
        else:
            # Concrete nouns / verbs / general words
            en_desc = f"A charming 2D anime illustration representing {ko} ({kanji if kanji else kana})"
            subject = f"An anime character interacting with {ko} ({kanji if kanji else kana})"
            metaphor = f"Clear central visual focus on {ko}"

        v4_prompt = build_v4_anime_prompt(subject, metaphor)
        
        cache[wid] = v4_prompt
        if kanji:
            cache[kanji] = v4_prompt
        if kana:
            cache[kana] = v4_prompt
            
        count += 1

with open(CACHE_FILE, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"🎉 총 {count}개 단어 전체 V4 일본 애니메이션 5단 프롬프트 전면 재작성 및 캐시 반영 완료!")
