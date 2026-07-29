import os
import json
import argparse
import gc
import time
import torch
import numpy as np
import re
import unicodedata
from diffusers import StableDiffusionXLPipeline
from diffusers import EulerAncestralDiscreteScheduler
from google import genai
from dotenv import load_dotenv


def is_degenerate_frame(pil_image):
    """SDXL+fp16+MPS에서 드물게 VAE 디코딩이 NaN을 내 완전 검은(또는 단색) 프레임이
    나온다. 픽셀 표준편차가 1.0 미만이거나 최대/최소 격차가 거의 없으면 깨진 프레임으로 판정한다."""
    arr = np.asarray(pil_image.convert('RGB'), dtype=np.float32)
    if arr.std() < 1.0:
        return True
    if (arr.max() - arr.min()) < 3.0:
        return True
    return False


categories_path = "utils/image_pipeline_v2/word_categories_all.json" if os.path.exists("utils/image_pipeline_v2/word_categories_all.json") else "utils/image_pipeline_v2/word_categories.json"

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


def parse_args():
    parser = argparse.ArgumentParser(description='Generate SDXL vocabulary images')
    parser.add_argument('--level', type=str, default='all', help='Target JLPT level (n1, n2, n3, n4, n5, or all)')
    parser.add_argument('--sample', action='store_true', help='Generate 1 sample image per category for testing')
    parser.add_argument('--ids', type=str, default='', help='Comma-separated word ids to generate (e.g. n4_118,n4_190)')
    parser.add_argument('--regenerate-list', type=str, default='', help='Path to image_regeneration_list.json')
    parser.add_argument('--count', type=int, default=0, help='Generate the first N words across all categories')
    parser.add_argument('--overwrite', action='store_true', help='Regenerate even if the image already exists')
    parser.add_argument('--categories', type=str, default=categories_path,
                        help='Path to a {category: [words]} JSON')
    parser.add_argument('--output_dir', type=str, default="assets/images/words_v3",
                        help='Directory to save generated images')
    return parser.parse_args()


def build_work_list(categories, args):
    """Return an ordered list of (category_name, word) pairs to generate."""
    if args.regenerate_list and os.path.exists(args.regenerate_list):
        with open(args.regenerate_list, 'r', encoding='utf-8') as f:
            items = json.load(f)
        ids = [x['id'] for x in items]
        index = {}
        for cat, words in categories.items():
            for w in words:
                index[w['id']] = (cat, w)
        work = []
        for wid in ids:
            if wid in index:
                work.append(index[wid])
            else:
                print(f"  ⚠️ id not found in categories: {wid}")
        return work

    ids = [x.strip() for x in args.ids.split(',') if x.strip()]
    if ids:
        index = {}
        for cat, words in categories.items():
            for w in words:
                index[w['id']] = (cat, w)
        work = []
        for wid in ids:
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


def clean_filename_korean(korean):
    cleaned = re.sub(r'[\s/,;\?:\*\"<>\|\\\.\(\)\[\]\{\}]', '', korean)
    return unicodedata.normalize('NFC', cleaned)


def clean_filename_japanese(jp):
    cleaned = jp.replace(' ', '')
    cleaned = re.sub(r'[\s/,;\?:\*\"<>\|\\\.\(\)\[\]\{\}〜~]', '', cleaned)
    return unicodedata.normalize('NFC', cleaned)


def output_path_for(cat_name, w, output_dir):
    level = w.get('level') or 'n4'
    japanese = clean_filename_japanese(w.get('kanji') or w.get('hiragana', ''))
    safe_kor = clean_filename_korean(w['korean'])
    filename = f"{level}_{japanese}_{safe_kor}.jpg"
    return filename, os.path.join(output_dir, filename)


