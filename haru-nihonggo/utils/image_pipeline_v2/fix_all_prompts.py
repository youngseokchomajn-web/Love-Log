import os
import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def generate_custom_prompt(w):
    kanji = w.get("kanji", "")
    hiragana = w.get("hiragana", "")
    korean = w.get("korean", "")
    english = w.get("english", "")
    cat = w.get("category", "")
    
    # Generic base template per category
    base_ghibli = "studio ghibli style, warm color palette, soft volumetric lighting"
    
    # Specific visual mapping rules
    if "옷" in korean or "정장" in korean or "신발" in korean or "양말" in korean or "모자" in korean or "suit" in english.lower() or "cloth" in english.lower():
        return f"neatly arranged clothing item ({korean}), wardrobe closet setting, {base_ghibli}"
    elif "죽" in korean or "음식" in korean or "요리" in korean or "밥" in korean or "과자" in korean or "차" in korean or "food" in english.lower() or "meal" in english.lower():
        return f"delicious fresh food dish ({korean}), cozy dining table setting, steam rising, {base_ghibli}"
    elif "사전" in korean or "dictionary" in english.lower():
        return f"thick antique dictionary book open on rustic wooden desk, brass spectacles, cozy library, {base_ghibli}"
    elif "등록" in korean or "신청" in korean or "서류" in korean:
        return f"official registration document paper with stamp seal and pen, wooden desk, {base_ghibli}"
    else:
        return f"iconic visual illustration representing '{korean}' ({kanji}), cozy aesthetic environment, {base_ghibli}"

def fix_all_level_prompts():
    report_path = f"{ROOT_DIR}/utils/image_pipeline_v2/full_vocab_audit_report.json"
    with open(report_path, "r", encoding="utf-8") as f:
        level_stats = json.load(f)
        
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    total_fixed = 0
    for lvl, data in level_stats.items():
        for item in data["suspicious"]:
            w_id = item["id"]
            # Replace generic prompts with improved visual prompts
            new_prompt = generate_custom_prompt(item)
            tags_cache[w_id] = new_prompt
            total_fixed += 1
            
    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] 전체 레벨 {total_fixed}개 단어 프롬프트 커스텀 정밀 개선 완료!")

if __name__ == "__main__":
    fix_all_level_prompts()
