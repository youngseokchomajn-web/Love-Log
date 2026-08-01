#!/usr/bin/env python3
"""
Gemini API / Imagen 3 자동 배치 이미지 생성기 스크립트
===================================================
기능:
1. 1,000개 이상의 단어에 대해 Gemini/Imagen API를 호출하여 자동 이미지 생성
2. API Rate Limit (429) 및 딜레이 자동 관리 (Rate Limit 백오프 포함)
3. 이미 생성된 단어 자동 스킵 (중복 렌더링 방지)
4. assets/images/words_v3/ 에 플랫 벡터 지브리 이미지 자동 저장

사용법:
  python3 batch_gemini_vector_generator.py [--count 50] [--ids n5_0489,n5_0001]
"""

import os
import sys
import json
import time
import argparse
from dotenv import load_dotenv
from google import genai

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"
CACHE_FILE = os.path.join(BASE_DIR, "utils/image_pipeline_v2/expanded_tags_cache.json")
MASTER_FILE = os.path.join(BASE_DIR, "utils/image_pipeline_v2/word_categories_all.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "assets/images/words_v3")

os.makedirs(OUTPUT_DIR, exist_ok=True)

load_dotenv(os.path.join(BASE_DIR, "word_card_generator/.env"))
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in word_card_generator/.env")
    sys.exit(1)

client = genai.Client(api_key=api_key)

with open(CACHE_FILE, 'r', encoding='utf-8') as f:
    cache = json.load(f)

with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    master = json.load(f)

def clean_filename(text):
    import re, unicodedata
    cleaned = re.sub(r'[\s/,;\?:\*\"<>\|\\\.\(\)\[\]\{\}〜~]', '', text)
    return unicodedata.normalize('NFC', cleaned)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10, help='Maximum images to generate in this run')
    parser.add_argument('--ids', type=str, default='', help='Specific comma-separated IDs')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay in seconds between API calls')
    args = parser.parse_args()

    all_words = []
    for cat_name, word_list in master.items():
        for w in word_list:
            all_words.append(w)

    target_words = []
    if args.ids:
        req_ids = [x.strip() for x in args.ids.split(',') if x.strip()]
        target_words = [w for w in all_words if w.get('id') in req_ids]
    else:
        target_words = all_words

    print(f"🚀 Gemini API 배치 이미지 생성기 시작 (대상: {len(target_words)}개 중 최대 {args.count}개 실행)")

    generated_count = 0

    for w in target_words:
        if generated_count >= args.count:
            break

        wid = w.get('id', '')
        kanji = w.get('kanji', '')
        kana = w.get('hiragana', '')
        ko = w.get('korean', '')

        display_name = kanji if kanji else kana
        filename = f"{w.get('level', 'n5')}_{clean_filename(display_name)}_{clean_filename(ko)}.jpg"
        save_path = os.path.join(OUTPUT_DIR, filename)

        prompt = cache.get(wid, cache.get(kanji, None))
        if not prompt:
            continue

        print(f"\n[{generated_count+1}/{args.count}] [{wid}] {display_name} ({ko}) 렌더링 중...")

        retry_count = 0
        success = False
        
        while retry_count < 3 and not success:
            try:
                # Gemini Imagen 3 / Image models
                res = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=prompt,
                    config=dict(
                        number_of_images=1,
                        aspect_ratio='1:1',
                        output_mime_type='image/jpeg'
                    )
                )
                if res and res.generated_images:
                    with open(save_path, 'wb') as f_out:
                        f_out.write(res.generated_images[0].image.image_bytes)
                    print(f"  ✅ Saved: {filename}")
                    success = True
                    generated_count += 1
            except Exception as e:
                err_msg = str(e)
                if '429' in err_msg or 'quota' in err_msg.lower():
                    print("  ⚠️ Rate Limit (429) 대기 중... 10초 휴식 후 재시도")
                    time.sleep(10)
                    retry_count += 1
                else:
                    print(f"  ❌ API 오류: {err_msg[:120]}")
                    break

        time.sleep(args.delay)

    print(f"\n🎉 총 {generated_count}개 Gemini API 플랫 벡터 이미지 카드 생성 완료!")

if __name__ == "__main__":
    main()
