#!/usr/bin/env python3
"""
Vertex AI ADC 기반 어휘 플래시카드 V5 초고속 멀티 리전(Multi-Region) 병렬 가속 파이프라인
=======================================================================================
- 프로젝트: project-8598242e-9cd6-4c63-9e8
- 무료 평가판 크레딧(₩435,523) 100% 자동 차감 (추가 카드 비용 0원)
- 모델: gemini-2.5-flash-image (Vertex AI API)
- 멀티 리전 분산: us-central1, us-east4, us-west1, europe-west1, asia-east1 (Rate Limit 5배 확장)
"""

import os
import sys
import json
import time
import re
import unicodedata
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"
CACHE_FILE = os.path.join(BASE_DIR, "utils/image_pipeline_v2/expanded_tags_cache.json")
MASTER_FILE = os.path.join(BASE_DIR, "utils/image_pipeline_v2/word_categories_all.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "assets/images/words_v4_gemini")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROJECT_ID = 'project-8598242e-9cd6-4c63-9e8'
LOCATIONS = ['us-central1', 'us-east4', 'us-west1', 'europe-west1', 'asia-east1']

with open(CACHE_FILE, 'r', encoding='utf-8') as f:
    cache = json.load(f)

with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    master = json.load(f)

def clean_filename(text):
    cleaned = re.sub(r'[\s/,;\?:\*\"<>\|\\\.\(\)\[\]\{\}〜~]', '', text)
    return unicodedata.normalize('NFC', cleaned)

# 미생성 어휘 탐색
missing_items = []
for cat_name, word_list in master.items():
    for w in word_list:
        wid = w.get('id', '')
        kanji = w.get('kanji', '')
        kana = w.get('hiragana', '')
        ko = w.get('korean', '')
        level = w.get('level', 'n5')

        display_name = kanji if kanji else kana
        filename = f"{level}_{clean_filename(display_name)}_{clean_filename(ko)}_v4.jpg"
        save_path = os.path.join(OUTPUT_DIR, filename)

        if not (os.path.exists(save_path) and os.path.getsize(save_path) > 5000):
            prompt = cache.get(wid, cache.get(kanji, cache.get(kana, None)))
            if prompt:
                missing_items.append({
                    'w': w,
                    'wid': wid,
                    'display': display_name,
                    'ko': ko,
                    'filename': filename,
                    'save_path': save_path,
                    'prompt': prompt
                })

print(f"📊 [Multi-Region Pipeline] 미생성 남은 어휘: {len(missing_items)}개", flush=True)

def render_worker(item):
    save_path = item['save_path']
    filename = item['filename']
    display_name = item['display']
    ko = item['ko']
    prompt = item['prompt']

    attempts = 0
    while attempts < 5:
        loc = random.choice(LOCATIONS)
        try:
            client = genai.Client(
                vertexai=True,
                project=PROJECT_ID,
                location=loc
            )
            res = client.models.generate_content(
                model='gemini-2.5-flash-image',
                contents=prompt
            )
            if res and res.candidates:
                for candidate in res.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                with open(save_path, 'wb') as f_out:
                                    f_out.write(part.inline_data.data)
                                return (True, filename)
            attempts += 1
            time.sleep(0.3)
        except Exception as e:
            err_msg = str(e)
            if '429' in err_msg or 'quota' in err_msg.lower():
                time.sleep(0.5)
            else:
                attempts += 1
                time.sleep(0.3)

    return (False, f"Failed: {filename}")

def main():
    workers = 10
    print(f"🚀 Vertex AI 5개 멀티 리전 분산 초고속 파이프라인 가동! ({workers}개 스레드)", flush=True)

    start_time = time.time()
    completed = 0
    total = len(missing_items)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(render_worker, item): item for item in missing_items}
        for f in as_completed(futures):
            success, msg = f.result()
            if success:
                completed += 1
                elapsed = time.time() - start_time
                speed = (completed / elapsed) * 60 if elapsed > 0 else 0
                eta_minutes = ((total - completed) / (completed / elapsed)) / 60 if completed > 0 else 0
                if completed % 10 == 0 or completed == total:
                    print(f"⚡ [{completed}/{total}] ({completed/total*100:.1f}%) | 속도: 분당 {speed:.1f}개 | 남은시간: {eta_minutes:.1f}분 완료!", flush=True)

    print(f"\n🎉 전체 {completed}개 고화질 V5 이미지 수집 완결!", flush=True)

if __name__ == "__main__":
    main()
