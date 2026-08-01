#!/usr/bin/env python3
"""
Playwright 기반 Gemini 웹 앱(gemini.google.com) 1개 테스트 자동 생성 스크립트
========================================================================
- 사용자 크롬 프로필(OAuth 로그인 상태)을 연결하거나 디버깅 포트로 접속하여
  Gemini 웹 앱에 5단 보정 프롬프트를 전송하고 100% 동일한 극상 퀄리티 이미지를 다운로드합니다.
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

print("🚀 Playwright로 Gemini 웹 앱 브라우저 자동화 시작...")

with sync_playwright() as p:
    # 사용자 Mac Chrome 데이터 디렉토리 활용 (로그인 세션 유지)
    user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    
    try:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=os.path.expanduser("~/.gemini_playwright_profile"),
            headless=False,
            channel="chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
    except Exception:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=os.path.expanduser("~/.gemini_playwright_profile"),
            headless=False
        )

    page = browser.new_page()
    page.goto("https://gemini.google.com/app", wait_until="networkidle")
    
    print("📍 Gemini 웹 앱 페이지 접속 완료!")
    time.sleep(3)

    # 프롬프트 입력창 찾기
    input_box = page.query_selector("div[contenteditable='true']") or page.query_selector("textarea")
    if input_box:
        input_box.fill(prompt_text)
        time.sleep(1)
        # Enter키 또는 전송 버튼 클릭
        page.keyboard.press("Enter")
        print("💬 Gemini 웹 앱으로 5단 보정 프롬프트 자동 전송 완료!")
        print("⏳ 고퀄리티 이미지 생성 대기 중 (약 15초)...")
        time.sleep(18)

        # 이미지 요소 찾기
        imgs = page.query_selector_all("img")
        target_img = None
        for img in imgs:
            src = img.get_attribute("src") or ""
            if "googleusercontent.com" in src or "blob:" in src or "generative" in src:
                target_img = img
                break
        
        if target_img:
            img_url = target_img.get_attribute("src")
            print(f"✅ 생성된 이미지 발견: {img_url[:60]}...")
            save_path = os.path.join(OUTPUT_DIR, "n5_何_무엇_gemini_app_v4.jpg")
            
            # 이미지 바이트 저장
            response = page.request.get(img_url)
            with open(save_path, "wb") as f:
                f.write(response.body())
            print(f"🎉 1개 테스트 이미지 자동 다운로드 완료! 저장 위치: {save_path}")
        else:
            print("⚠️ 이미지를 바로 감지하지 못했습니다. 화면을 확인해 주세요.")
    else:
        print("⚠️ Gemini 입력창을 찾지 못했습니다. 로그인 상태를 확인해 주세요.")

    browser.close()
