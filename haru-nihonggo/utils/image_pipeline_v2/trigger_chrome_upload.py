#!/usr/bin/env python3
"""
AppleScript를 이용하여 크롬의 Google Drive 탭에서 업로드 대화상자를 열거나 제어하는 자동화 스크립트
"""

import subprocess
import os

zip_file = "/Users/youngseok/Downloads/Haru_Nihongo_Before_After_Comparison.zip"

applescript = '''
tell application "Google Chrome"
    activate
    repeat with w in windows
        set tabIndex to 1
        repeat with t in tabs of w
            if URL of t contains "drive.google.com" then
                set active tab index of w to tabIndex
                set index of w to 1
                exit repeat
            end if
            set tabIndex to tabIndex + 1
        end repeat
    end repeat
end tell
'''

subprocess.run(["osascript", "-e", applescript])
print("✅ 크롬 Google Drive 탭 활성화 완료!")
