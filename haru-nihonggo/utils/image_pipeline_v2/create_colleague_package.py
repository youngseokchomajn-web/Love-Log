#!/usr/bin/env python3
"""
동료 검토용(Google Drive Shareable Review) 전용 단일 독립형 HTML & 이미지 구조화 스크립트
===================================================================================
1. image_comparison_standalone.html (이미지 base64 인코딩 포함 단일 독립 파일)
2. Downloads/Haru_Nihongo_Colleague_Review_Folder/ (동료가 드라이브에 올려서 열어보기 가장 편한 100% 독립 구조)
"""

import json
import os
import glob
import base64

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"
DOWNLOADS_DIR = "/Users/youngseok/Downloads"
TARGET_LIST_FILE = os.path.join(BASE_DIR, "utils/image_pipeline_v2/target_55_words.json")

REVIEW_DIR = os.path.join(DOWNLOADS_DIR, "Haru_Nihongo_Colleague_Review")
os.makedirs(REVIEW_DIR, exist_ok=True)

with open(TARGET_LIST_FILE, 'r', encoding='utf-8') as f:
    target_words = json.load(f)

def get_base64_image(file_path):
    if not file_path or not os.path.exists(file_path):
        return None
    ext = os.path.splitext(file_path)[1].lower()
    mime = "image/jpeg" if ext in ['.jpg', '.jpeg'] else "image/webp" if ext == '.webp' else "image/png"
    with open(file_path, "rb") as img_f:
        encoded = base64.b64encode(img_f.read()).decode('utf-8')
        return f"data:{mime};base64,{encoded}"

def find_image_path(folder, word_id, kanji, kana):
    matches = glob.glob(os.path.join(BASE_DIR, folder, f"*{word_id}*.jpg")) + glob.glob(os.path.join(BASE_DIR, folder, f"*{word_id}*.webp"))
    if matches:
        return matches[0]
    if kanji:
        matches = glob.glob(os.path.join(BASE_DIR, folder, f"*{kanji}*.jpg")) + glob.glob(os.path.join(BASE_DIR, folder, f"*{kanji}*.webp"))
        if matches:
            return matches[0]
    if kana:
        matches = glob.glob(os.path.join(BASE_DIR, folder, f"*{kana}*.jpg")) + glob.glob(os.path.join(BASE_DIR, folder, f"*{kana}*.webp"))
        if matches:
            return matches[0]
    return None

cards_html = []
md_report = []

md_report.append("# 🎨 Haru-Nihongo 단어 카드 시각화 개선 (동료 검토용 리포트)\n")
md_report.append("추상어 및 의문사의 구체적 장소 서사를 제거하고 11대 카테고리 Visual Hero(물음표/실루엣/미니멀 배경)를 적용한 1:1 비교 리포트입니다.\n")

for idx, item in enumerate(target_words):
    wid = item['id']
    kanji = item.get('kanji', '')
    kana = item.get('kana', '')
    korean = item.get('korean', '')
    prompt = item.get('prompt', '')
    
    before_path = find_image_path("assets/images/words_v2", wid, kanji, kana) or find_image_path("assets/images/words", wid, kanji, kana) or os.path.join(DOWNLOADS_DIR, "KakaoTalk_Photo_2026-07-31-18-53-52.jpeg")
    after_path = find_image_path("assets/images/words_v3", wid, kanji, kana)
    
    b64_before = get_base64_image(before_path) or "https://via.placeholder.com/300x300?text=No+Before"
    b64_after = get_base64_image(after_path) or "https://via.placeholder.com/300x300?text=No+After"
    
    title_str = f"{kanji} ({kana})" if kanji else kana
    
    card = f"""
    <div class="comparison-card">
        <div class="card-header">
            <span class="word-id">#{idx+1} {wid}</span>
            <h2 class="word-title">{title_str} = <span class="korean">{korean}</span></h2>
        </div>
        <div class="image-comparison">
            <div class="side before-side">
                <div class="tag before-tag">🔴 BEFORE (기존 카드)</div>
                <div class="img-wrapper">
                    <img src="{b64_before}" alt="BEFORE">
                </div>
                <div class="desc">구체적 장소 서사(도서관/책장 등)가 단어 의미 오인 유발</div>
            </div>
            <div class="side after-side">
                <div class="tag after-tag">✨ AFTER (개선 카드)</div>
                <div class="img-wrapper">
                    <img src="{b64_after}" alt="AFTER">
                </div>
                <div class="desc">서사 배제 ➔ 미니멀 배경 + ❓ Visual Hero 물음표 강조</div>
            </div>
        </div>
        <div class="prompt-box">
            <strong>개선 프롬프트:</strong> <code>{prompt}</code>
        </div>
    </div>
    """
    cards_html.append(card)
    
    md_report.append(f"### {idx+1}. {wid} | {title_str} = {korean}")
    md_report.append(f"- **개선 핵심**: 구체적 배경 제거 ➔ 미니멀 배경 + ❓ 물음표/실루엣 메타포 강조")
    md_report.append(f"- **신규 프롬프트**: `{prompt}`\n")

standalone_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Haru-Nihongo | 동료 검토용 단어 카드 1:1 비교 대시보드</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
        .header {{ text-align: center; margin-bottom: 32px; }}
        .header h1 {{ color: #38bdf8; font-size: 2rem; margin-bottom: 8px; }}
        .header p {{ color: #94a3b8; font-size: 1.1rem; }}
        .container {{ max-width: 1100px; margin: 0 auto; display: flex; flex-direction: column; gap: 32px; }}
        .comparison-card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 24px; }}
        .card-header {{ margin-bottom: 20px; border-bottom: 1px solid #334155; padding-bottom: 12px; }}
        .word-id {{ color: #38bdf8; font-weight: bold; font-size: 0.85rem; }}
        .word-title {{ margin: 4px 0 0 0; font-size: 1.5rem; }}
        .korean {{ color: #f43f5e; }}
        .image-comparison {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
        .side {{ display: flex; flex-direction: column; gap: 12px; }}
        .tag {{ font-weight: bold; padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; width: fit-content; }}
        .before-tag {{ background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }}
        .after-tag {{ background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }}
        .img-wrapper {{ aspect-ratio: 1; width: 100%; background-color: #020617; border-radius: 12px; overflow: hidden; border: 1px solid #334155; }}
        .img-wrapper img {{ width: 100%; height: 100%; object-fit: cover; }}
        .desc {{ font-size: 0.85rem; color: #94a3b8; line-height: 1.4; }}
        .prompt-box {{ margin-top: 16px; background-color: #0f172a; padding: 12px 16px; border-radius: 8px; font-size: 0.85rem; border-left: 4px solid #38bdf8; color: #e2e8f0; }}
        .prompt-box code {{ color: #7dd3fc; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 Haru-Nihongo 단어 카드 시각화 개선 (동료 검토용 대시보드)</h1>
        <p>동료분이 이 파일 하나만 열어보시면 이미지 경로 깨짐 없이 100% 나란히 시각 비교가 가능합니다.</p>
    </div>
    <div class="container">
        {"".join(cards_html)}
    </div>
</body>
</html>
"""

# 파일 저장
html_out = os.path.join(REVIEW_DIR, "00_동료검토용_비교대시보드.html")
md_out = os.path.join(REVIEW_DIR, "01_동료검토용_비교리포트.md")

with open(html_out, 'w', encoding='utf-8') as f:
    f.write(standalone_html)

with open(md_out, 'w', encoding='utf-8') as f:
    f.write("\n".join(md_report))

print(f"✅ 동료 검토용 패키지 생성 완료: {REVIEW_DIR}")
