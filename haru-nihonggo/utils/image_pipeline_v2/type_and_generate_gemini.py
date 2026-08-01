#!/usr/bin/env python3
"""
AppleScript 기반 Gemini 웹 앱 자동 텍스트 입력 및 이미지 생성 구동 스크립트
"""

import subprocess
import time
import os

prompt_text = (
    "A clean minimalist 1:1 flat vector illustration for a mobile flashcard app. "
    "Studio Ghibli inspired character art style with clean line art and flat warm colors. "
    "- Subject: A young girl with her head tilted in thought, curious gentle expression, looking up slightly. "
    "- Visual metaphor: A few small subtle floating question marks (?) around her head. "
    "- Background: Extremely minimal plain soft pastel background, NO buildings, NO scenery, NO clouds, NO complex environment. "
    "- Style: Flat 2D vector graphic, clean borders, minimal UI card design. "
    "- Constraint: NO text, NO Korean, NO Japanese, NO written words in the image."
)

# 클립보드에 프롬프트 복사
process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
process.communicate(prompt_text.encode('utf-8'))

applescript = '''
tell application "Google Chrome"
    activate
    repeat with w in windows
        set tabIndex to 1
        repeat with t in tabs of w
            if URL of t contains "gemini.google.com" then
                set active tab index of w to tabIndex
                set index of w to 1
                exit repeat
            end if
            set tabIndex to tabIndex + 1
        end repeat
    end repeat
end tell
tell application "System Events"
    delay 0.5
    keystroke "v" using {command down}
    delay 0.5
    key code 36 -- Return
end tell
'''

subprocess.run(["osascript", "-e", applescript])
print("💬 Gemini 웹 앱으로 5단 보정 프롬프트 자동 입력 완료!")
print("⏳ Gemini가 고화질 이미지를 렌더링 중입니다 (약 15초)...")
