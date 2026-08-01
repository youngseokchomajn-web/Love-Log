import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def inspect_five():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    target_korean_list = ["편리하다", "지우다", "끄다", "닫다", "구", "9", "집"]
    
    print("=== 지적하신 5개 단어군 프롬프트 전수 점검 ===")
    
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            korean = w.get("korean", "")
            kanji = w.get("kanji", "")
            hiragana = w.get("hiragana", "")
            w_id = w["id"]
            
            if any(tk in korean for tk in target_korean_list) or kanji in ["便利", "消す", "閉める", "九", "家", "内"]:
                prompt = tags_cache.get(w_id, "")
                print(f"[{w.get('level', 'n5').upper()}] ID: {w_id} | 단어: {kanji} ({hiragana}) = {korean}")
                print(f"  - Category: {cat_name}")
                print(f"  - Current Prompt: {prompt}\n")

if __name__ == "__main__":
    inspect_five()
