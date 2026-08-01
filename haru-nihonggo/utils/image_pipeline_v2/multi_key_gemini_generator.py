#!/usr/bin/env python3
"""
멀티 계정(API Key Rotation) Gemini 무료 API 자동 생성기 스크립트
============================================================
- 여러 구글 계정의 GEMINI_API_KEY를 순차적/자동 회전(Rotation)하여
  하루 1,500개 한도를 넘겨 하루 3,000~4,500개 이상 초고속 초대량 렌더링
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
OUTPUT_DIR = os.path.join(BASE_DIR, "assets/images/words_v4_gemini")
os.makedirs(OUTPUT_DIR, exist_ok=True)

load_dotenv(os.path.join(BASE_DIR, "word_card_generator/.env"))

# 키 목록 수집 (GEMINI_API_KEY, GEMINI_API_KEY_1, GEMINI_API_KEY_2 ...)
keys = []
for k, v in os.environ.items():
    if k.startswith("GEMINI_API_KEY") and v.strip():
        keys.append(v.strip())

# 중복 제거
keys = list(dict.fromkeys(keys))

if not keys:
    print("❌ Error: 등록된 GEMINI_API_KEY가 없습니다. word_card_generator/.env 파일에 키를 추가해 주세요.")
    sys.exit(1)

print(f"🔑 총 {len(keys)}개의 구글 계정 API 키가 감지되었습니다.")

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
    parser.add_argument('--count', type=int, default=3000, help='Maximum images to generate in this run')
    parser.add_argument('--delay', type=float, default=4.0, help='Delay between API calls in seconds')
    args = parser.parse_args()

    all_words = []
    for cat_name, word_list in master.items():
        for w in word_list:
            all_words.append(w)

    current_key_idx = 0

    def get_client():
        nonlocal current_key_idx
        k = keys[current_key_idx]
        print(f"🔑 [계정 #{current_key_idx+1}/{len(keys)}] API 키 사용 중: {k[:10]}...")
        return genai.Client(api_key=k)

    client = get_client()

    generated_count = 0
    skipped_count = 0

    for w in all_words:
        if generated_count >= args.count:
            break

        wid = w.get('id', '')
        kanji = w.get('kanji', '')
        kana = w.get('hiragana', '')
        ko = w.get('korean', '')

        display_name = kanji if kanji else kana
        filename = f"{w.get('level', 'n5')}_{clean_filename(display_name)}_{clean_filename(ko)}_v4.jpg"
        save_path = os.path.join(OUTPUT_DIR, filename)

        # 이미 존재하는 파일은 자동 스킵 (중복 렌더링 방지)
        if os.path.exists(save_path) and os.path.getsize(save_path) > 5000:
            skipped_count += 1
            continue

        prompt = cache.get(wid, cache.get(kanji, cache.get(kana, None)))
        if not prompt:
            continue

        print(f"[{generated_count+1}/{args.count}] [{wid}] {display_name} ({ko}) 렌더링 중...")

        success = False
        attempts = 0

        while attempts < len(keys) and not success:
            try:
                res = client.models.generate_content(
                    model='gemini-2.5-flash-image',
                    contents=prompt
                )
                for candidate in res.candidates:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            with open(save_path, 'wb') as f_out:
                                f_out.write(part.inline_data.data)
                            print(f"  ✅ 저장 완료: {filename}")
                            success = True
                            generated_count += 1
                            break
                if success:
                    break
            except Exception as e:
                err_msg = str(e)
                if '429' in err_msg or 'quota' in err_msg.lower():
                    print(f"  ⚠️ 계정 #{current_key_idx+1} 일일 한도 소진. 다음 계정으로 전환합니다...")
                    current_key_idx = (current_key_idx + 1) % len(keys)
                    client = get_client()
                    attempts += 1
                else:
                    print(f"  ❌ 오류: {err_msg[:100]}")
                    break

        time.sleep(args.delay)

    print(f"\n🎉 총 {generated_count}개 새로운 이미지 생성 완료! (스킵: {skipped_count}개)")

if __name__ == "__main__":
    main()
