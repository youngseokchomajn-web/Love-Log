#!/usr/bin/env python3
"""
플랫 벡터 지브리 앱 카드 5단 구조 프롬프트 일괄 적용 및 백치 자동화 스크립트
========================================================================
- 사용자 Gemini 테스트 성공 템플릿 100% 반영:
  1. Style: A clean minimalist 1:1 flat vector illustration for a mobile flashcard app. Studio Ghibli inspired character art style with clean line art and flat warm colors.
  2. Subject: 단어별 인물/오브젝트
  3. Visual metaphor: 단어별 상징 기호 (예: floating question marks)
  4. Background: Extremely minimal plain soft pastel background, NO buildings, NO scenery, NO clouds, NO complex environment.
  5. Style & Constraint: Flat 2D vector graphic, clean borders, minimal UI card design. NO text, NO Korean, NO Japanese, NO written words in the image.
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

all_words = []
for cat_name, word_list in master.items():
    for w in word_list:
        w['_cat'] = cat_name
        all_words.append(w)

def build_flat_vector_prompt(subject_desc, metaphor_desc):
    return (
        f"A clean minimalist 1:1 flat vector illustration for a mobile flashcard app. "
        f"Studio Ghibli inspired character art style with clean line art and flat warm colors. "
        f"- Subject: {subject_desc}. "
        f"- Visual metaphor: {metaphor_desc}. "
        f"- Background: Extremely minimal plain soft pastel background, NO buildings, NO scenery, NO clouds, NO complex environment. "
        f"- Style: Flat 2D vector graphic, clean borders, minimal UI card design. "
        f"- Constraint: NO text, NO Korean, NO Japanese, NO written words in the image."
    )

interrogative_exact_korean = ['무엇', '누구', '어디', '언제', '왜', '어느', '어떻게', '몇', '어째서', '어느쪽', '어느 것']

count = 0
for w in all_words:
    wid = w.get('id', '')
    kanji = w.get('kanji', '')
    kana = w.get('hiragana', '')
    ko = w.get('korean', '')
    cat = w.get('_cat', '')
    
    is_interrogative = any(re.search(r'(?:^|[;,/\s・~～〜()（）])' + re.escape(ik) + r'(?:$|[;,/\s・~～〜()（）])', ko) for ik in interrogative_exact_korean) or kanji.startswith('何') or kanji.startswith('誰')
    
    if is_interrogative or cat in ['abstract_nouns', 'adverbs_functional', 'adjectives_states']:
        if is_interrogative:
            subject = "A young person with head tilted in thought, curious gentle expression"
            metaphor = "A few small subtle floating question marks (?) around head"
        elif any(k in ko for k in ['이것', '저것', '그것', '여기', '거기', '저기']):
            subject = "A young character pointing with index finger towards target"
            metaphor = "Subtle glowing target highlight ring"
        elif any(k in ko for k in ['하지만', '그러나', '그래서', '그럼']):
            subject = "Two contrasting side-by-side elements"
            metaphor = "A subtle transition arrow symbol"
        elif any(k in ko for k in ['매우', '조금', '꽤', '상당히']):
            subject = "A character observing a level gauge scale"
            metaphor = "A minimalist level indicator bar"
        elif any(k in ko for k in ['가끔', '자주', '요즘', '드디어']):
            subject = "A character looking at a minimal clock timeline"
            metaphor = "A subtle sandglass hour-marker icon"
        elif any(k in ko for k in ['몇 개', '몇 살', '수량']):
            subject = "Three bright red juicy apples lined up on table"
            metaphor = "Minimalist wooden blocks with numbers 1 2 3"
        elif any(k in ko for k in ['서로', '함께', '동갑', '남녀공학']):
            subject = "Two young friends standing side by side in balanced composition"
            metaphor = "Warm caring friendly interaction"
        elif any(k in ko for k in ['기쁨', '슬픔', '걱정', '짝사랑']):
            subject = "A character with expressive emotion close-up face"
            metaphor = "Subtle glowing mood aura icon"
        else:
            subject = "A young Ghibli character expressing central concept"
            metaphor = "A floating central concept metaphor symbol"
            
        new_prompt = build_flat_vector_prompt(subject, metaphor)
        cache[wid] = new_prompt
        if kanji:
            cache[kanji] = new_prompt
        count += 1

with open(CACHE_FILE, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"✅ 총 {count}개 추상/기능어 프롬프트 5단 플랫 벡터 구조 적용 완료!")
