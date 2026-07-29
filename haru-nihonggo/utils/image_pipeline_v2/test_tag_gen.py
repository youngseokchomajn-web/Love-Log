import os
import json
import time
from google import genai
from dotenv import load_dotenv

# Load dotenv
env_path = os.path.join("word_card_generator", ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in env.")
    exit(1)

client = genai.Client(api_key=api_key)

# Read chunk_2.json
with open('utils/image_pipeline_v2/chunks/chunk_2.json', 'r', encoding='utf-8') as f:
    words = json.load(f)

# Take first 3 words for test
test_words = words[:3]

prompt = f"""You are an expert prompt engineer for a Stable Diffusion model.
Your task is to generate descriptive, warm, Ghibli-style illustration tags for Japanese vocabulary learning cards.

For each word provided in the JSON list, generate 6-10 descriptive, warm, Ghibli-style illustration tags based on its definition (Korean/English) and Japanese example sentence.
The tags should describe a peaceful, everyday-life scene in Ghibli style (warm tones, watercolor-like, detailed background, soft lighting, cozy atmosphere).
Do not use generic tags only; ensure the specific meaning of the word or the scene in the example sentence is visually depicted.
All tags must be in English.

You must respond with a JSON object where the keys are the word 'id's, and the values are the generated tags as a single string of comma-separated tags.
Format of response:
{{
  "word_id_1": "tag1, tag2, tag3, ghibli style, warm lighting, ...",
  "word_id_2": "..."
}}

Do not include any markdown formatting like ```json or ``` in your response, just the raw JSON text.

Input words:
{json.dumps(test_words, ensure_ascii=False, indent=2)}
"""

print("Sending request to Gemini...")
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=0.4,
            response_mime_type="application/json"
        )
    )
    print("Response received:")
    print(response.text)
    result = json.loads(response.text.strip())
    print("Parsed JSON successfully:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error: {e}")
