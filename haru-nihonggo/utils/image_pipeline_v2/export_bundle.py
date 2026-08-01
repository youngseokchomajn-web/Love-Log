#!/usr/bin/env python3
"""
Love-Log 이미지 파이프라인 외부 공유용 번들 생성 스크립트
===================================================
Downloads 폴더에 2가지 형태의 번들 생성:
1. LoveLog_ImagePipeline_Bundle.zip (모든 파이프라인 코드, README, 리포트 압축)
2. LoveLog_ImagePipeline_Summary.txt (대화창 단일 복사/붙여넣기 또는 파일 첨부용 텍스트)
"""

import os
import zipfile
import json

downloads_dir = "/Users/youngseok/Downloads"
base_dir = "/Users/youngseok/Desktop/love-log/haru-nihonggo/utils/image_pipeline_v2"
brain_dir = "/Users/youngseok/.gemini/antigravity/brain/3363dc1d-0877-4c52-a76a-a737bee15ffa"

zip_path = os.path.join(downloads_dir, "LoveLog_ImagePipeline_Bundle.zip")
txt_path = os.path.join(downloads_dir, "LoveLog_ImagePipeline_Summary.txt")

# 1. ZIP 번들 생성
files_to_zip = [
    ("README.md", os.path.join(base_dir, "README.md")),
    ("audit_framework_v3.py", os.path.join(base_dir, "audit_framework_v3.py")),
    ("generator_v2.py", os.path.join(base_dir, "generator_v2.py")),
    ("tag_extractor.py", os.path.join(base_dir, "tag_extractor.py")),
    ("abstract_word_audit_report.md", os.path.join(brain_dir, "abstract_word_audit_report.md")),
    ("framework_audit_result.md", os.path.join(brain_dir, "framework_audit_result.md")),
    ("word_categories.json", os.path.join(base_dir, "word_categories.json")),
]

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for arcname, filepath in files_to_zip:
        if os.path.exists(filepath):
            zipf.write(filepath, arcname)

print(f"✅ ZIP 번들 생성 완료: {zip_path}")

# 2. 통합 텍스트 파일 (Summary.txt) 생성
summary_content = []
summary_content.append("==========================================================================")
summary_content.append("HARU-NIHONGO / LOVE-LOG IMAGE PIPELINE & PROMPT AUDIT BUNDLE")
summary_content.append("==========================================================================\n")

for arcname, filepath in files_to_zip:
    if os.path.exists(filepath) and not filepath.endswith('.json'):
        summary_content.append(f"\n{'='*70}")
        summary_content.append(f" FILE: {arcname}")
        summary_content.append(f"{'='*70}\n")
        with open(filepath, 'r', encoding='utf-8') as f:
            summary_content.append(f.read())

# 샘플 프롬프트 50개 추출 추가
cache_path = os.path.join(base_dir, "expanded_tags_cache.json")
if os.path.exists(cache_path):
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    summary_content.append(f"\n{'='*70}")
    summary_content.append(f" SAMPLE PROMPT CACHE (50 Representative Words)")
    summary_content.append(f"{'='*70}\n")
    
    sample_keys = list(cache.keys())[:50]
    for k in sample_keys:
        summary_content.append(f"Key: {k} | Prompt: {cache[k]}")

with open(txt_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(summary_content))

print(f"✅ 단일 텍스트 요약본 생성 완료: {txt_path}")
