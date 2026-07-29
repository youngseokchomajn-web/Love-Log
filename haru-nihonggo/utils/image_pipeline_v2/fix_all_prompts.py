import os
import json
import re

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

FOOD_EXACT_KR = {"죽", "음식", "요리", "밥", "과자", "녹차", "홍차", "커피", "음료", "식사", "반찬", "찌개", "국", "스프", "빵", "케이크", "라면", "국수", "초밥", "사탕"}
CLOTHING_EXACT_KR = {"옷", "의복", "정장", "군복", "모자", "양말", "신발", "바지", "셔츠", "코트", "자켓", "드레스", "치마", "넥타이", "장갑"}

def is_exact_food(korean, english):
    tokens = set(re.split(r'[\s,/\(\)\.\:]+', korean))
    if tokens & FOOD_EXACT_KR:
        return True
    eng_lower = english.lower()
    return any(e in eng_lower for e in ["food", "dish", "meal", "soup", "rice", "snack", "tea", "coffee", "cake", "bread", "noodle"])

def is_exact_clothing(korean, english):
    tokens = set(re.split(r'[\s,/\(\)\.\:]+', korean))
    if tokens & CLOTHING_EXACT_KR:
        return True
    eng_lower = english.lower()
    return any(ce in eng_lower for ce in ["suit", "cloth", "garment", "outfit", "dress", "shirt", "pants", "shoes", "socks", "hat", "jacket", "coat", "glove"])

def generate_custom_prompt(w):
    kanji = w.get("kanji", "")
    hiragana = w.get("hiragana", "")
    korean = w.get("korean", "")
    english = w.get("english", "")
    
    base_ghibli = "studio ghibli style, warm color palette, soft volumetric lighting"
    
    if is_exact_clothing(korean, english):
        return f"neatly arranged clothing item ({korean}), wardrobe closet setting, {base_ghibli}"
    elif is_exact_food(korean, english):
        return f"delicious fresh food dish ({korean}), cozy dining table setting, steam rising, {base_ghibli}"
    elif "사전" in korean or "dictionary" in english.lower():
        return f"thick antique dictionary book open on rustic wooden desk, brass spectacles, cozy library, {base_ghibli}"
    elif "등록" in korean or "신청" in korean or "서류" in korean:
        return f"official registration document paper with stamp seal and pen, wooden desk, {base_ghibli}"
    else:
        return f"iconic visual illustration representing '{korean}' ({kanji or hiragana}), cozy aesthetic environment, {base_ghibli}"

def fix_all_level_prompts():
    report_path = f"{ROOT_DIR}/utils/image_pipeline_v2/full_vocab_audit_report.json"
    if not os.path.exists(report_path):
        return
        
    with open(report_path, "r", encoding="utf-8") as f:
        level_stats = json.load(f)
        
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    total_fixed = 0
    for lvl, data in level_stats.items():
        for item in data.get("suspicious", []):
            w_id = item["id"]
            new_prompt = generate_custom_prompt(item)
            tags_cache[w_id] = new_prompt
            total_fixed += 1
            
    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] 전체 레벨 {total_fixed}개 단어 프롬프트 (정밀 토큰 매칭) 수정 완료!")

if __name__ == "__main__":
    fix_all_level_prompts()
