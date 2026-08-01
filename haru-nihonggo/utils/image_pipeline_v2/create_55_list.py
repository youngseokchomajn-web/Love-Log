#!/usr/bin/env python3
"""
최우선 재렌더링 대상 55개 단어 ID 목록 생성 스크립트
"""

import json
import os
import re

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo/utils/image_pipeline_v2"
MASTER_FILE = os.path.join(BASE_DIR, "word_categories_all.json")
CACHE_FILE = os.path.join(BASE_DIR, "expanded_tags_cache.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "target_55_words.json")

with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    master = json.load(f)

with open(CACHE_FILE, 'r', encoding='utf-8') as f:
    cache = json.load(f)

all_words = []
for cat_name, word_list in master.items():
    for w in word_list:
        w['_cat'] = cat_name
        all_words.append(w)

interrogative_exact_korean = ['무엇', '누구', '어디', '언제', '왜', '어느', '어떻게', '몇', '어째서', '어느쪽', '어느 것']

target_55 = []

for w in all_words:
    w_id = w.get('id', '')
    kanji = w.get('kanji', '')
    kana = w.get('hiragana', '')
    ko = w.get('korean', '')
    
    is_interrogative = any(re.search(r'(?:^|[;,/\s・~～〜()（）])' + re.escape(ik) + r'(?:$|[;,/\s・~～〜()（）])', ko) for ik in interrogative_exact_korean) or kanji.startswith('何') or kanji.startswith('誰')
    
    if is_interrogative:
        target_55.append({
            'id': w_id,
            'kanji': kanji,
            'kana': kana,
            'korean': ko,
            'prompt': cache.get(w_id, cache.get(kanji, ''))
        })

target_55 = target_55[:55]

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(target_55, f, ensure_ascii=False, indent=2)

print(f"✅ 최우선 55개 단어 목록 생성 완료 ({len(target_55)}개): {OUTPUT_FILE}")

# ID 목록을 반점으로 연결
id_list_str = ",".join([w['id'] for w in target_55])
print(f"ID 파라미터: {id_list_str[:120]}...")
