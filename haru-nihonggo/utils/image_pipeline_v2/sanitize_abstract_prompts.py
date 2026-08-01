#!/usr/bin/env python3
"""
High Risk 추상어 218개 프롬프트 정제 및 11대 카테고리 Visual Hero 일괄 적용 스크립트 (v2 - 정밀 서브스트링 보정)
===================================================================================
- 서브스트링 오매칭 보정: '스튜어디스'의 '어디' 오매칭 방지
- expanded_tags_cache.json 복구 후 정밀 갱신
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

overshadowing_keywords = [
    'cherry blossom', 'railway platform', 'train station', 'fireplace',
    'mailbox filled with letters', 'scarf', 'porch shade', 'falling leaves'
]

VISUAL_HERO_TEMPLATES = {
    '의문사': "glowing big question mark float above, 1boy pointing at mysterious silhouette box, curious expression, simple neutral soft backdrop, studio ghibli style, warm color palette",
    '지시어': "pointing index finger, target highlight ring, clear focus indicator, simple neutral backdrop, studio ghibli style, warm color palette",
    '접속사': "2-panel split frame contrast, transition arrow icon, simple neutral background, studio ghibli style, warm color palette",
    '정도부사': "glowing level gauge scale bar contrast, clear level indicator, simple soft backdrop, studio ghibli style, warm color palette",
    '시간부사': "minimal clock timeline gauge, subtle sandglass motif, simple neutral background, studio ghibli style, warm color palette",
    '관계': "symmetric two characters interaction, balanced composition, simple soft backdrop, studio ghibli style, warm color palette",
    '감정': "close up face emotional expression focus, minimal simple backdrop, studio ghibli style, warm color palette",
    '기본추상': "floating central concept metaphor symbol, minimal clean background, simple soft backdrop, studio ghibli style, warm color palette"
}

interrogative_exact_korean = ['무엇', '누구', '어디', '언제', '왜', '어느', '어떻게', '몇', '어째서', '어느쪽', '어느 것']

sanitized_count = 0
sanitized_log = []

for w in all_words:
    w_id = w.get('id', '')
    kanji = w.get('kanji', '')
    kana = w.get('hiragana', '')
    ko = w.get('korean', '')
    cat = w.get('_cat', '')
    
    prompt = cache.get(w_id, cache.get(kanji, ''))
    if not prompt:
        continue
        
    prompt_lower = prompt.lower()
    has_overshadowing = any(kw in prompt_lower for kw in overshadowing_keywords)
    
    # 의문사 엄격 매칭 (단어경계/완전일치)
    is_interrogative = any(re.search(r'(?:^|[;,/\s・~～〜()（）])' + re.escape(ik) + r'(?:$|[;,/\s・~～〜()（）])', ko) for ik in interrogative_exact_korean) or kanji.startswith('何') or kanji.startswith('誰')
    
    if is_interrogative or (cat in ['abstract_nouns', 'adverbs_functional'] and has_overshadowing):
        old_prompt = prompt
        
        if is_interrogative:
            new_prompt = VISUAL_HERO_TEMPLATES['의문사']
        elif any(k in ko for k in ['이것', '저것', '그것', '여기', '거기', '저기']):
            new_prompt = VISUAL_HERO_TEMPLATES['지시어']
        elif any(k in ko for k in ['하지만', '그러나', '그래서', '그럼']):
            new_prompt = VISUAL_HERO_TEMPLATES['접속사']
        elif any(k in ko for k in ['매우', '조금', '꽤', '상당히']):
            new_prompt = VISUAL_HERO_TEMPLATES['정도부사']
        elif any(k in ko for k in ['가끔', '자주', '요즘', '드디어']):
            new_prompt = VISUAL_HERO_TEMPLATES['시간부사']
        elif any(k in ko for k in ['서로', '함께', '동갑', '남녀공학']):
            new_prompt = VISUAL_HERO_TEMPLATES['관계']
        elif any(k in ko for k in ['기쁨', '슬픔', '걱정', '짝사랑']):
            new_prompt = VISUAL_HERO_TEMPLATES['감정']
        else:
            new_prompt = VISUAL_HERO_TEMPLATES['기본추상']
            
        cache[w_id] = new_prompt
        if kanji:
            cache[kanji] = new_prompt
            
        sanitized_count += 1
        sanitized_log.append({
            'id': w_id,
            'kanji': kanji,
            'korean': ko,
            'old': old_prompt[:90],
            'new': new_prompt[:90]
        })

# 캐시 파일 저장
with open(CACHE_FILE, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"✅ 총 {sanitized_count}개 High Risk 추상어 프롬프트 정밀 정제 완료!")
print(f"💾 캐시 파일 업데이트: {CACHE_FILE}")

# 대표 샘플 출력
print("\n📋 정제된 대표 10개 샘플 Diff:")
for item in sanitized_log[:10]:
    print(f"[{item['id']}] {item['kanji']} ({item['korean']})")
    print(f"  ❌ Old: {item['old']}...")
    print(f"  ✨ New: {item['new']}...")
    print("-" * 50)
