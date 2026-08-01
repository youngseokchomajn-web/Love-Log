#!/usr/bin/env python3
"""
Gemini 무료 API를 이용한 1장 테스트 렌더링 스크립트
==================================================
- 저장 경로: assets/images/words_v4_gemini/ (기존 words_v3 보존)
- 모델: gemini-2.5-flash-image / gemini-3.1-flash-image
"""

import os
import sys
import json
import time
from dotenv import load_dotenv
from google import genai

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"
OUTPUT_DIR = os.path.join(BASE_DIR, "assets/images/words_v4_gemini")
os.makedirs(OUTPUT_DIR, exist_ok=True)

load_dotenv(os.path.join(BASE_DIR, "word_card_generator/.env"))
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found!")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# 테스트용 단어: 何となく (왠지/어쩐지) or 何 (무엇)
word_id = "n5_0489" # 또는 n1_何となく
prompt_text = (
    "A clean minimalist 1:1 flat vector illustration for a mobile flashcard app. "
    "Studio Ghibli inspired character art style with clean line art and flat warm colors. "
    "- Subject: A young Ghibli girl with her head tilted in thought, curious gentle expression, looking up slightly. "
    "- Visual metaphor: A few small subtle floating question marks (?) around her head. "
    "- Background: Extremely minimal plain soft pastel background, NO buildings, NO scenery, NO clouds, NO complex environment. "
    "- Style: Flat 2D vector graphic, clean borders, minimal UI card design. "
    "- Constraint: NO text, NO Korean, NO Japanese, NO written words in the image."
)

print("🚀 Gemini 무료 API로 1개 테스트 이미지 렌더링 시도 중...")

models = ['gemini-2.5-flash-image', 'gemini-3.1-flash-image', 'gemini-3-pro-image']

save_path = os.path.join(OUTPUT_DIR, "n5_何_무엇_v4.jpg")

success = False
for m in models:
    try:
        print(f"  --> 모델 {m} 호출 중...")
        res = client.models.generate_content(
            model=m,
            contents=prompt_text
        )
        # Check for image bytes in candidates/parts
        for candidate in res.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    with open(save_path, 'wb') as f:
                        f.write(part.inline_data.data)
                    print(f"✅ 성공! 이미지 저장 완료: {save_path}")
                    success = True
                    break
        if success:
            break
    except Exception as e:
        print(f"  ⚠️ {m} 호출 오류: {str(e)[:150]}")
        time.sleep(2)

if not success:
    print("❌ Gemini 이미지 생성 실패. API 디버그를 확인합니다.")
