import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def inspect_four_words():
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    target_ids = ["n5_0002", "n5_0083", "n5_0344", "n5_0428"]
    
    print("=== 4개 단어 프롬프트 및 카테고리 진단 ===")
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            if w["id"] in target_ids:
                w_id = w["id"]
                kanji = w.get("kanji", "")
                hiragana = w.get("hiragana", "")
                korean = w.get("korean", "")
                prompt = tags_cache.get(w_id, "")
                print(f"\nID: {w_id} | 단어: {kanji} ({hiragana}) = {korean}")
                print(f"  - Category: {cat_name}")
                print(f"  - Cached Prompt: {prompt}")

if __name__ == "__main__":
    inspect_four_words()
