import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load env for Gemini API
env_path = os.path.join("word_card_generator", ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in dotenv file!")

client = genai.Client(api_key=api_key)

CHUNK_PATH = "utils/image_pipeline_v2/chunks/chunk_5.json"
RESULT_PATH = "utils/image_pipeline_v2/chunks/result_5.json"

def make_prompt(word):
    kanji = word.get('kanji', '')
    hiragana = word.get('hiragana', '')
    english = word.get('english', '')
    korean = word.get('korean', '')
    exampleJp = word.get('exampleJp', '')
    exampleKo = word.get('exampleKo', '')
    
    prompt = f"""You are an expert prompt engineer for a Stable Diffusion Anime model (specifically Animagine XL 3.1 which uses Danbooru tags).
Generate descriptive, warm, Ghibli-style illustration tags for a Japanese vocabulary flashcard.

Word: '{kanji}' ({hiragana})
English Meaning: '{english}'
Korean Meaning: '{korean}'
Example Sentence:
  Japanese: {exampleJp}
  Korean: {exampleKo}

Output rules:
1. Output ONLY a comma-separated list of Danbooru tags (English). NO sentences, NO explanations, NO quotes, NO introduction, NO markdown codeblocks. Just the tags themselves.
2. Output 6-10 highly descriptive visual tags that depict the meaning of the word or the context of the example sentence.
3. The illustration style MUST be a warm, peaceful, Ghibli-style scene. You MUST include tags like 'ghibli style', 'watercolor', 'warm lighting', 'soft colors' to achieve the desired aesthetic.
4. For actions and emotional states, include exactly ONE human subject (e.g. 1boy, 1girl, businessman, student, child, old man, etc.). Front-load the tag representing the character, pose, or main action.
5. Keep the scene peaceful and warm. Never use fighting, violence, extreme action, or modern flat anime shading.

Example output:
1girl, reading book, warm sunlight, cozy library, soft shadow, ghibli style, watercolor, aesthetic
"""
    return prompt

def generate_tags_for_word(word):
    prompt = make_prompt(word)
    w_id = word['id']
    
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.5,
                )
            )
            text = response.text.strip()
            # Clean up the output tags
            # Remove markdown formatting if any
            if text.startswith("```"):
                lines = text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                text = "\n".join(lines).strip()
            
            # Remove any trailing or leading quotes
            text = text.replace('"', '').replace('`', '').strip()
            # If it starts with 'Tags:', strip it
            if text.lower().startswith("tags:"):
                text = text[5:].strip()
            
            # Simple check
            tags = [t.strip() for t in text.split(",") if t.strip()]
            cleaned_tags_str = ", ".join(tags)
            
            if len(tags) >= 3: # sanity check
                return w_id, cleaned_tags_str
            else:
                print(f"  [Attempt {attempt+1}] Got malformed output for {w_id}: {text}")
        except Exception as e:
            print(f"  [Attempt {attempt+1}] Gemini API error for {w_id}: {e}")
            
        time.sleep(2 * (attempt + 1))
        
    return w_id, None

def main():
    # Load input chunk
    with open(CHUNK_PATH, 'r', encoding='utf-8') as f:
        words = json.load(f)
    
    # Load existing results if any (for resuming)
    results = {}
    if os.path.exists(RESULT_PATH):
        try:
            with open(RESULT_PATH, 'r', encoding='utf-8') as f:
                results = json.load(f)
            print(f"Loaded {len(results)} existing results.")
        except Exception as e:
            print(f"Error loading existing results: {e}. Starting fresh.")
            
    # Filter out already processed words
    todo = [w for w in words if w['id'] not in results]
    total_todo = len(todo)
    print(f"Total words: {len(words)}, Already processed: {len(results)}, Todo: {total_todo}")
    
    if total_todo == 0:
        print("All words already processed!")
        return

    # Use ThreadPoolExecutor to request concurrently
    # Since we might run into rate limits, let's keep max_workers at 5
    max_workers = 5
    completed = len(results)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(generate_tags_for_word, w): w for w in todo}
        
        for future in as_completed(futures):
            word = futures[future]
            w_id, tags = future.result()
            
            if tags:
                results[w_id] = tags
                completed += 1
                print(f"[{completed}/{len(words)}] Processed {w_id} ({word.get('kanji') or word.get('english')}): {tags}")
                
                # Periodically save results atomically
                if completed % 5 == 0 or completed == len(words):
                    temp_path = RESULT_PATH + ".tmp"
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    os.replace(temp_path, RESULT_PATH)
            else:
                print(f"❌ Failed to process {w_id} ({word.get('kanji') or word.get('english')}) after all attempts.")
                
    # Final save
    temp_path = RESULT_PATH + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, RESULT_PATH)
    print(f"Successfully wrote all results to {RESULT_PATH}.")

if __name__ == "__main__":
    main()
