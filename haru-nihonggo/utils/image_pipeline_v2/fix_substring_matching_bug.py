import os
import json
import re

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def clean_prompts_and_fix_pipeline():
    print("=== 단어 부분 문자열 매칭 버그 수정 및 프롬프트 복구 시작 ===")
    
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    # Food words must strictly match actual food items, avoiding "차" in "자동차/순찰차/차고" or "죽" in "죽다"
    food_korean_exact = {"죽", "음식", "요리", "밥", "과자", "녹차", "홍차", "커피", "음료", "식사", "반찬", "찌개", "국", "스프", "빵", "케이크", "라면", "국수", "초밥", "사탕"}
    clothing_korean_exact = {"옷", "의복", "정장", "군복", "모자", "양말", "신발", "바지", "셔츠", "코트", "자켓", "드레스", "치마", "넥타이", "장갑"}
    
    base_ghibli = "studio ghibli style, warm color palette, soft volumetric lighting"
    
    restored_count = 0
    
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            w_id = w["id"]
            prompt = tags_cache.get(w_id, "")
            kanji = w.get("kanji", "")
            hiragana = w.get("hiragana", "")
            korean = w.get("korean", "")
            english = w.get("english", "").lower()
            
            # Check if erroneously assigned "delicious fresh food dish"
            if "delicious fresh food dish" in prompt:
                # Test exact match
                is_real_food = any(f == korean or f" {f} " in f" {korean} " or f"({f})" in korean for f in food_korean_exact) or any(fe in english for fe in ["food", "dish", "meal", "soup", "rice", "snack", "tea", "coffee", "cake", "bread", "noodle"])
                if not is_real_food:
                    # Fix prompt based on true meaning
                    new_prompt = f"iconic visual illustration representing '{korean}' ({kanji or hiragana}), cozy aesthetic environment, {base_ghibli}"
                    tags_cache[w_id] = new_prompt
                    restored_count += 1
                    
            # Check if erroneously assigned "neatly arranged clothing item"
            elif "neatly arranged clothing item" in prompt:
                is_real_clothing = any(c == korean or f" {c} " in f" {korean} " or f"({c})" in korean for c in clothing_korean_exact) or any(ce in english for ce in ["suit", "cloth", "garment", "outfit", "dress", "shirt", "pants", "shoes", "socks", "hat", "jacket", "coat", "glove"])
                if not is_real_clothing:
                    new_prompt = f"iconic visual illustration representing '{korean}' ({kanji or hiragana}), cozy aesthetic environment, {base_ghibli}"
                    tags_cache[w_id] = new_prompt
                    restored_count += 1

    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] 오적용된 프롬프트 {restored_count}개 복구 및 교정 완료!")

if __name__ == "__main__":
    clean_prompts_and_fix_pipeline()
