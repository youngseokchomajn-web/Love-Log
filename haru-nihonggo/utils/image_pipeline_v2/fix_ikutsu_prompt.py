#!/usr/bin/env python3
"""
'いくつ (몇 개/몇 살)' 프롬프트 끔찍함/기괴함 소거 및 밝은 숫자/사과 카운팅 재설계 스크립트
"""

import json
import os

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo/utils/image_pipeline_v2"
CACHE_FILE = os.path.join(BASE_DIR, "expanded_tags_cache.json")

with open(CACHE_FILE, 'r', encoding='utf-8') as f:
    cache = json.load(f)

# 기괴한 흑화 유령 태그 100% 제거 -> 귀여운 숫자 장난감 블록 & 붉은 사과 3개 카운팅으로 교체
new_prompt = "three bright red juicy apples lined up on a wooden table, wooden toy blocks with numbers 1 2 3, bright cheerful lighting, simple soft pastel backdrop, studio ghibli style, warm cozy atmosphere"

cache['n5_いくつ'] = new_prompt
cache['いくつ'] = new_prompt

with open(CACHE_FILE, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print("✅ 'いくつ(몇 개/몇 살)' 프롬프트 재설계 완료!")
print("  신규 프롬프트:", new_prompt)
