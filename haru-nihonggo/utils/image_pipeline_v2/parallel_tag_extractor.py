import json
import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Lock for thread-safe cache file updates
cache_lock = Lock()

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
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=20)
        if response.status_code == 200:
            res_text = response.json().get("response", "").strip()
            res_text = res_text.replace("`", "").replace('"', '').strip()
            # Split and clean tags
            tags_list = [t.strip() for t in res_text.split(',') if t.strip()]
            if len(tags_list) >= 2:
                # Filter out any weird prefix comments that Llama sometimes prepends
                filtered_tags = []
                for tag in tags_list:
                    if len(tag.split()) < 5:  # Valid tags are short phrases
                        filtered_tags.append(tag)
                if len(filtered_tags) >= 2:
                    return ", ".join(filtered_tags)
    except Exception as e:
        pass
    return None

def process_word(w_id, cat, w, cache_path):
    tags = get_danbooru_tags_ollama(
        w.get('english', ''),
        w.get('korean', ''),
        w.get('hiragana', ''),
        w.get('exampleJp', ''),
        w.get('exampleKo', ''),
        cat
    )
    if tags:
        with cache_lock:
            # Load and update
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            cache[w_id] = tags
            
            temp_path = cache_path + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, cache_path)
        return w_id, tags
    return w_id, None

def main():
    vocab_path = "utils/image_pipeline_v2/word_categories_all.json"
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    with open(vocab_path, 'r', encoding='utf-8') as f:
        categories = json.load(f)
        
    print("🚀 Starting parallel_tag_extractor.py (Multi-threaded Ollama)")
    
    # Identify uncached words
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    to_process = []
    for cat, words in categories.items():
        for w in words:
            w_id = w['id']
            if w_id not in cache:
                to_process.append((w_id, cat, w))
                
    total_count = len(to_process)
    print(f"📊 Total uncached words to process: {total_count}")
    if total_count == 0:
        print("🎉 Cache is already fully populated!")
        return

    # Use 4 parallel workers (good balance for M-series Mac CPU/GPU)
    max_workers = 4
    completed = 0
    success = 0
    
    print(f"⚡ Launching ThreadPoolExecutor with {max_workers} parallel workers...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_word, w_id, cat, w, cache_path): w_id 
            for w_id, cat, w in to_process
        }
        
        for future in as_completed(futures):
            w_id = futures[future]
            completed += 1
            try:
                w_id, tags = future.result()
                if tags:
                    success += 1
                    print(f"✅ [{completed}/{total_count}] Extracted tags for {w_id} ➔ {tags}")
                else:
                    print(f"❌ [{completed}/{total_count}] Failed extraction for {w_id}")
            except Exception as e:
                print(f"💥 [{completed}/{total_count}] Exception for {w_id}: {e}")
                
            # Log progress statistics every 50 words
            if completed % 50 == 0:
                elapsed = time.time() - start_time
                speed = completed / elapsed
                eta = (total_count - completed) / speed if speed > 0 else 0
                print(f"\n📈 Progress: {completed}/{total_count} ({completed/total_count*100:.1f}%) | Success: {success} | Speed: {speed:.2f} words/sec | ETA: {eta/60:.1f} mins\n")

if __name__ == "__main__":
    main()
