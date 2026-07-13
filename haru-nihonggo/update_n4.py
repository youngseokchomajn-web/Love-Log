import re
import json
import sys
import shutil
import datetime

md_file = "/Users/youngseok/.gemini/antigravity/brain/ecf3c171-57fd-4a2c-a540-51bd9049e2ec/jlpt_n4_comprehensive.md"
ts_file = "data/seedWords.ts"

# ⚠️ 안전 가드: 이 스크립트는 seedWords.ts의 모든 N4 항목을 재생성한다.
# 현재 커밋된 데이터에는 이 스크립트가 출력하지 않는 `pronunciation`/`imageKey`가
# 들어 있고 id도 n4_100~ 로 매겨져 있어, 그냥 재실행하면 그 값들이 전부 사라지고
# id가 n4_200~ 으로 뒤바뀌어 이미지 매칭이 깨진다.
# 반드시 의도한 경우에만 `--force` 로 실행하며, 실행 전 자동 백업한다.
if "--force" not in sys.argv:
    print("⛔ 중단: 이 스크립트는 seedWords.ts의 N4 데이터를 파괴적으로 덮어씁니다.")
    print("   현재 데이터의 pronunciation/imageKey가 삭제되고 id가 재넘버링됩니다.")
    print("   정말 재생성하려면:  python update_n4.py --force")
    sys.exit(1)

# ⛔ 구조 가드: seedWords.ts가 다중 레벨(N1~N5) 구조로 재편된 이후엔 이 구버전
# 단일 배열 append 스크립트가 파일을 깨뜨린다(글로벌 치환이 export 배열까지 건드림).
# 신규 레벨 데이터는 data/jlpt_* 파이프라인을 사용하라.
with open(ts_file, "r", encoding="utf-8") as _f:
    _existing = _f.read()
if "baseWords" in _existing or "...n1Words" in _existing:
    print("⛔ 중단: seedWords.ts가 다중 레벨(N1~N5) 구조입니다.")
    print("   이 스크립트는 구버전 단일 배열 전용이라 지금 실행하면 파일이 손상됩니다.")
    print("   신규 레벨은 data/jlpt_* 파이프라인으로 관리하세요.")
    sys.exit(1)

# 실행 전 타임스탬프 백업
backup = f"{ts_file}.bak-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
shutil.copyfile(ts_file, backup)
print(f"💾 백업 생성: {backup}")

with open(md_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_words = []
word_id = 200

for line in lines:
    if line.startswith("|") and not line.startswith("| 번호 |") and not line.startswith("| --- |"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 5:
            kanji = parts[2]
            hiragana = parts[3]
            korean = parts[4]
            
            if kanji == "" and hiragana != "": kanji = hiragana
            if hiragana == "" and kanji != "": hiragana = kanji
            if not kanji and not hiragana: continue
            
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

print(f"Parsed {len(new_words)} words from markdown.")

with open(ts_file, "r", encoding="utf-8") as f:
    ts_content = f.read()

# Find where the N4 words start
marker = '{"id": "n4_'
if marker in ts_content:
    base_content = ts_content[:ts_content.index(marker)]
    # Ensure it ends cleanly
    base_content = base_content.rstrip().rstrip(",") + ",\n"
else:
    # If not found, just replace before ];
    base_content = ts_content.replace("\n];", ",\n")

new_words_str = ",\n".join(json.dumps(w, ensure_ascii=False) for w in new_words)

final_content = base_content + new_words_str + "\n];\n"

with open(ts_file, "w", encoding="utf-8") as f:
    f.write(final_content)

print("Updated seedWords.ts with new N4 words.")
