import re
import json
import sys
import shutil
import datetime

md_file = "/Users/youngseok/.gemini/antigravity/brain/ecf3c171-57fd-4a2c-a540-51bd9049e2ec/jlpt_n4_comprehensive.md"
ts_file = "data/seedWords.ts"

# ⚠️ 안전 가드: update_n4.py 와 동일하게 seedWords.ts를 파괴적으로 덮어쓴다.
# 현재 데이터의 pronunciation/imageKey가 사라지므로 의도한 경우에만 --force 로 실행한다.
if "--force" not in sys.argv:
    print("⛔ 중단: seedWords.ts를 파괴적으로 덮어씁니다 (pronunciation/imageKey 삭제).")
    print("   정말 재생성하려면:  python parse_n4.py --force")
    sys.exit(1)

# ⛔ 구조 가드: seedWords.ts가 다중 레벨(N1~N5) 구조면 이 구버전 스크립트가 파일을 깨뜨린다.
with open(ts_file, "r", encoding="utf-8") as _f:
    _existing = _f.read()
if "baseWords" in _existing or "...n1Words" in _existing:
    print("⛔ 중단: seedWords.ts가 다중 레벨(N1~N5) 구조입니다. 이 구버전 스크립트는 실행 시 파일을 손상시킵니다.")
    print("   신규 레벨은 data/jlpt_* 파이프라인으로 관리하세요.")
    sys.exit(1)

backup = f"{ts_file}.bak-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
shutil.copyfile(ts_file, backup)
print(f"💾 백업 생성: {backup}")

with open(md_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_words = []
word_id = 200 # Start from a high ID to avoid collision

# Parsing markdown table
for line in lines:
    if line.startswith("|") and not line.startswith("| 번호 |") and not line.startswith("| --- |"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 5:
            # parts[0] is empty, parts[1] is 번호, parts[2] is 한자, parts[3] is 요미가나, parts[4] is 뜻
            kanji = parts[2]
            hiragana = parts[3]
            korean = parts[4]
            
            if kanji == "" and hiragana != "":
                kanji = hiragana
            if hiragana == "" and kanji != "":
                hiragana = kanji
                
            if not kanji and not hiragana: continue
            
            # remove extra stuff in korean like "추상/기타 " or "자연/사물 "
            korean = re.sub(r'^(추상/기타|자연/사물|기타|장소/기관|사람/신체|부사/기타|동사/기타)\s*', '', korean)
            
            word = {
                "id": f"n4_{word_id}",
                "kanji": kanji,
                "hiragana": hiragana,
                "korean": korean,
                "english": "",
                "status": "new",
                "nextReviewDate": 0,
                "interval": 0,
                "easeFactor": 2.5,
                "incorrectCount": 0
            }
            new_words.append(word)
            word_id += 1

print(f"Parsed {len(new_words)} words")

# Now append to seedWords.ts
with open(ts_file, "r", encoding="utf-8") as f:
    ts_content = f.read()

# Replace the closing bracket of the array
if "];" in ts_content:
    new_words_str = ",\n".join(json.dumps(w, ensure_ascii=False) for w in new_words)
    ts_content = ts_content.replace("\n];", ",\n" + new_words_str + "\n];")
    
    with open(ts_file, "w", encoding="utf-8") as f:
        f.write(ts_content)
    print("Updated seedWords.ts")
else:
    print("Could not find end of array in seedWords.ts")
