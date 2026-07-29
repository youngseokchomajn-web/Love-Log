import json
import os
import subprocess
import time
import requests

def get_danbooru_tags_ollama(eng, kor, hiragana, example_jp, example_ko, category):
    prompt = f"""
You are an expert prompt engineer for a Stable Diffusion Anime model (Danbooru tags).
Generate descriptive illustration tags for a Japanese vocabulary flashcard.
Word: '{eng}' (Korean: '{kor}')
Category: {category}
Example sentence (PRIMARY visual source - depict this context):
  Japanese: {example_jp}
  Korean: {example_ko}

Output rules:
1. Output ONLY a comma-separated list of Danbooru tags. NO sentences, NO explanations, NO quotes, NO introduction.
2. Output 6-10 highly descriptive visual tags that make the word's exact meaning identifiable.
3. Front-load the tags representing the action, object, or posture.
4. Keep the scene peaceful and warm.

Output format example:
shaking hands, two businessmen, suits, national flag, press conference, podium, indoor

Tags:"""
    
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.5
        }
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        if response.status_code == 200:
            res_text = response.json().get("response", "").strip()
            # Clean up potential markdown or quotes
            res_text = res_text.replace("`", "").replace('"', '').strip()
            # Basic sanity check (ensure it is comma-separated tags)
            if len(res_text.split(',')) >= 2:
                return res_text
    except Exception as e:
        print(f"  ❌ Ollama connection failed: {e}")
    return None

def main():
    vocab_path = "utils/image_pipeline_v2/word_categories_all.json"
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    output_dir = "assets/images/words_v3"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load vocabulary
    with open(vocab_path, 'r', encoding='utf-8') as f:
        categories = json.load(f)
        
    print("🚀 Starting auto_pipeline_v4 (Ollama + SDXL Hybrid)")
    
    while True:
        # Load latest cache inside the loop
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            
        # Find uncached words
        uncached = []
        for cat, words in categories.items():
            for w in words:
                w_id = w['id']
                if w_id not in cache:
                    uncached.append((cat, w))
                    
        total_left = len(uncached)
        print(f"\n📊 Remaining uncached words: {total_left}")
        if total_left == 0:
            print("🎉 All 8,424 words successfully cached and processed!")
            break
            
        # Take a chunk of 50 words
        chunk = uncached[:50]
        chunk_ids = [w['id'] for _, w in chunk]
        print(f"🎯 Processing next 50 words: {chunk_ids[0]} ~ {chunk_ids[-1]}")
        
        # 1. Fetch tags using local Ollama (Llama 3.1)
        newly_cached = {}
        for idx, (cat, w) in enumerate(chunk, 1):
            w_id = w['id']
            print(f"  [{idx}/50] Extracting tags for: {w['english']} ({w['korean']}) using local Llama 3.1...")
            
            tags = get_danbooru_tags_ollama(
                w.get('english', ''),
                w.get('korean', ''),
                w.get('hiragana', ''),
                w.get('exampleJp', ''),
                w.get('exampleKo', ''),
                cat
            )
            
            if tags:
                newly_cached[w_id] = tags
                print(f"    ➔ Tags: {tags}")
            else:
                print(f"    ⚠️ Failed to get tags for {w_id}. Skipping this turn.")
                
        # 2. Merge newly extracted tags into the main cache
        if newly_cached:
            cache.update(newly_cached)
            temp_path = cache_path + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, cache_path)
            print(f"  💾 Saved {len(newly_cached)} new tags to cache atomically. Current cache size: {len(cache)}")
            
        # 3. Trigger image generation for this specific chunk
        active_ids = [w_id for w_id in chunk_ids if w_id in cache]
        if not active_ids:
            print("  ⚠️ No tags successfully cached in this chunk. Waiting 10 seconds to retry...")
            time.sleep(10)
            continue
            
        ids_str = ",".join(active_ids)
        print(f"  🎨 Triggering SDXL generation for {len(active_ids)} words...")
        
        # Run generator_v2.py synchronously for this chunk of 50 words
        cmd = [
            "./word_card_generator/venv/bin/python",
            "utils/image_pipeline_v2/generator_v2.py",
            "--categories", vocab_path,
            "--output_dir", output_dir,
            "--ids", ids_str
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=False, text=True)
            if result.returncode == 0:
                print(f"  ✅ Image generation completed for chunk {chunk_ids[0]} ~ {chunk_ids[-1]}")
            else:
                print(f"  ❌ Image generation returned error code {result.returncode} for this chunk.")
        except Exception as e:
            print(f"  ❌ Failed to run generator subprocess: {e}")
            
        # Small cooldown between chunks
        time.sleep(2)

if __name__ == "__main__":
    main()
