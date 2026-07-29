import json
import os
import re

def clean_corrupted_cache():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    vocab_path = "utils/image_pipeline_v2/word_categories_all.json"
    
    if not os.path.exists(cache_path) or not os.path.exists(vocab_path):
        print("Required files not found.")
        return
        
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    with open(vocab_path, 'r', encoding='utf-8') as f:
        categories = json.load(f)
        
    # Build vocabulary mapping for english word lookup
    vocab_map = {}
    for cat, words in categories.items():
        for w in words:
            vocab_map[w['id']] = w
            
    print(f"Loaded cache: {len(cache)} entries.")
    
    corrupted_count = 0
    cleaned_cache = {}
    purged_details = []
    
    for w_id, tags in cache.items():
        w = vocab_map.get(w_id)
        if not w:
            # Word no longer exists in JSON, discard
            corrupted_count += 1
            continue
            
        eng = w.get('english', '')
        
        # Check criteria for corruption:
        # 1. Tags string is exactly equal to english translation (or very close)
        # 2. Tags has no commas (usually Danbooru has multiple tags separated by commas)
        # 3. Tags has semicolons (direct copy of english polysemous words)
        is_corrupted = False
        
        if tags.strip() == eng.strip():
            is_corrupted = True
        elif ';' in tags and ',' not in tags:
            is_corrupted = True
        elif len(tags.split(',')) <= 2 and len(tags.strip().split()) <= 4:
            # Too short, probably fallback to English translation
            # e.g. "handcuffs; manacles" or "dried plum"
            is_corrupted = True
            
        if is_corrupted:
            corrupted_count += 1
            purged_details.append(f"[{w_id}] Kanji: {w.get('kanji') or w.get('hiragana')} | Korean: {w['korean']} | Eng: {eng} | Purged Tags: '{tags}'")
        else:
            cleaned_cache[w_id] = tags
            
    print(f"\n📊 Total corrupted/fallback tags detected: {corrupted_count}")
    
    print("\n--- Purged Examples Sample ---")
    for detail in purged_details[:20]:
        print(detail)
    if len(purged_details) > 20:
        print(f"... and {len(purged_details)-20} more.")
        
    # Write back clean cache atomically
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    print(f"\n💾 Atomic write completed. Cleaned cache entries: {len(cleaned_cache)} (Purged: {corrupted_count})")

if __name__ == "__main__":
    clean_corrupted_cache()
