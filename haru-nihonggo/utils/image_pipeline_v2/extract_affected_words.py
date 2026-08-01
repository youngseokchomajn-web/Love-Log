import os
import json
import csv
import re

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def extract_all_affected():
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    affected_list = []
    
    # Substring collision culprits: "차" (car/train/crossroads/chime), "죽" (die/porridge), "노" (no/yellow), "해" (do/sun), etc.
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            w_id = w["id"]
            kanji = w.get("kanji", "")
            hiragana = w.get("hiragana", "")
            korean = w.get("korean", "")
            english = w.get("english", "")
            level = w.get("level", "n5").upper()
            prompt = tags_cache.get(w_id, "")
            
            # Check if this word contains "차" or "죽" or similar collision substring AND is NOT a real food item
            contains_cha = "차" in korean
            contains_juk = "죽" in korean
            
            is_real_food = any(fe in english.lower() for fe in ["food", "dish", "meal", "soup", "rice", "snack", "tea", "coffee", "cake", "bread", "noodle", "porridge"]) or korean in ["죽", "음식", "요리", "밥", "과자", "녹차", "홍차", "커피", "식사"]
            
            if (contains_cha or contains_juk) and not is_real_food:
                reason = "부분 문자열 매칭 오작동 ('차'/'죽' 함유 비음식 단어)"
                if contains_cha:
                    reason = "부분 문자열 매칭 오작동 ('차' -> 자동차/열차/차고/차임벨 등 비음식 단어)"
                elif contains_juk:
                    reason = "부분 문자열 매칭 오작동 ('죽' -> 죽다/반죽 등 비음식 단어)"
                    
                affected_list.append({
                    "id": w_id,
                    "level": level,
                    "kanji": kanji,
                    "hiragana": hiragana,
                    "korean": korean,
                    "english": english,
                    "reason": reason,
                    "fixed_prompt": prompt
                })
                
    # Sort by Level (N5 -> N1)
    level_order = {"N5": 1, "N4": 2, "N3": 3, "N2": 4, "N1": 5}
    affected_list.sort(key=lambda x: (level_order.get(x["level"], 99), x["id"]))
    
    print(f"=== 부분 문자열 매칭 버그로 영향 받은 단어 총 {len(affected_list)}개 추출 완료 ===")
    
    # Save to JSON
    json_path = f"{ROOT_DIR}/utils/image_pipeline_v2/affected_words_list.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(affected_list, f, ensure_ascii=False, indent=2)
        
    # Save to CSV
    csv_path = f"{ROOT_DIR}/utils/image_pipeline_v2/affected_words_list.csv"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "level", "kanji", "hiragana", "korean", "english", "reason", "fixed_prompt"])
        writer.writeheader()
        writer.writerows(affected_list)
        
    print(f"[Success] 추출 목록 저장 완료:\n  - JSON: {json_path}\n  - CSV: {csv_path}")

if __name__ == "__main__":
    extract_all_affected()
