import os
import re
import gc
import glob
import unicodedata
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

seed_words_path = "data/seedWords.ts"
word_images_path = "data/wordImages.ts"
image_dir = "assets/images/words"

os.makedirs(image_dir, exist_ok=True)

legacy_prompts = {
    '1': ('나, 저', 'simple hand pointing to chest'),
    '2': ('당신', 'hand pointing forward'),
    '3': ('사람', 'person silhouette'),
    '4': ('집', 'cozy small house'),
    '5': ('역', 'train station platform'),
    '6': ('학교', 'school building'),
    '7': ('자동차', 'red cartoon car'),
    '8': ('물', 'glass of clear water'),
    '9': ('차(마시는)', 'cup of green tea with steam'),
    '10': ('책', 'open hardcover book'),
    '11': ('오늘', 'calendar page showing today'),
    '12': ('내일', 'sunrise behind hills'),
    '13': ('어제', 'sunset behind hills'),
    '14': ('선생님', 'teacher holding blackboard pointer'),
    '15': ('학생', 'student holding backpack'),
    '16': ('먹다', 'person eating delicious food'),
    '17': ('마시다', 'person drinking from a glass'),
    '18': ('가다', 'footprints walking forward'),
    '19': ('오다', 'person waving welcome'),
    '20': ('돌아가다', 'person walking towards cozy house'),
    '21': ('보다', 'pair of binoculars looking forward'),
    '22': ('듣다', 'hand to ear listening'),
    '23': ('이야기하다', 'two speech bubbles talking'),
    '24': ('읽다', 'person reading book under lamp'),
    '25': ('쓰다', 'hand writing with pen on paper'),
    '26': ('사다', 'hand holding a shopping bag'),
    '27': ('일어나다', 'person waking up in bed stretching'),
    '28': ('자다', 'cute baby sleeping in bed'),
    '29': ('크다', 'huge elephant standing next to small mouse'),
    '30': ('작다', 'tiny green ladybug leaf')
}

def clean_name(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFC', text)
    # Remove chars that are bad for filenames
    text = re.sub(r'[\\/*?:"<>|()\s,/]', '', text)
    return text.strip()

def rebuild_word_images():
    print("Rebuilding wordImages.ts...")
    png_files = glob.glob(os.path.join(image_dir, "*.png"))
    mappings = []
    for f in sorted(png_files):
        base = os.path.splitext(os.path.basename(f))[0]
        safe_key = f"'{base}'" if not base.isalnum() else base
        mappings.append(f"  {safe_key}: require('../assets/images/words/{base}.png'),")
        
    with open(word_images_path, 'w', encoding='utf-8') as f:
        f.write("export const wordImages: Record<string, any> = {\n")
        for m in mappings:
            f.write(m + "\n")
        f.write("};\n")
    print(f"Registered {len(mappings)} images in {word_images_path}.")

def main():
    if not os.path.exists(seed_words_path):
        print(f"⚠️ {seed_words_path} not found.")
        return
        
    # Read seedWords.ts
    with open(seed_words_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    updated = False
    words_to_generate = []
    
    # 1. Identify which legacy words need images
    for i, line in enumerate(lines):
        m_id = re.search(r"id:\s*'([1-9]|1[0-9]|2[0-9]|30)'", line)
        if m_id:
            w_id = m_id.group(1)
            # Check if it already has imageKey
            m_kanji = re.search(r"kanji:\s*'([^']*)'", line)
            m_hira = re.search(r"hiragana:\s*'([^']*)'", line)
            if "imageKey:" not in line and m_kanji and m_hira:
                kanji = m_kanji.group(1).strip()
                hira = m_hira.group(1).strip()
                original_word = kanji if kanji != '' else hira
                
                korean, prompt = legacy_prompts[w_id]
                clean_orig = clean_name(original_word)
                clean_kor = clean_name(korean)
                image_key = f"{w_id}_{clean_orig}_{clean_kor}"
                img_path = os.path.join(image_dir, f"{image_key}.png")
                
                # Check if image on disk exists
                if not os.path.exists(img_path):
                    words_to_generate.append((w_id, korean, prompt, image_key, i))
                else:
                    # Update line directly with imageKey
                    parts = line.split("status:")
                    if len(parts) == 2:
                        lines[i] = parts[0] + f"imageKey: '{image_key}', status:" + parts[1]
                        updated = True
                        
    if not words_to_generate and not updated:
        print("🎉 All legacy words 1-30 already have images!")
        return
        
    if words_to_generate:
        print(f"Need to generate {len(words_to_generate)} legacy images.")
        
        # Load Stable Diffusion
        print("Loading local Stable Diffusion model (dreamlike-art/dreamlike-anime-1.0)...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "dreamlike-art/dreamlike-anime-1.0", 
            torch_dtype=torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        pipe = pipe.to("mps")
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe.enable_attention_slicing()
        
        for w_id, korean, prompt_val, image_key, line_idx in words_to_generate:
            print(f"\nProcessing legacy word '{korean}' ({w_id}) with prompt '{prompt_val}'...")
            
            prompt = f"({prompt_val}:1.5), simple background, white background, solo object, modern clean design, game prop, UI asset, beautiful watercolor, studio ghibli color palette, high quality, masterpiece"
            negative_prompt = "complex background, scenery, landscape, messy, text, watermark, lowres, worst quality, low quality, blurry, human, person"
            
            try:
                with torch.inference_mode():
                    image = pipe(
                        prompt=prompt, 
                        negative_prompt=negative_prompt, 
                        num_inference_steps=15, 
                        guidance_scale=7.5
                    ).images[0]
                
                image_path = os.path.join(image_dir, f"{image_key}.png")
                image.save(image_path)
                print(f"  ✅ Image saved to {image_path}!")
                
                # Update line in lines list
                parts = lines[line_idx].split("status:")
                if len(parts) == 2:
                    lines[line_idx] = parts[0] + f"imageKey: '{image_key}', status:" + parts[1]
                    updated = True
                    
                # Write back immediately
                with open(seed_words_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                    
                rebuild_word_images()
                
                # Memory cleanup
                del image
                gc.collect()
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()
                    
            except Exception as e:
                print(f"  ❌ Generation failed: {e}")
                
    if updated:
        with open(seed_words_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Updated seedWords.ts successfully!")
        rebuild_word_images()

if __name__ == "__main__":
    main()
