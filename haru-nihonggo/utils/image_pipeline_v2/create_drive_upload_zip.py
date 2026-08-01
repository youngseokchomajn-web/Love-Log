#!/usr/bin/env python3
"""
구글 드라이브 업로드용 BEFORE vs AFTER 시각 비교 압축 패키지 생성 스크립트
"""

import os
import zipfile
import json
import glob

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"
DOWNLOADS_DIR = "/Users/youngseok/Downloads"
ZIP_PATH = os.path.join(DOWNLOADS_DIR, "Haru_Nihongo_Before_After_Comparison.zip")

files_to_pack = [
    "image_comparison_before_after.html",
    "image_audit_gallery.html",
    "utils/image_pipeline_v2/expanded_tags_cache.json",
    "utils/image_pipeline_v2/abstract_framework_audit_result.json",
    "utils/image_pipeline_v2/target_55_words.json",
]

with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # 1. HTML 및 JSON 파일 패킹
    for rel_path in files_to_pack:
        abs_path = os.path.join(BASE_DIR, rel_path)
        if os.path.exists(abs_path):
            zipf.write(abs_path, os.path.basename(rel_path))
            
    # 2. 55개 신규 이미지 카드 패킹 (assets/images/words_v3)
    target_55_path = os.path.join(BASE_DIR, "utils/image_pipeline_v2/target_55_words.json")
    with open(target_55_path, 'r', encoding='utf-8') as f:
        target_words = json.load(f)
        
    for w in target_words:
        wid = w['id']
        kanji = w.get('kanji', '')
        kana = w.get('kana', '')
        
        # v3 이미지
        v3_matches = glob.glob(os.path.join(BASE_DIR, "assets/images/words_v3", f"*{wid}*.jpg"))
        if not v3_matches and kanji:
            v3_matches = glob.glob(os.path.join(BASE_DIR, "assets/images/words_v3", f"*{kanji}*.jpg"))
        if v3_matches:
            zipf.write(v3_matches[0], os.path.join("rendered_images_v3", os.path.basename(v3_matches[0])))

print(f"✅ 구글 드라이브 업로드용 ZIP 패키지 생성 완료: {ZIP_PATH}")
