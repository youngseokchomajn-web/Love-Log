import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def check_adverbs():
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    print("=== '매우', '대단히' 단어 검색 및 프롬프트 진단 ===")
    
    found_count = 0
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            korean = w.get("korean", "")
            if "매우" in korean or "대단히" in korean:
                w_id = w["id"]
                kanji = w.get("kanji", "")
                hiragana = w.get("hiragana", "")
                prompt = tags_cache.get(w_id, "")
                found_count += 1
                print(f"[{w['level'].upper()}] ID: {w_id} | 단어: {kanji} ({hiragana}) = {korean}")
                print(f"  - Prompt: {prompt}\n")
                
    print(f"총 검색된 '매우'/'대단히' 단어: {found_count}개")

if __name__ == "__main__":
    check_adverbs()
