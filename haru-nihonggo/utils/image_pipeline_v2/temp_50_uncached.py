import json
import os

def query_50():
    vocab_path = "utils/image_pipeline_v2/word_categories_all.json"
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    with open(vocab_path, 'r', encoding='utf-8') as f:
        categories = json.load(f)
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    uncached = []
    for cat, words in categories.items():
        for w in words:
            w_id = w['id']
            if w_id not in cache:
                uncached.append(w)
                if len(uncached) >= 50:
                    break
        if len(uncached) >= 50:
            break
            
    temp_out = "utils/image_pipeline_v2/temp_50_uncached.json"
    with open(temp_out, 'w', encoding='utf-8') as f:
        json.dump(uncached, f, ensure_ascii=False, indent=2)
    print(f"Stored {len(uncached)} uncached words in temp_50_uncached.json")

if __name__ == "__main__":
    query_50()
