import os
import json
import time
import argparse
from google import genai
from dotenv import load_dotenv

# Load env for Gemini API
env_path = os.path.join("word_card_generator", ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

default_categories_path = "utils/image_pipeline_v2/word_categories_all.json"
cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"

CATEGORY_GUIDANCE = {
    "concrete_nouns": {
        "text": "This is a physical object. Show ONE clear, iconic instance of it, centered and large, on a simple background. Usually NO people. Make the object instantly recognizable and not confusable with similar objects.",
        "use_example": False,
    },
    "abstract_nouns": {
        "text": "This is an abstract concept — often impossible to draw in isolation. Do NOT try to depict the word directly; instead depict the concrete SCENE from the example sentence below, since that scene is what makes the abstract meaning visible.",
        "use_example": True,
    },
    "action_verbs": {
        "text": "This is an action. Show exactly ONE person mid-action. The pose, hands, gaze, facial expression and surrounding context together must make THIS specific action obvious and clearly different from similar verbs. Use the example sentence to pick the right context if the action alone is ambiguous.",
        "use_example": True,
    },
    "adjectives_states": {
        "text": "This is a quality or emotional state. Convey it through the character's facial expression, body language and the mood of the environment, grounded in the situation from the example sentence. The state must be unmistakable.",
        "use_example": True,
    },
    "adverbs_functional": {
        "text": "This is a functional/grammatical word (adverb, conjunction, particle, counter, pronoun) — it has no picture of its own. You MUST depict the concrete scene from the example sentence below as a mini cause-and-effect or situational illustration; do not attempt to symbolize the word itself.",
        "use_example": True,
    },
}


def get_danbooru_tags(category, eng, kor, hiragana="", example_jp="", example_ko=""):
    if not eng or not str(eng).strip():
        eng = kor
    if not client:
        return eng

    sub_rule = ""
    if hiragana == 'あげる':
        sub_rule = "\nSPECIAL RULE for 'あげる' (to give): The character must be extending a gift forward, palms facing out (e.g. '1boy, looking at viewer, holding gift, extending arm forward, offering')."
    elif hiragana == 'くれる':
        sub_rule = "\nSPECIAL RULE for 'くれる' (to give to me): You MUST use the exact tag 'POV hands' or 'hands out of frame' offering a gift to the main character. Example: '1girl, looking at viewer, happy, receiving gift, POV hands offering gift'."
    elif hiragana == 'もらう':
        sub_rule = "\nSPECIAL RULE for '도라우' (to receive): The character must be holding a gift closely to their chest with both hands (e.g. '1girl, looking at viewer, holding gift to chest, both hands, happy smile')."
    elif hiragana == 'あやまる':
        sub_rule = "\nSPECIAL RULE for '謝る' (to apologize): A simple bow is TOO AMBIGUOUS (looks like a greeting or thanks). Show a SINGLE character with UNMISTAKABLE remorse: a very deep 90-degree bow with the head lowered and eyes closed, OR clasped hands pressed together while pleading. Always add remorse cues. Example: '1boy, deep bow, bowing deeply, head down, eyes closed, apologizing, remorseful, sorry, sweatdrop, hands together, indoors'. Do NOT use a casual polite bow, waving, or smiling."
    elif hiragana == 'それで':
        sub_rule = "\nSPECIAL RULE for 'それで' (because of that, so): Create an expressive scene showing a consequence or realization (e.g. '1boy, looking at viewer, pointing up, realization, lightbulb icon, explaining')."

    guidance = CATEGORY_GUIDANCE.get(category, {"text": "", "use_example": False})
    example_block = ""
    if guidance.get("use_example") and example_jp:
        example_block = f"""
Example sentence using this word (this is your primary visual source — depict THIS scene):
  Japanese: {example_jp}
  Korean: {example_ko}
"""

    prompt = f"""
You are an expert prompt engineer for a Stable Diffusion Anime model (Danbooru tags).
Generate tags for an educational Japanese vocabulary flashcard.
Word meaning: '{eng}' (Korean: '{kor}')
Category: {category}
Category guidance: {guidance.get("text", "")}
{example_block}
The illustration MUST be a peaceful, everyday-life scene. NEVER use fighting, extreme action, or surreal/violent concepts.

MOST IMPORTANT — DISAMBIGUATION & ACCURACY:
1. The picture must be identifiable as THIS EXACT word and nothing else. Many words look alike as pictures (e.g. apologize vs. greet vs. thank; run vs. walk; happy vs. surprised; give vs. receive; hot vs. spicy).
2. CRITICAL RULE FOR POLYSEMOUS WORDS: If the English word has multiple meanings (e.g. spring, bank, bar, head) or could lead to visual confusion, you MUST ignore the literal English meaning if the Korean translation indicates a specific context. The Korean meaning and the context sentence (if provided) are your absolute PRIMARY SOURCE of truth. Do NOT generate tags for incorrect meanings (e.g., do not draw a human head anatomy or mannequin for '수뇌' which means politicians/summit; do not draw a spring season for '스프링' which means metal coils; do not draw financial banks for '제방, 둑' which means river embankment).
3. A generic pose (e.g. just "bowing", "standing", "holding") is NOT acceptable when a more specific, meaning-revealing pose exists.

Output rules:
1. Output ONLY a comma-separated list of Danbooru tags. NO sentences, NO explanations.
2. For actions and emotional states, include exactly ONE human subject and VARY it (1boy, 1girl, businessman,
   student, child, old man, ...). Do NOT default to '1girl'.
3. For interactions (greeting, giving, talking), use a SINGLE character interacting with the viewer
   ('looking at viewer', 'POV hands', ...). Do NOT use 2+ characters — the model struggles with interactions.
4. Provide 6-10 highly descriptive tags, front-loading the ones that carry the specific meaning.
5. If an example sentence is given above, it is your PRIMARY source for the scene — build the tags around what is
   literally happening in that sentence, not a generic/textbook depiction of the word.
{sub_rule}

Few-shot Examples (note how each adds cues that rule out look-alike words):
Word: 'to run' (달리다) [action_verbs]
Tags: 1boy, school uniform, running, mid-stride, arms pumping, outdoors, park, motion blur, energetic

Word: 'to apologize' (사과하다) [action_verbs]
Tags: 1boy, deep bow, bowing deeply, head down, eyes closed, remorseful, sorry, sweatdrop, indoors

Word: 'umbrella' (우산) [concrete_nouns]
Tags: umbrella, open umbrella, single object, centered, raindrops, simple background, soft colors, no humans

Word: 'dream' (꿈) [abstract_nouns]
Tags: 1girl, sleeping, thought bubble, floating stars, soft glow, night, peaceful, dreamy atmosphere

Word: 'lonely' (외로운) [adjectives_states]
Tags: 1boy, sitting alone, empty bench, downcast eyes, melancholy, dim evening light, long shadow

Word: 'so, because of that' (그래서) [adverbs_functional], example: "雨が降っていました。それで、傘を持って行きました。" (비가 내려서 우산을 가지고 갔다)
Tags: 1girl, looking out window, rain outside, holding umbrella by the door, about to leave, cause and effect, everyday morning

Word: 'nerve, mind, feeling' (신경) [concrete_nouns], example: "気にしないでください。" (신경 쓰지 마세요)
Tags: 1boy, reassuring gesture, hand up, gentle smile, comforting another person off-frame, relieved atmosphere

Word: '{eng}' ({kor}) [{category}]
Tags:"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.5,
                )
            )
            tags = response.text.strip()
            if tags:
                return tags
        except Exception as e:
            print(f"  [Gemini API error (Attempt {attempt+1}/3)]: {e}")
            time.sleep(5)
    return None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--categories', type=str, default=default_categories_path,
                        help='Path to a {category: [words]} JSON')
    parser.add_argument('--limit', type=int, default=0, help='Max number of tags to extract (0 for all)')
    return parser.parse_args()


def main():
    args = parse_args()

    if not client:
        print("❌ Error: GEMINI_API_KEY is not set.")
        return

    # Load categories
    with open(args.categories, 'r', encoding='utf-8') as f:
        categories = json.load(f)

    # Load existing cache if any
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            print(f"Loaded existing cache with {len(cache)} tag entries.")
        except Exception as e:
            print(f"Error loading cache: {e}. Starting fresh.")

    # Flatten and filter out words that already have cache
    work_list = []
    for cat_name, words in categories.items():
        for w in words:
            w_id = w['id']
            if w_id not in cache:
                work_list.append((cat_name, w))

    if not work_list:
        print("Everything is already cached!")
        return

    print(f"Found {len(work_list)} uncached words to process.")
    
    if args.limit > 0:
        work_list = work_list[:args.limit]
        print(f"Limited processing to first {args.limit} words.")

    success_count = 0
    try:
        for i, (cat_name, w) in enumerate(work_list, 1):
            w_id = w['id']
            eng = w['english']
            kor = w['korean']
            hiragana = w.get('hiragana', '')
            example_jp = w.get('exampleJp', '')
            example_ko = w.get('exampleKo', '')

            print(f"[{i}/{len(work_list)}] Extracting tags for: {w_id} - {eng} ({kor})")
            
            tags = get_danbooru_tags(cat_name, eng, kor, hiragana, example_jp, example_ko)
            
            if tags:
                cache[w_id] = tags
                success_count += 1
                print(f"  ➔ Tags: {tags}")
            
            # Save cache incrementally to avoid loss on interrupt (Atomic Save)
            if success_count % 5 == 0 or i == len(work_list):
                temp_path = cache_path + ".tmp"
                try:
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, ensure_ascii=False, indent=2)
                    os.replace(temp_path, cache_path)
                    print(f"  💾 Saved cache atomically (total entries: {len(cache)})")
                except Exception as e:
                    print(f"  ⚠️ Error saving cache atomically: {e}. Falling back to normal write.")
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, ensure_ascii=False, indent=2)
            
            # Delay to comply with free-tier Gemini API rate limits
            time.sleep(3)

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving current cache...")
        temp_path = cache_path + ".tmp"
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, cache_path)
            print("Cache saved atomically.")
        except Exception as e:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            print("Cache saved successfully (fallback normal).")

    print(f"Done. Successfully processed {success_count} words.")


if __name__ == "__main__":
    main()
