#!/usr/bin/env python3
"""
Playwright 로그인 세션 및 Gemini 웹 앱 DOM 요소 고화질 이미지 다운로더
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"
OUTPUT_DIR = os.path.join(BASE_DIR, "assets/images/words_v4_gemini")
os.makedirs(OUTPUT_DIR, exist_ok=True)

prompt_text = (
    "A clean minimalist 1:1 flat vector illustration for a mobile flashcard app. "
    "Studio Ghibli inspired character art style with clean line art and flat warm colors.\n"
    "- Subject: A young girl with her head tilted in thought, curious gentle expression, looking up slightly.\n"
    "- Visual metaphor: A few small subtle floating question marks (?) around her head.\n"
    "- Background: Extremely minimal plain soft pastel background, NO buildings, NO scenery, NO clouds, NO complex environment.\n"
    "- Style: Flat 2D vector graphic, clean borders, minimal UI card design.\n"
    "- Constraint: NO text, NO Korean, NO Japanese, NO written words in the image."
)

with sync_playwright() as p:
    # 브라우저 실행 (사용자가 로그인 화면 확인 가능하도록 창 띄움)
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://gemini.google.com/app")
    
    print("📍 Gemini 웹 앱 접속. 로그인 상태 및 입력창 확인...")
    time.sleep(3)
    
    # 입력창 확인
    input_box = page.query_selector("div[contenteditable='true']")
    if input_box:
        input_box.fill(prompt_text)
        page.keyboard.press("Enter")
        print("💬 5단 플랫 벡터 프롬프트 자동 입력 완료! Imagen 3 고화질 렌더링 중 (20초)...")
        time.sleep(20)
        
        # 이미지 선택자 탐색
        img_elements = page.query_selector_all("img")
        valid_img = None
        for img in img_elements:
            src = img.get_attribute("src") or ""
            # Gemini 웹 앱이 생성한 고화질 이미지 URL 패턴
            if ("googleusercontent.com" in src or "lh3" in src) and "s64" not in src and "avatar" not in src:
                valid_img = img
                break
                
        if valid_img:
            src = valid_img.get_attribute("src")
            save_path = os.path.join(OUTPUT_DIR, "n5_何_무엇_gemini_app_v4.jpg")
            # 이미지 다운로드
            res = page.request.get(src)
            with open(save_path, "wb") as f:
                f.write(res.body())
            print(f"🎉 성공! 고화질 Gemini 웹 앱 이미지 다운로드 완료! ({len(res.body())} bytes)")
        else:
            print("⚠️ 생성된 이미지를 아직 찾지 못했습니다. 로그인 또는 렌더링 시간을 확인해주세요.")
    else:
        print("⚠️ Gemini 웹 앱 로그인 필요. 창에서 로그인을 완료해 주세요.")

    browser.close()
