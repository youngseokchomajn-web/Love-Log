import os
import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def generate_gallery():
    print("=== 3단계: 로컬 시각 검수 대시보드(image_audit_gallery.html) 생성 ===")
    
    # Load categories and words
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    cards = []
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            w_id = w["id"]
            prompt = tags_cache.get(w_id, "")
            cards.append({
                "id": w_id,
                "kanji": w.get("kanji", ""),
                "hiragana": w.get("hiragana", ""),
                "korean": w.get("korean", ""),
                "level": w.get("level", "n5"),
                "category": cat_name,
                "exampleJp": w.get("exampleJp", ""),
                "exampleKo": w.get("exampleKo", ""),
                "prompt": prompt
            })
            
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Love-Log 단어 카드 이미지 적절성 검수 대시보드</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: #0f172a; color: #f8fafc; padding: 20px; }}
        header {{ display: flex; justify-content: space-between; align-items: center; background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; flex-wrap: wrap; gap: 15px; }}
        h1 {{ font-size: 1.5rem; font-weight: 700; color: #38bdf8; }}
        .controls {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
        input, select, button {{ padding: 10px 14px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #f8fafc; font-size: 0.95rem; }}
        button {{ background: #0284c7; border: none; font-weight: 600; cursor: pointer; transition: background 0.2s; }}
        button:hover {{ background: #0369a1; }}
        .btn-export {{ background: #ef4444; }}
        .btn-export:hover {{ background: #dc2626; }}
        .stats {{ font-size: 0.9rem; color: #94a3b8; width: 100%; display: flex; gap: 20px; margin-top: 10px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .card {{ background: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155; display: flex; flex-direction: column; position: relative; }}
        .card.flagged {{ border: 2px solid #ef4444; background: #2a1b24; }}
        .badge {{ position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.75); padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; color: #38bdf8; }}
        .card-header {{ padding: 15px; border-bottom: 1px solid #334155; }}
        .kanji {{ font-size: 1.4rem; font-weight: 800; color: #f8fafc; }}
        .reading {{ font-size: 0.9rem; color: #94a3b8; margin-top: 2px; }}
        .meaning {{ font-size: 1.05rem; font-weight: 600; color: #fbbf24; margin-top: 6px; }}
        .example {{ padding: 12px 15px; background: #0f172a; font-size: 0.85rem; color: #cbd5e1; line-height: 1.4; border-bottom: 1px solid #334155; flex: 1; }}
        .prompt-box {{ padding: 10px 15px; font-size: 0.75rem; color: #64748b; background: #182234; height: 60px; overflow-y: auto; line-height: 1.3; }}
        .card-footer {{ padding: 10px 15px; background: #1e293b; display: flex; justify-content: space-between; align-items: center; }}
        .flag-btn {{ background: #334155; color: #f8fafc; padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; border: none; }}
        .card.flagged .flag-btn {{ background: #ef4444; color: white; }}
    </style>
</head>
<body>

    <header>
        <div>
            <h1>🎨 Love-Log 단어 카드 이미지 적절성 검수 대시보드</h1>
            <div class="stats">
                <span>총 단어 수: <strong id="totalCount">{len(cards)}</strong>개</span>
                <span>마킹된 부적절 카드: <strong id="flaggedCount" style="color:#ef4444;">0</strong>개</span>
            </div>
        </div>
        <div class="controls">
            <input type="text" id="searchInput" placeholder="단어, 읽기, 뜻 검색..." oninput="filterCards()">
            <select id="levelSelect" onchange="filterCards()">
                <option value="all">전체 레벨 (N1~N5)</option>
                <option value="n5">N5</option>
                <option value="n4">N4</option>
                <option value="n3">N3</option>
                <option value="n2">N2</option>
                <option value="n1">N1</option>
            </select>
            <button class="btn-export" onclick="exportFlagged()">📥 부적절 이미지 리포트 다운로드 (JSON)</button>
        </div>
    </header>

    <div class="grid" id="cardGrid"></div>

    <script>
        const cardsData = {json.dumps(cards, ensure_ascii=False)};
        let flaggedIds = new Set(JSON.parse(localStorage.getItem('flagged_images') || '[]'));

        function updateStats() {{
            document.getElementById('flaggedCount').innerText = flaggedIds.size;
        }}

        function toggleFlag(id) {{
            if (flaggedIds.has(id)) {{
                flaggedIds.delete(id);
            }} else {{
                flaggedIds.add(id);
            }}
            localStorage.setItem('flagged_images', JSON.stringify(Array.from(flaggedIds)));
            updateStats();
            const cardEl = document.getElementById('card-' + id);
            if (cardEl) {{
                cardEl.classList.toggle('flagged', flaggedIds.has(id));
                const btn = cardEl.querySelector('.flag-btn');
                btn.innerText = flaggedIds.has(id) ? '🚩 마킹됨' : '🚩 부적절 마킹';
            }}
        }}

        function renderCards(list) {{
            const grid = document.getElementById('cardGrid');
            grid.innerHTML = list.slice(0, 300).map(c => {{
                const isFlagged = flaggedIds.has(c.id);
                return `
                    <div class="card ${{isFlagged ? 'flagged' : ''}}" id="card-${{c.id}}">
                        <div class="badge">${{c.level.toUpperCase()}}</div>
                        <div class="card-header">
                            <div class="kanji">${{c.kanji}}</div>
                            <div class="reading">${{c.hiragana}}</div>
                            <div class="meaning">${{c.korean}}</div>
                        </div>
                        <div class="example">
                            <strong>예문:</strong> ${{c.exampleJp}}<br>
                            <span style="color:#94a3b8;">${{c.exampleKo}}</span>
                        </div>
                        <div class="prompt-box">
                            <strong>Prompt:</strong> ${{c.prompt}}
                        </div>
                        <div class="card-footer">
                            <span style="font-size:0.75rem; color:#64748b;">${{c.id}}</span>
                            <button class="flag-btn" onclick="toggleFlag('${{c.id}}')">
                                ${{isFlagged ? '🚩 마킹됨' : '🚩 부적절 마킹'}}
                            </button>
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        function filterCards() {{
            const q = document.getElementById('searchInput').value.toLowerCase();
            const lvl = document.getElementById('levelSelect').value;
            const filtered = cardsData.filter(c => {{
                const matchesLvl = (lvl === 'all' || c.level === lvl);
                const matchesQ = !q || c.kanji.toLowerCase().includes(q) || c.hiragana.toLowerCase().includes(q) || c.korean.toLowerCase().includes(q) || c.id.toLowerCase().includes(q);
                return matchesLvl && matchesQ;
            }});
            renderCards(filtered);
            document.getElementById('totalCount').innerText = filtered.length;
        }}

        function exportFlagged() {{
            const flaggedList = cardsData.filter(c => flaggedIds.has(c.id));
            const blob = new Blob([JSON.stringify(flaggedList, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'flagged_inappropriate_images.json';
            a.click();
        }}

        // Initial Render
        updateStats();
        renderCards(cardsData);
    </script>
</body>
</html>
"""
    
    gallery_path = f"{ROOT_DIR}/image_audit_gallery.html"
    with open(gallery_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[Success] 대시보드 생성 완료: {gallery_path}")

if __name__ == "__main__":
    generate_gallery()
