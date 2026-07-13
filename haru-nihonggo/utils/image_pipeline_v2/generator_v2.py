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

# 카테고리별로 "어떤 그림이어야 하는지" 일반 지침 (단어별 하드코딩 대신 전 단어에 적용)
CATEGORY_GUIDANCE = {
    "concrete_nouns": "This is a physical object. Show ONE clear, iconic instance of it, centered and large, on a simple background. Usually NO people. Make the object instantly recognizable and not confusable with similar objects.",
    "abstract_nouns": "This is an abstract concept. Depict it with a single clear visual metaphor or a symbolic scene that evokes the concept. Make the mood or symbol unambiguous.",
    "action_verbs": "This is an action. Show exactly ONE person mid-action. The pose, hands, gaze, facial expression and surrounding context together must make THIS specific action obvious and clearly different from similar verbs.",
    "adjectives_states": "This is a quality or emotional state. Convey it through the character's facial expression, body language and the mood of the environment. The state must be unmistakable.",
    "adverbs_functional": "This is a functional/adverbial word. Show a concrete everyday situation that clearly exemplifies the word, using an expressive single character.",
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
    elif hiragana == 'あやまる':
        sub_rule = "\\nSPECIAL RULE for '謝る' (to apologize): A simple bow is TOO AMBIGUOUS (looks like a greeting or thanks). Show a SINGLE character with UNMISTAKABLE remorse: a very deep 90-degree bow with the head lowered and eyes closed, OR clasped hands pressed together while pleading. Always add remorse cues. Example: '1boy, deep bow, bowing deeply, head down, eyes closed, apologizing, remorseful, sorry, sweatdrop, hands together, indoors'. Do NOT use a casual polite bow, waving, or smiling."
    elif hiragana == 'それで':
        sub_rule = "\\nSPECIAL RULE for 'それで' (because of that, so): Create an expressive scene showing a consequence or realization (e.g. '1boy, looking at viewer, pointing up, realization, lightbulb icon, explaining')."

    category_guidance = CATEGORY_GUIDANCE.get(category, "")

    prompt = f"""
You are an expert prompt engineer for a Stable Diffusion Anime model (Danbooru tags).
Generate tags for an educational Japanese vocabulary flashcard.
Word meaning: '{eng}' (Korean: '{kor}')
Category: {category}
Category guidance: {category_guidance}

The illustration MUST be a peaceful, everyday-life scene. NEVER use fighting, extreme action, or surreal/violent concepts.

MOST IMPORTANT — DISAMBIGUATION:
The picture must be identifiable as THIS EXACT word and nothing else. Many words look alike as pictures
(e.g. apologize vs. greet vs. thank; run vs. walk; happy vs. surprised; give vs. receive; hot vs. spicy).
Whenever the meaning could be confused with a related word, you MUST add explicit disambiguating cues — a
distinctive facial expression, a specific hand/body posture, or a context prop — that positively rule out the
similar meanings. A generic pose (e.g. just "bowing", "standing", "holding") is NOT acceptable when a more
specific, meaning-revealing pose exists.

Output rules:
1. Output ONLY a comma-separated list of Danbooru tags. NO sentences, NO explanations.
2. For actions and emotional states, include exactly ONE human subject and VARY it (1boy, 1girl, businessman,
   student, child, old man, ...). Do NOT default to '1girl'.
3. For interactions (greeting, giving, talking), use a SINGLE character interacting with the viewer
   ('looking at viewer', 'POV hands', ...). Do NOT use 2+ characters — the model struggles with interactions.
4. Provide 6-10 highly descriptive tags, front-loading the ones that carry the specific meaning.
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

Word: '{eng}' ({kor}) [{category}]
Tags:"""
    import time
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
            if tags: return tags
        except Exception as e:
            print(f"  [Gemini API error (Attempt {attempt+1}/3)]: {e}")
            time.sleep(3)
    return eng

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', action='store_true', help='Generate 1 sample from each category')
    parser.add_argument('--ids', type=str, default='', help='Comma-separated word ids to generate (e.g. n4_118,n4_190)')
    parser.add_argument('--count', type=int, default=0, help='Generate the first N words across all categories')
    parser.add_argument('--overwrite', action='store_true', help='Regenerate even if the image already exists')
    parser.add_argument('--categories', type=str, default=categories_path,
                        help='Path to a {category: [words]} JSON (default: N4 word_categories.json)')
    return parser.parse_args()


def build_work_list(categories, args):
    """Return an ordered list of (category_name, word) pairs to generate."""
    ids = [x.strip() for x in args.ids.split(',') if x.strip()]
    if ids:
        index = {}
        for cat, words in categories.items():
            for w in words:
                index[w['id']] = (cat, w)
        work = []
        for wid in ids:  # preserve the requested order
            if wid in index:
                work.append(index[wid])
            else:
                print(f"  ⚠️ id not found in categories: {wid}")
        return work
    if args.sample:
        return [(cat, words[0]) for cat, words in categories.items() if words]
    if args.count:
        flat = [(cat, w) for cat, words in categories.items() for w in words]
        return flat[:args.count]
    return []


def output_path_for(cat_name, w):
    japanese = (w.get('kanji') or w.get('hiragana', '')).replace(' ', '')
    safe_kor = w['korean'].replace(' ', '').replace('/', '').replace(',', '')
    filename = f"{w['id']}_{cat_name}_{japanese}_{safe_kor}.png"
    return filename, os.path.join(output_dir, filename)


def main():
    args = parse_args()

    with open(args.categories, 'r', encoding='utf-8') as f:
        categories = json.load(f)

    work = build_work_list(categories, args)
    if not work:
        print("아무 것도 생성하지 않습니다. --ids, --count, 또는 --sample 중 하나를 지정하세요.")
        return

    # Skip already-generated images unless --overwrite
    if not args.overwrite:
        work = [(c, w) for (c, w) in work if not os.path.exists(output_path_for(c, w)[1])]
        if not work:
            print("대상 이미지가 이미 모두 존재합니다. (--overwrite 로 재생성)")
            return

    # 손으로 작성한 큐레이션 태그 로드 (id가 있으면 Gemini보다 우선 사용)
    curated = {}
    curated_path = "utils/image_pipeline_v2/curated_tags.json"
    if os.path.exists(curated_path):
        with open(curated_path, 'r', encoding='utf-8') as f:
            curated = {k: v for k, v in json.load(f).items() if not k.startswith('_')}
        print(f"큐레이션 태그 {len(curated)}개 로드됨.")

    print(f"총 {len(work)}개 이미지를 생성합니다.")
    print("Loading Animagine XL 3.1 model...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "cagliostrolab/animagine-xl-3.1",
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to("mps")
    # pipe.enable_attention_slicing()  # Memory optimization if needed

    for i, (cat_name, w) in enumerate(work, 1):
        eng = w['english']
        kor = w['korean']
        hiragana = w.get('hiragana', '')

        print(f"\n[{i}/{len(work)}] Generating for: {eng} ({kor}) - {hiragana} [{cat_name}]")

        # 큐레이션 태그가 있으면 우선 사용, 없으면 Gemini로 확장
        curated_tags = curated.get(w['id'])
        if curated_tags:
            expanded_tags = curated_tags
            print(f"  [Curated Tags]: {expanded_tags}")
        else:
            expanded_tags = get_danbooru_tags(cat_name, eng, kor, hiragana)
            print(f"  [Gemini Tags]: {expanded_tags}")

        template = PROMPT_TEMPLATES.get(cat_name)
        if template is None:
            print(f"  ⚠️ 알 수 없는 카테고리 '{cat_name}', 건너뜀")
            continue

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

            filename, output_path = output_path_for(cat_name, w)
            image.save(output_path)
            print(f"  ✅ Saved {filename}")

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
