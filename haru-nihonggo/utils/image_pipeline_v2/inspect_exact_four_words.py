import json
import os

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def inspect_exact_four():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    target_ids = {
        "n5_0002": ("問題", "문제"),
        "n5_0015": ("売る", "팔다"),
        "n2_0430": ("箸", "젓가락"),
        "n5_0005": ("台所", "부엌")
    }
    
    for w_id, (kanji, kor) in target_ids.items():
        prompt = tags_cache.get(w_id, "NONE")
        # Find category
        cat_name = None
        for cat, words in categories_data.items():
            for w in words:
                if w["id"] == w_id:
                    cat_name = cat
                    break
                    
        print(f"=== ID: {w_id} | 단어: {kanji} ({kor}) ===")
        print(f"  - Category: {cat_name}")
        print(f"  - Cached Prompt: {prompt}\n")

if __name__ == "__main__":
    inspect_exact_four()
