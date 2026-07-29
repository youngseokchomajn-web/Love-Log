import os
import json
import re

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def sync_word_categories():
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            if w.get("id") == "n3_1079":
                w["hiragana"] = "とん"
                
    with open(cat_path, "w", encoding="utf-8") as f:
        json.dump(categories_data, f, ensure_ascii=False, indent=2)
        
    print("[Success] Cleaned n3_1079 hiragana in word_categories_all.json!")

if __name__ == "__main__":
    sync_word_categories()
