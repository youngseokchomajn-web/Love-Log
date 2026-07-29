import json
import os

def restore_pure_cache():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    # Complete manual high-quality list engineered directly by Antigravity in Checkpoint 4 and subsequent batches
    # 1. First 34 words (original verified high-quality tags)
    # 2. First batch (50 tags: n1_0017 ~ n1_0413)
    # 3. Second batch (27 tags: n1_0723 ~ n1_0839)
    # 4. Third batch (27 tags: n1_0846 ~ n1_0989)
    
    # We will query the JSON to keep only the entries that:
    # A) Exist in the 34 original clean ones (we can check by looking at IDs that were generated earlier, let's keep only what we manually defined)
    # To do this safely, we can read the cache, but wait! We can just filter out any IDs that were added by Llama 3.1.
    # The Llama 3.1 tasks added tags for: n1_0415 ~ n1_0617 (first loop) and n1_0625 ~ n1_1006 (parallel loop).
    # Specifically, we know our manual IDs:
    # 1st manual batch IDs:
    manual_1 = ["n1_0017", "n1_0077", "n1_0155", "n1_0160", "n1_0169", "n1_0174", "n1_0175", "n1_0177", 
                "n1_0178", "n1_0192", "n1_0197", "n1_0201", "n1_0206", "n1_0209", "n1_0219", "n1_0226", 
                "n1_0228", "n1_0233", "n1_0235", "n1_0244", "n1_0256", "n1_0263", "n1_0275", "n1_0281", 
                "n1_0297", "n1_0298", "n1_0299", "n1_0300", "n1_0307", "n1_0309", "n1_0314", "n1_0318", 
                "n1_0325", "n1_0328", "n1_0329", "n1_0334", "n1_0337", "n1_0341", "n1_0344", "n1_0349", 
                "n1_0351", "n1_0353", "n1_0354", "n1_0356", "n1_0363", "n1_0382", "n1_0384", "n1_0401", 
                "n1_0410", "n1_0413"]
    # 2nd manual batch IDs:
    manual_2 = ["n1_0723", "n1_0742", "n1_0750", "n1_0751", "n1_0754", "n1_0756", "n1_0763", "n1_0766", 
                "n1_0773", "n1_0775", "n1_0780", "n1_0781", "n1_0783", "n1_0785", "n1_0787", "n1_0788", 
                "n1_0791", "n1_0795", "n1_0797", "n1_0798", "n1_0802", "n1_0810", "n1_0814", "n1_0815", 
                "n1_0822", "n1_0838", "n1_0839"]
    # 3rd manual batch IDs:
    manual_3 = ["n1_0846", "n1_0856", "n1_0858", "n1_0859", "n1_0865", "n1_0866", "n1_0869", "n1_0874", 
                "n1_0883", "n1_0897", "n1_0899", "n1_0900", "n1_0903", "n1_0910", "n1_0911", "n1_0914", 
                "n1_0926", "n1_0928", "n1_0932", "n1_0945", "n1_0946", "n1_0961", "n1_0965", "n1_0971", 
                "n1_0982", "n1_0988", "n1_0989"]
    
    # Original 34 clean ones (we can load the current keys, and if they are not in manual_1, manual_2, manual_3,
    # and were present before Llama 3.1 ran, we keep them.
    # Llama 3.1 ran for: n1_0415 ~ n1_0617 and n1_0625 ~ n1_1006.
    # So if an ID is NOT in Llama's range, or is in the manual lists, we keep it.)
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    pure_cache = {}
    removed_count = 0
    
    for w_id, tags in cache.items():
        # Keep if manually defined
        if w_id in manual_1 or w_id in manual_2 or w_id in manual_3:
            pure_cache[w_id] = tags
            continue
            
        # Parse numerical ID part
        try:
            num = int(w_id.split('_')[1])
        except Exception:
            # Keep non-standard format
            pure_cache[w_id] = tags
            continue
            
        # Check if in Llama 3.1 run ranges
        is_llama = False
        # 1st run: n1_0415 ~ n1_0617
        if 415 <= num <= 617:
            is_llama = True
        # 2nd run (parallel): n1_0625 ~ n1_1006
        elif 625 <= num <= 1006:
            is_llama = True
            
        if is_llama:
            removed_count += 1
            print(f"🧹 Removing Llama 3.1 contaminated entry: {w_id} ➔ {tags[:40]}...")
        else:
            pure_cache[w_id] = tags
            
    # Write back
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(pure_cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    
    print(f"\n✨ Purge Completed! Removed {removed_count} contaminated entries. Clean cache size: {len(pure_cache)}")

if __name__ == "__main__":
    restore_pure_cache()
