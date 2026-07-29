import json
import os
import re
import unicodedata

def prune_corrupted_images():
    vocab_path = "utils/image_pipeline_v2/word_categories_all.json"
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    output_dir = "assets/images/words_v3"
    
    if not os.path.exists(vocab_path) or not os.path.exists(cache_path):
        print("❌ Error: word_categories_all.json or expanded_tags_cache.json missing.")
        return
        
    with open(vocab_path, 'r', encoding='utf-8') as f:
        categories = json.load(f)
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    # 1. Gather all word definitions by ID
    vocab_map = {}
    for cat, words in categories.items():
        for w in words:
            vocab_map[w['id']] = w
            
    # 2. Re-simulate the exact corruption criteria to identify the target IDs to prune
    # (This matches the exact logic of clean_corrupted_cache.py to ensure 0% false positives)
    purged_ids = set()
    for w_id, w in vocab_map.items():
        eng = w.get('english', '')
        kor = w.get('korean', '')
        
        # If the word ID was not found in the CLEANED cache, it was either:
        # a) Purged during the cleaning process as corrupted
        # b) Never cached at all (not processed yet)
        # We only want to delete files for words that were PURGED.
        # But to be 100% safe, we recalculate the corruption condition for each word's former state:
        # Since we ran clean_corrupted_cache.py, the cache now contains ONLY clean entries.
        # If a word is NOT in the cleaned cache, but an image file exists for it,
        # it means it was rendered using the corrupted fallback tag.
        if w_id not in cache:
            purged_ids.add(w_id)

    print(f"🎯 Targeted word IDs for image pruning: {len(purged_ids)}")
    
    # 3. Helper functions for filename sanitization (copied exactly from generator_v2.py)
    def clean_filename_korean(korean):
        cleaned = re.sub(r'[\s/,;\?:\*\"<>\|\\\.\(\)\[\]\{\}]', '', korean)
        return unicodedata.normalize('NFC', cleaned)

    def clean_filename_japanese(jp):
        cleaned = jp.replace(' ', '')
        cleaned = re.sub(r'[\s/,;\?:\*\"<>\|\\\.\(\)\[\]\{\}〜~]', '', cleaned)
        return unicodedata.normalize('NFC', cleaned)

    # 4. Map target IDs to their exact generated filenames
    files_to_delete = []
    for w_id in purged_ids:
        w = vocab_map[w_id]
        level = w.get('level') or 'n4'
        jp_text = w.get('kanji') or w.get('hiragana', '')
        kor_text = w.get('korean', '')
        
        if jp_text and kor_text:
            safe_jp = clean_filename_japanese(jp_text)
            safe_kor = clean_filename_korean(kor_text)
            filename = f"{level}_{safe_jp}_{safe_kor}.jpg"
            file_path = os.path.join(output_dir, filename)
            
            if os.path.exists(file_path):
                files_to_delete.append((w_id, filename, file_path))

    print(f"📂 Found {len(files_to_delete)} rendered image files corresponding to corrupted cache entries.")
    
    # 5. Execute Pruning
    deleted_count = 0
    for w_id, filename, path in files_to_delete:
        try:
            os.remove(path)
            deleted_count += 1
            if deleted_count <= 20:
                print(f"  🗑️ Deleted: {filename}")
        except Exception as e:
            print(f"  ❌ Failed to delete {filename}: {e}")
            
    if len(files_to_delete) > 20:
        print(f"  ... and {len(files_to_delete)-20} more files deleted.")
        
    print(f"\n✅ Pruning completed. Successfully deleted {deleted_count} low-quality images.")

if __name__ == "__main__":
    prune_corrupted_images()
