import os
import json
import time
from google import genai
from dotenv import load_dotenv

# Load env variables for Gemini API
env_path = os.path.join("word_card_generator", ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY is not set.")
    exit(1)

client = genai.Client(api_key=api_key)

input_file = "utils/image_pipeline_v2/chunks/chunk_2.json"
output_file = "utils/image_pipeline_v2/chunks/result_2.json"

# Load words chunk
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found.")
    exit(1)

with open(input_file, 'r', encoding='utf-8') as f:
    words = json.load(f)

# Load existing results if any (for resume capability)
results = {}
if os.path.exists(output_file):
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        print(f"Loaded existing results: {len(results)} items.")
    except Exception as e:
        print(f"Warning: Failed to load existing output file: {e}. Starting fresh.")

# Filter out words that already have generated tags
words_to_process = [w for w in words if w['id'] not in results]
print(f"Total words: {len(words)}, Words to process: {len(words_to_process)}")

if not words_to_process:
    print("All words already processed. Done!")
    exit(0)

# Batch size for Gemini API requests
BATCH_SIZE = 15
batches = [words_to_process[i:i + BATCH_SIZE] for i in range(0, len(words_to_process), BATCH_SIZE)]

system_instruction = """You are an expert prompt engineer for a Stable Diffusion model.
Your task is to generate descriptive, warm, Ghibli-style illustration tags for Japanese vocabulary learning cards.

For each word provided in the JSON list, generate exactly 6-10 descriptive, warm, Ghibli-style illustration tags based on its definition (Korean/English) and Japanese example sentence.
The tags must describe a peaceful, everyday-life scene in Ghibli style (warm tones, watercolor-like, detailed background, soft lighting, cozy atmosphere).
Do not use generic tags only; ensure the specific meaning of the word or the scene in the example sentence is visually depicted.
All tags must be in English.

Output constraints:
1. Each tag must be a short word or phrase (e.g., "1boy", "grassy hill", "warm lighting", "watercolor style", "ghibli style", "cozy room").
2. Do NOT write complete long sentences or paragraphs as tags.
3. For each word, return a single string of 6-10 comma-separated tags.
4. You must respond with a JSON object where the keys are the word 'id's and the values are the generated tags as a single string.
"""

def generate_tags_for_batch(batch_words):
    prompt = f"""Generate tags for the following list of Japanese vocabulary words:
{json.dumps(batch_words, ensure_ascii=False, indent=2)}

Return a JSON object matching this structure:
{{
  "word_id_1": "tag1, tag2, tag3, watercolor style, ghibli style, warm lighting",
  "word_id_2": "tag1, tag2, tag3, cozy room, ghibli style"
}}
Do not include any markdown styling (like ```json). Return only the raw JSON.
"""
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text.strip())
            return data
        except Exception as e:
            print(f"  [Error in attempt {attempt+1}/3]: {e}")
            time.sleep(5)
    return None

# Process batches
success_count = 0
for idx, batch in enumerate(batches, 1):
    print(f"Processing batch {idx}/{len(batches)} ({len(batch)} words)...")
    batch_results = generate_tags_for_batch(batch)
    
    if batch_results:
        for w in batch:
            w_id = w['id']
            if w_id in batch_results:
                results[w_id] = batch_results[w_id]
                success_count += 1
            else:
                # Fallback if specific ID was missed in JSON response
                print(f"  Warning: ID {w_id} was missing in response.")
        
        # Save progress incrementally
        temp_file = output_file + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, output_file)
        print(f"  Saved progress: {len(results)} words.")
    else:
        print(f"  Failed to generate tags for batch {idx}.")
    
    # Delay to respect API limits
    time.sleep(3)

print(f"Finished processing. Total successfully generated words: {success_count}.")
# Double check: ensure output matches input order or covers all.
print("Done!")
