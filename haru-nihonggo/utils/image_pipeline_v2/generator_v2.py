import os
import json
import argparse
import gc
import time
import torch
from diffusers import StableDiffusionXLPipeline
from diffusers import EulerAncestralDiscreteScheduler
from google import genai
from dotenv import load_dotenv

categories_path = "utils/image_pipeline_v2/word_categories.json"
output_dir = "assets/images/words_v2"

os.makedirs(output_dir, exist_ok=True)

# Load env for Gemini
env_path = os.path.join("word_card_generator", ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

PROMPT_TEMPLATES = {
    "concrete_nouns": {
        "suffix": "masterpiece, best quality, very aesthetic, absurdres, solo object, clear focus, studio lighting, highly detailed, (studio ghibli:1.3), (traditional media, watercolor:1.2)",
        "negative": "lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, signature, multiple objects, crowd, (modern anime style, flat shading:1.2)"
    },
    "abstract_nouns": {
        "suffix": "masterpiece, best quality, very aesthetic, absurdres, abstract concept, metaphorical visual, expressive, (studio ghibli:1.3), (traditional media, watercolor:1.2)",
        "negative": "lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, signature, literal object, realistic, photorealistic, (modern anime style, flat shading:1.2)"
    },
    "action_verbs": {
        "suffix": "masterpiece, best quality, very aesthetic, absurdres, everyday life, simple clear action, educational illustration, (studio ghibli:1.3), (traditional media, watercolor:1.2)",
        "negative": "lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, signature, fighting, extreme action, motion lines, (modern anime style, flat shading:1.2)"
    },
    "adjectives_states": {
        "suffix": "masterpiece, best quality, very aesthetic, absurdres, emotional mood, expressive environment, beautiful color palette, (studio ghibli:1.3), (traditional media, watercolor:1.2)",
        "negative": "lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, signature, (modern anime style, flat shading:1.2)"
    },
    "adverbs_functional": {
        "suffix": "masterpiece, best quality, very aesthetic, absurdres, clear situation, expressive characters, (studio ghibli:1.3), (traditional media, watercolor:1.2)",
        "negative": "lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, signature, photorealistic, confusing, (modern anime style, flat shading:1.2)"
    }
}

def get_danbooru_tags(category, eng, kor, hiragana=""):
    if not client:
        return eng
        
    sub_rule = ""
    if hiragana == 'あげる':
        sub_rule = "\\nSPECIAL RULE for 'あげる' (to give): The character must be extending a gift forward, palms facing out (e.g. '1boy, looking at viewer, holding gift, extending arm forward, offering')."
    elif hiragana == 'くれる':
        sub_rule = "\\nSPECIAL RULE for 'くれる' (to give to me): You MUST use the exact tag 'POV hands' or 'hands out of frame' offering a gift to the main character. Example: '1girl, looking at viewer, happy, receiving gift, POV hands offering gift'."
    elif hiragana == 'もらう':
        sub_rule = "\\nSPECIAL RULE for 'もらう' (to receive): The character must be holding a gift closely to their chest with both hands (e.g. '1girl, looking at viewer, holding gift to chest, both hands, happy smile')."
    elif hiragana == 'それで':
        sub_rule = "\\nSPECIAL RULE for 'それで' (because of that, so): Create an expressive scene showing a consequence or realization (e.g. '1boy, looking at viewer, pointing up, realization, lightbulb icon, explaining')."

    prompt = f"""
You are an expert prompt engineer for a Stable Diffusion Anime model (Danbooru tags).
The user wants to generate an illustration for the Japanese vocabulary word meaning: '{eng}' (Korean: '{kor}').
Category: {category}

Since this is for an educational vocabulary flashcard, the illustration MUST be a peaceful, everyday life scene. 
NEVER use tags related to fighting, extreme action, or surreal concepts.
Focus on clear, simple situations.

Crucial Rules:
1. Output ONLY a comma-separated list of Danbooru tags.
2. NO sentences, NO explanations, NO intro/outro text.
3. For action verbs and emotions, ALWAYS include a human subject (e.g. 1boy, 1girl, businessman, teacher, old man) to make the action clear.
4. Vary the human subjects! Do not just use '1girl'. Use '1boy', 'businessman', 'child', 'student', etc.
5. Provide around 5-10 highly descriptive tags.
6. For actions involving other people (like greeting, talking), ALWAYS make it a single character interacting with the viewer (e.g., '1boy, looking at viewer, waving, smiling'). Do NOT use 2 or more characters as the model struggles with interactions.
{sub_rule}

Few-shot Examples:
Word: 'to run' (달리다)
Tags: 1boy, school uniform, running, outdoors, park, day, looking at viewer, energetic

Word: 'to study' (공부하다)
Tags: 1girl, student, sitting at desk, reading book, taking notes, focused, bedroom, everyday life

Word: '{eng}' ({kor})
Tags:"""
    import time
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.7,
                )
            )
            tags = response.text.strip()
            if tags: return tags
        except Exception as e:
            print(f"  [Gemini API error (Attempt {attempt+1}/3)]: {e}")
            time.sleep(3)
    return eng

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', action='store_true', help='Generate 1 sample from each category')
    return parser.parse_args()

def main():
    args = parse_args()
    
    with open(categories_path, 'r', encoding='utf-8') as f:
        categories = json.load(f)
        
    print("Loading Animagine XL 3.1 model...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "cagliostrolab/animagine-xl-3.1", 
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to("mps")
    # pipe.enable_attention_slicing()  # Memory optimization if needed

    for cat_name, words in categories.items():
        if not words:
            continue
            
        print(f"\n--- Category: {cat_name} ---")
        
        words_to_process = []
        for w in words:
            if w.get('id') in ['n4_280', 'n4_247', 'n4_172']:
                words_to_process.append(w)
        
        if not words_to_process:
            continue
        
        for w in words_to_process:
            eng = w['english']
            kor = w['korean']
            w_id = w['id']
            hiragana = w.get('hiragana', '')
            
            print(f"Generating for: {eng} ({kor}) - {hiragana}")
            
            # Use Gemini to expand the word into Danbooru tags
            expanded_tags = get_danbooru_tags(cat_name, eng, kor, hiragana)
            print(f"  [Expanded Tags]: {expanded_tags}")
            
            template = PROMPT_TEMPLATES[cat_name]
            
            # Emphasize the core tags (weight 1.2) + the stylistic suffix
            prompt = f"({expanded_tags}:1.2), {template['suffix']}"
            negative = template['negative']
            
            try:
                with torch.inference_mode():
                    print("  Generating image...")
                    image = pipe(
                        prompt=expanded_tags + ", " + template["suffix"],
                        negative_prompt=template["negative"],
                        num_inference_steps=25,
                        guidance_scale=7.0,
                        width=832,
                        height=1216
                    ).images[0]
                
                japanese = w.get('kanji', '')
                if not japanese:
                    japanese = w.get('hiragana', '')
                japanese = japanese.replace(' ', '')
                safe_kor = kor.replace(' ', '').replace('/', '').replace(',', '')
                image_filename = f"{w_id}_{cat_name}_{japanese}_{safe_kor}.png"
                
                output_path = os.path.join(output_dir, image_filename)
                image.save(output_path)
                print(f"  ✅ Saved {image_filename}")
                
                del image
                gc.collect()
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()
                
                # Sleep to avoid Gemini API rate limits
                time.sleep(2)
                    
            except Exception as e:
                print(f"  ❌ Generation failed: {e}")

if __name__ == "__main__":
    main()
