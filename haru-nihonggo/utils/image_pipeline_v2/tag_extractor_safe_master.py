import os
import json
import time
from google import genai
from dotenv import load_dotenv

# Load env for Gemini API
env_path = os.path.join("word_card_generator", ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("⚠️ GEMINI_API_KEY is not set in word_card_generator/.env")
    exit(1)

client = genai.Client(api_key=api_key)

def get_danbooru_tags_gemini(eng, kor, hiragana, example_jp, example_ko, category):
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
    
    try:
        # Use official new SDK client with gemini-2.5-flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        if response and response.text:
            res_text = response.text.strip()
            res_text = res_text.replace("`", "").replace('"', '').strip()
            if len(res_text.split(',')) >= 2:
                return res_text
    except Exception as e:
        print(f"  ❌ Gemini API Call Exception: {e}")
    return None

def main():
    vocab_path = "utils/image_pipeline_v2/word_categories_all.json"
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    print("🚀 Starting tag_extractor_safe_master.py (Google GenAI New SDK - Strict 4.5s Rate Limited)")
    
    with open(vocab_path, 'r', encoding='utf-8') as f:
        categories = json.load(f)
        
    while True:
        # Load latest cache
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            
        # Find next uncached word
        target_w = None
        target_cat = None
        for cat, words in categories.items():
            for w in words:
                w_id = w['id']
                if w_id not in cache:
                    target_w = w
                    target_cat = cat
                    break
            if target_w:
                break
                
        if not target_w:
            print("🎉 All 8,424 words have been successfully cached!")
            break
            
        w_id = target_w['id']
        print(f"⏳ [{len(cache)+1}/8424] Querying Gemini API for {w_id}: {target_w['english']} ({target_w['korean']})...")
        
        start_time = time.time()
        
        tags = get_danbooru_tags_gemini(
            target_w.get('english', ''),
            target_w.get('korean', ''),
            target_w.get('hiragana', ''),
            target_w.get('exampleJp', ''),
            target_w.get('exampleKo', ''),
            target_cat
        )
        
        if tags:
            # Load, update and save atomically
            with open(cache_path, 'r', encoding='utf-8') as f:
                current_cache = json.load(f)
            current_cache[w_id] = tags
            
            temp_path = cache_path + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(current_cache, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, cache_path)
            print(f"  ✅ Saved: {tags}")
        else:
            print(f"  ⚠️ Failed. Skipping this word for retry in next loops.")
            
        # Enforce strict 4.5s delay to keep under 15 RPM
        elapsed = time.time() - start_time
        sleep_time = max(0.1, 4.5 - elapsed)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