def save_failed_word(w_id, w, reason, output_dir):
    failed_path = os.path.join(output_dir, "failed_generation.json")
    failed_data = {}
    if os.path.exists(failed_path):
        try:
            with open(failed_path, 'r', encoding='utf-8') as f:
                failed_data = json.load(f)
        except Exception:
            pass
    failed_data[w_id] = {
        "japanese": w.get('kanji') or w.get('hiragana', ''),
        "korean": w.get('korean', ''),
        "reason": str(reason)
    }
    temp_path = failed_path + ".tmp"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(failed_data, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, failed_path)
    except Exception:
        with open(failed_path, 'w', encoding='utf-8') as f:
            json.dump(failed_data, f, ensure_ascii=False, indent=2)


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.categories, 'r', encoding='utf-8') as f:
        categories = json.load(f)

    work = build_work_list(categories, args)
    if not work:
        print("아무 것도 생성하지 않습니다. --ids, --regenerate-list, --count, 또는 --sample 중 하나를 지정하세요.")
        return

    # Skip already-generated images unless --overwrite
    if not args.overwrite:
        def already_exists(c, w):
            _, jpg_path = output_path_for(c, w, args.output_dir)
            png_path = jpg_path.replace('.jpg', '.png')
            return os.path.exists(jpg_path) or os.path.exists(png_path)
        work = [(c, w) for (c, w) in work if not already_exists(c, w)]
        if not work:
            print("대상 이미지가 이미 모두 존재합니다. (--overwrite 로 재생성)")
            return

    # 큐레이션 태그 로드
    curated = {}
    curated_path = "utils/image_pipeline_v2/curated_tags.json"
    if os.path.exists(curated_path):
        with open(curated_path, 'r', encoding='utf-8') as f:
            curated = {k: v for k, v in json.load(f).items() if not k.startswith('_')}

    # 캐시된 태그 로드
    cache = {}
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        print(f"캐시 태그 {len(cache)}개 로드됨.")

    print(f"총 {len(work)}개 이미지를 생성합니다.")
    print("Loading Animagine XL 3.1 model...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "cagliostrolab/animagine-xl-3.1",
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    
    # Load Hyper-SD 4-steps LoRA for ultra-fast generation
    print("Loading Hyper-SD 4-steps LoRA...")
    pipe.load_lora_weights("ByteDance/Hyper-SD", weight_name="Hyper-SDXL-4steps-lora.safetensors")
    pipe.fuse_lora()
    
    pipe = pipe.to("mps")

    for i, (cat_name, w) in enumerate(work, 1):
        w_id = w['id']
        eng = w.get('english', '')
        kor = w['korean']
        hiragana = w.get('hiragana', '')
        example_jp = w.get('exampleJp', '')
        example_ko = w.get('exampleKo', '')

        print(f"\n[{i}/{len(work)}] Generating for: {eng} ({kor}) - {hiragana} [{cat_name}]")

        curated_tags = curated.get(w_id)
        cached_tags = cache.get(w_id)
        if curated_tags:
            expanded_tags = curated_tags
            print(f"  [Curated Tags]: {expanded_tags}")
        elif cached_tags:
            expanded_tags = cached_tags
            print(f"  [Cached Tags]: {expanded_tags}")
        else:
            print(f"  ⚠️ 태그가 존재하지 않습니다 (id={w_id}), 스킵합니다.")
            continue

        template = PROMPT_TEMPLATES.get(cat_name, PROMPT_TEMPLATES["concrete_nouns"])

        try:
            image = None
            for attempt in range(3):
                with torch.inference_mode():
                    if attempt == 0:
                        print("  Generating image...")
                    else:
                        print(f"  ⚠️ 검은/단색 프레임 감지, 재시도 {attempt+1}/3...")
                    candidate = pipe(
                        prompt=expanded_tags + ", " + template["suffix"],
                        negative_prompt=template["negative"],
                        num_inference_steps=4,
                        guidance_scale=1.2,
                        width=768,
                        height=768
                    ).images[0]
                if not is_degenerate_frame(candidate):
                    image = candidate
                    break
            
            if image is None:
                err_msg = "All 3 generation attempts returned degenerate (NaN) frame"
                print(f"  ❌ {err_msg} — 건너뜀 (id={w_id})")
                save_failed_word(w_id, w, err_msg, args.output_dir)
                continue

            filename, output_path = output_path_for(cat_name, w, args.output_dir)
            image.convert('RGB').save(output_path, format='JPEG', quality=88, optimize=True)
            print(f"  ✅ Saved {filename}")

            del image
            gc.collect()
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()

            time.sleep(0.5)

        except Exception as e:
            print(f"  ❌ Generation failed: {e}")
            save_failed_word(w_id, w, f"Exception: {e}", args.output_dir)


if __name__ == "__main__":
    main()
