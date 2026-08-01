#!/usr/bin/env python3
"""
Chrome Remote Debugging (CDP 9222) 포트 연동 Gemini 웹 앱 자동 렌더링 & 고화질 다운로더
==================================================================================
사용자 맥북에서 이미 로그인된 크롬 브라우저 세션을 그대로 제어하여
100% 동일한 극상 퀄리티 Gemini 웹 이미지를 다운로드합니다.
"""

import os
import sys
import time
import requests
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

print("🚀 Chrome CDP(9222) 포트 연결을 통해 로그인 세션 유지 자동화 시작...")

with sync_playwright() as p:
    try:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
    except Exception:
        # Chrome CDP 포트 미실행 시 persistent context 사용
        browser = p.chromium.launch_persistent_context(
            user_data_dir=os.path.expanduser("~/Library/Application Support/Google/Chrome"),
            headless=False,
            channel="chrome"
        )
        page = browser.new_page()

    page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
    print("📍 로그인된 Gemini 웹 앱 접속 완료!")
    time.sleep(3)

    input_box = page.query_selector("div[contenteditable='true']")
    if input_box:
        input_box.fill(prompt_text)
        page.keyboard.press("Enter")
        print("💬 프롬프트 전송 완료. Imagen 3 고화질 렌더링 중 (18초)...")
        time.sleep(18)

        # 생성된 고화질 이미지 엘리먼트 추출
        imgs = page.query_selector_all("img")
        target_src = None
        for img in imgs:
            src = img.get_attribute("src") or ""
            if "googleusercontent.com" in src and "s64" not in src and "avatar" not in src:
                target_src = src
                break

        if target_src:
            save_path = os.path.join(OUTPUT_DIR, "n5_何_무엇_gemini_app_v4.jpg")
            res = requests.get(target_src)
            with open(save_path, "wb") as f:
                f.write(res.content)
            print(f"🎉 성공! 1개 고화질 테스트 이미지 다운로드 완료! 위치: {save_path}")
        else:
            print("⚠️ 이미지를 추출하지 못했습니다. 화면 구성을 확인합니다.")
    else:
        print("⚠️ Gemini 입력창을 찾을 수 없습니다.")

    browser.close()
