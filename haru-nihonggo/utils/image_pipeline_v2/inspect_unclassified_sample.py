#!/usr/bin/env python3
"""
미분류 2,491개 샘플 조사 - 실제로 프롬프트 수정이 필요한 유형 vs 구체적 단어
"""

import json
import re
from collections import defaultdict

with open('utils/image_pipeline_v2/word_categories_all.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

with open('utils/image_pipeline_v2/expanded_tags_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

all_words = []
for cat_name, word_list in categories.items():
    for w in word_list:
        w['_category'] = cat_name
        all_words.append(w)

# 기존 분류 로직 (v2와 동일)을 적용하여 미분류만 추출
# ... (간단히 _category만 확인)

abstract_cats = ['abstract_nouns', 'adverbs_functional']
abstract_words = [w for w in all_words if w['_category'] in abstract_cats]

print(f"추상/기능어 카테고리 총: {len(abstract_words)}")

# 무작위 100개 샘플링하여 직접 확인
import random
random.seed(42)
sample = random.sample(abstract_words, min(100, len(abstract_words)))

# 프롬프트와 함께 출력
for i, w in enumerate(sample[:50]):
    w_id = w.get('id','')
    kanji = w.get('kanji','')
    kana = w.get('hiragana','')
    ko = w.get('korean','')
    en = w.get('english','')
    prompt = cache.get(w_id, cache.get(kanji, 'N/A'))
    
    # 단어가 실제로 구체적인지 판단 힌트
    # 한자가 구체적 사물/동작을 나타내면 OK
    print(f"[{i+1}] {w_id} | {kanji}({kana}) = {ko} [{en}]")
    print(f"   CAT: {w['_category']}")
    if prompt != 'N/A':
        print(f"   PROMPT: {prompt[:130]}")
    print()
