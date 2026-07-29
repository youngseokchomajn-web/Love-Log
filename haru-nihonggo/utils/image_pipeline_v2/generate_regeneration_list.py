import os
import json
import csv

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def build_regeneration_list():
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    # Read modified items from our previous audits
    regeneration_items = []
    
    # 1. Specific data-corrected IDs
    data_fixed_ids = {
        "n1_0469": "한자 표기 정정 (幕 → 帳)",
        "n1_1501": "한자 표기 정정 (悪い → 憎い)",
        "n1_2376": "한자 표기 정정 (逆上る → 遡る)",
        "n1_3179": "한자 표기 정정 (著 → 着)",
        "n2_0779": "한자 오타 정정 (卒直 → 率直)",
        "n2_1249": "유니코드 정정 (Ͼ立 → 対立)",
        "n3_0102": "한자/뜻 정정 (ね → 値)",
        "n3_0744": "한자/뜻 정정 (しまい → 姉妹)",
        "n3_1756": "한자/뜻 정정 (どう → 童)",
        "n3_1537": "영문/뜻 정정 (はい / sword → yes)",
        "n5_0567": "읽기 정정 (おじいさん → おじ)"
    }
    
    seen_ids = set()
    
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            w_id = w["id"]
            prompt = tags_cache.get(w_id, "")
            kanji = w.get("kanji", "")
            hiragana = w.get("hiragana", "")
            korean = w.get("korean", "")
            level = w.get("level", "n5").upper()
            
            reason = None
            if w_id in data_fixed_ids:
                reason = data_fixed_ids[w_id]
            elif "iconic visual illustration representing" in prompt or "clothing item" in prompt or "food dish" in prompt:
                reason = "프롬프트 시각화 정밀 개선 (범용 폴백 교체)"
            elif w_id in ["n1_0140", "n1_0621", "n1_1696", "n1_1782", "n1_2621"]:
                reason = "프롬프트 시각화 정밀 개선 (단어 맞춤 지브리 연출)"
                
            if reason and w_id not in seen_ids:
                seen_ids.add(w_id)
                regeneration_items.append({
                    "id": w_id,
                    "level": level,
                    "kanji": kanji,
                    "hiragana": hiragana,
                    "korean": korean,
                    "reason": reason,
                    "prompt": prompt
                })
                
    # Sort by Level (N5 -> N1)
    level_order = {"N5": 1, "N4": 2, "N3": 3, "N2": 4, "N1": 5}
    regeneration_items.sort(key=lambda x: (level_order.get(x["level"], 99), x["id"]))
    
    print(f"총 이미지 재생성 필요 대상 단어: {len(regeneration_items)}개")
    
    # Save to JSON
    json_path = f"{ROOT_DIR}/utils/image_pipeline_v2/image_regeneration_list.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(regeneration_items, f, ensure_ascii=False, indent=2)
        
    # Save to CSV
    csv_path = f"{ROOT_DIR}/utils/image_pipeline_v2/image_regeneration_list.csv"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "level", "kanji", "hiragana", "korean", "reason", "prompt"])
        writer.writeheader()
        writer.writerows(regeneration_items)
        
    print(f"[Success] 재생성 목록 저장 완료:")
    print(f"  - JSON: {json_path}")
    print(f"  - CSV: {csv_path}")

if __name__ == "__main__":
    build_regeneration_list()
