#!/usr/bin/env python3
"""
기존(BEFORE) vs 개선(AFTER) 단어 카드 비교 HTML 생성 스크립트
============================================================
- assets/images/words 및 words_v2 (기존) vs words_v3 (신규) 1:1 비교
- image_comparison_before_after.html 생성
"""

import json
import os
import glob

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"
TARGET_LIST_FILE = os.path.join(BASE_DIR, "utils/image_pipeline_v2/target_55_words.json")
OUTPUT_HTML = os.path.join(BASE_DIR, "image_comparison_before_after.html")

with open(TARGET_LIST_FILE, 'r', encoding='utf-8') as f:
    target_words = json.load(f)

# 이미지 파일 매칭 함수
def find_image_path(folder, word_id, kanji, kana):
    # 1. ID 패턴
    matches = glob.glob(os.path.join(BASE_DIR, folder, f"*{word_id}*.jpg")) + glob.glob(os.path.join(BASE_DIR, folder, f"*{word_id}*.webp"))
    if matches:
        return os.path.relpath(matches[0], BASE_DIR)
    
    # 2. 한자 패턴
    if kanji:
        matches = glob.glob(os.path.join(BASE_DIR, folder, f"*{kanji}*.jpg")) + glob.glob(os.path.join(BASE_DIR, folder, f"*{kanji}*.webp"))
        if matches:
            return os.path.relpath(matches[0], BASE_DIR)
            
    # 3. 가나 패턴
    if kana:
        matches = glob.glob(os.path.join(BASE_DIR, folder, f"*{kana}*.jpg")) + glob.glob(os.path.join(BASE_DIR, folder, f"*{kana}*.webp"))
        if matches:
            return os.path.relpath(matches[0], BASE_DIR)
            
    return None

cards_html = []

for idx, item in enumerate(target_words):
    wid = item['id']
    kanji = item.get('kanji', '')
    kana = item.get('kana', '')
    korean = item.get('korean', '')
    prompt = item.get('prompt', '')
    
    # BEFORE: words_v2 or words
    before_img = find_image_path("assets/images/words_v2", wid, kanji, kana) or find_image_path("assets/images/words", wid, kanji, kana)
    
    # AFTER: words_v3
    after_img = find_image_path("assets/images/words_v3", wid, kanji, kana)
    
    before_src = before_img if before_img else "https://via.placeholder.com/300x300?text=No+Before+Image"
    after_src = after_img if after_img else "https://via.placeholder.com/300x300?text=No+After+Image"
    
    card = f"""
    <div class="comparison-card">
        <div class="card-header">
            <span class="word-id">#{idx+1} {wid}</span>
            <h2 class="word-title">{kanji if kanji else kana} <span class="kana">({kana})</span> = <span class="korean">{korean}</span></h2>
        </div>
        <div class="image-comparison">
            <div class="side before-side">
                <div class="tag before-tag">🔴 BEFORE (기존 이미지)</div>
                <div class="img-wrapper">
                    <img src="{before_src}" alt="BEFORE" loading="lazy">
                </div>
                <div class="desc">
                    <strong>기존 문제점:</strong> 구체적 배경 서사(도서관/책/특정 장소)로 단어 의미 왜곡 위험
                </div>
            </div>
            <div class="side after-side">
                <div class="tag after-tag">✨ AFTER (개선된 이미지)</div>
                <div class="img-wrapper">
                    <img src="{after_src}" alt="AFTER" loading="lazy">
                </div>
                <div class="desc">
                    <strong>개선 사항:</strong> 서사 제거 ➔ 미니멀 배경 + ❓ 물음표/실루엣 Visual Hero 강조
                </div>
            </div>
        </div>
        <div class="prompt-box">
            <strong>적용된 새 프롬프트:</strong> <code>{prompt}</code>
        </div>
    </div>
    """
    cards_html.append(card)

html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Haru-Nihongo | 단어 카드 BEFORE vs AFTER 시각 비교 대시보드</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --accent-before: #ef4444;
            --accent-after: #10b981;
            --border-color: #334155;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 24px;
        }}
        .header-title {{
            text-align: center;
            margin-bottom: 32px;
        }}
        .header-title h1 {{
            font-size: 2rem;
            margin-bottom: 8px;
            color: #38bdf8;
        }}
        .header-title p {{
            color: #94a3b8;
            font-size: 1.1rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 32px;
        }}
        .comparison-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }}
        .card-header {{
            margin-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
        }}
        .word-id {{
            font-size: 0.85rem;
            color: #38bdf8;
            font-weight: bold;
        }}
        .word-title {{
            margin: 4px 0 0 0;
            font-size: 1.6rem;
        }}
        .kana {{
            color: #cbd5e1;
            font-size: 1.2rem;
        }}
        .korean {{
            color: #f43f5e;
        }}
        .image-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }}
        @media (max-width: 768px) {{
            .image-comparison {{
                grid-template-columns: 1fr;
            }}
        }}
        .side {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .tag {{
            font-weight: bold;
            padding: 6px 12px;
            border-radius: 8px;
            display: inline-block;
            width: fit-content;
            font-size: 0.9rem;
        }}
        .before-tag {{
            background-color: rgba(239, 68, 68, 0.2);
            color: var(--accent-before);
            border: 1px solid var(--accent-before);
        }}
        .after-tag {{
            background-color: rgba(16, 185, 129, 0.2);
            color: var(--accent-after);
            border: 1px solid var(--accent-after);
        }}
        .img-wrapper {{
            aspect-ratio: 1;
            width: 100%;
            background-color: #020617;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        .img-wrapper img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .desc {{
            font-size: 0.9rem;
            color: #94a3b8;
            line-height: 1.4;
        }}
        .prompt-box {{
            margin-top: 16px;
            background-color: #0f172a;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.85rem;
            color: #e2e8f0;
            border-left: 4px solid #38bdf8;
        }}
        .prompt-box code {{
            color: #7dd3fc;
        }}
    </style>
</head>
<body>
    <div class="header-title">
        <h1>🎨 Haru-Nihongo | BEFORE vs AFTER 이미지 시각 비교</h1>
        <p>추상어 오인 문제 해결: 구체적 배경 서사 제거 ➔ 미니멀 배경 + ❓ Visual Hero 적용 비교 (총 55개)</p>
    </div>
    <div class="container">
        {"".join(cards_html)}
    </div>
</body>
</html>
"""

with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ BEFORE vs AFTER 비교 HTML 생성 완료: {OUTPUT_HTML}")
