import os
import re
import sys
import glob
import json
import time
import argparse
import pandas as pd
import unicodedata
from google import genai
from dotenv import load_dotenv

excel_path = "data/jlpt_n4_clean_merged.xlsx"
word_images_path = "data/wordImages.ts"
seed_words_path = "data/seedWords.ts"
image_dir = "assets/images/words"

os.makedirs(image_dir, exist_ok=True)

# Load env
env_path = os.path.join("word_card_generator", ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None, help='Limit number of images to generate')
    return parser.parse_args()

def clean_name(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFC', text)
    # Remove chars that are bad for filenames
    text = re.sub(r'[\\/*?:"<>|()\s,/]', '', text)
    return text.strip()

def parse_existing_original_words():
    words = []
    if not os.path.exists(seed_words_path):
        return words
        
    seen_ids = set()
    with open(seed_words_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "id: '" in line:
                m_id = re.search(r"id:\s*'([^']+)'", line)
                m_kanji = re.search(r"kanji:\s*'([^']*)'", line)
                m_hira = re.search(r"hiragana:\s*'([^']*)'", line)
                m_pron = re.search(r"pronunciation:\s*'([^']*)'", line)
                m_korean = re.search(r"korean:\s*'([^']*)'", line)
                m_image = re.search(r"imageKey:\s*'([^']*)'", line)
                
                if m_id and m_kanji and m_hira and m_pron and m_korean:
                    w_id = m_id.group(1)
                    if w_id.isdigit() and int(w_id) <= 45:
                        if w_id not in seen_ids:
                            seen_ids.add(w_id)
                            entry = {
                                'id': w_id,
                                'kanji': m_kanji.group(1),
                                'hiragana': m_hira.group(1),
                                'pronunciation': m_pron.group(1),
                                'korean': m_korean.group(1),
                                'imageKey': m_image.group(1) if m_image else None
                            }
                            words.append(entry)
    return words

def rebuild_code_files(df, original_words):
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
    
    print("Rebuilding seedWords.ts...")
    with open(seed_words_path, 'w', encoding='utf-8') as f:
        f.write("export const seedWords = [\n")
        for ew in original_words:
            img_str = f", imageKey: '{ew['imageKey']}'" if ew['imageKey'] else ''
            f.write(f"  {{ id: '{ew['id']}', kanji: '{ew['kanji']}', hiragana: '{ew['hiragana']}', pronunciation: '{ew['pronunciation']}', korean: '{ew['korean']}'{img_str}, status: 'new', nextReviewDate: Date.now(), interval: 0, easeFactor: 2.5, incorrectCount: 0 }},\n")
            
        for _, row in df.iterrows():
            w_id = str(row['ID']).strip()
            if w_id.isdigit() and int(w_id) <= 45:
                continue
                
            kanji = str(row['한자']).strip() if pd.notna(row['한자']) else ''
            hira = str(row['히라가나']).strip()
            pron = str(row['한글 발음']).strip()
            korean = str(row['한국어 뜻']).strip()
            english = str(row['영어 뜻']).strip() if pd.notna(row['영어 뜻']) else ''
            image_key = str(row['이미지 키']).strip() if ('이미지 키' in df.columns and pd.notna(row['이미지 키']) and str(row['이미지 키']).strip() != '') else ''
            
            korean_esc = korean.replace("'", "\\'")
            english_esc = english.replace("'", "\\'")
            img_str = f", imageKey: '{image_key}'" if image_key else ''
            
            f.write(f"  {{ id: '{w_id}', kanji: '{kanji}', hiragana: '{hira}', pronunciation: '{pron}', korean: '{korean_esc}', english: '{english_esc}'{img_str}, status: 'new', nextReviewDate: Date.now(), interval: 0, easeFactor: 2.5, incorrectCount: 0 }},\n")
            
        f.write("];\n")
    print(f"Wrote all words to {seed_words_path}.")

def expand_prompts_batch(df, client):
    rows_to_expand = []
    for index, row in df.iterrows():
        w_id = str(row['ID']).strip()
        if w_id.isdigit() and int(w_id) <= 45:
            continue
        current_prompt = str(row['비주얼 프롬프트']).strip()
        if current_prompt == '' or pd.isna(row['비주얼 프롬프트']) or current_prompt == 'nan':
            rows_to_expand.append((index, w_id, str(row['한국어 뜻']).strip(), str(row['영어 뜻']).strip() if pd.notna(row['영어 뜻']) else ''))
            
    if not rows_to_expand:
        print("💡 All prompts are already expanded!")
        return
        
    print(f"Expanding prompts for {len(rows_to_expand)} words in batches of 50 using Gemini...")
    batch_size = 50
    for i in range(0, len(rows_to_expand), batch_size):
        batch = rows_to_expand[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(rows_to_expand)-1)//batch_size + 1}...")
        
        test_words = [{'id': item[1], 'korean': item[2], 'english': item[3]} for item in batch]
        
        prompt_text = f"""
        당신은 일본어 단어 학습용 카드 게임의 이미지 생성을 돕는 전문가입니다.
        주어진 단어 리스트의 모든 단어에 대해 **반드시 구체적으로 묘사 가능한 시각화 프롬프트(2-5단어의 영어 명사구)**를 작성하십시오.
        절대 'UNVISUAL'이나 빈칸을 출력하지 마십시오. 모든 단어는 100% 시각화되어야 합니다.

        상징/은유 가이드라인:
        - 구체적인 대상이 없는 부사, 접속사, 형용사 등은 그 의미를 직관적으로 연상시킬 수 있는 기호, 상징, 은유 또는 구체적인 행동 상황으로 변환하십시오.
          * 예: '그리고' (and) -> 'two puzzle pieces connecting'
          * 예: '매우' (very) -> 'a thermometer bursting with red liquid'
          * 예: '사이' (between) -> 'a small green sprout growing between two large gray stones'
          * 예: '맞는' (correct/fit) -> 'a glowing green checkmark icon'
          * 예: '나' (I/me) -> 'a simple hand pointing to chest'
          * 예: '당신' (you) -> 'a hand pointing forward'

        다음 JSON 형식의 리스트로 응답하십시오:
        [
          {{"id": "단어ID", "prompt": "영어 명사구"}}
        ]

        단어 리스트:
        {json.dumps(test_words, ensure_ascii=False)}
        """
        
        success = False
        retries = 3
        while not success and retries > 0:
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_text,
                    config={'response_mime_type': 'application/json'}
                )
                res_data = json.loads(response.text.strip())
                
                # Map back to df
                mapping = {item['id']: item['prompt'] for item in res_data}
                for index_df, w_id, _, _ in batch:
                    val = mapping.get(w_id, '')
                    if not val or val == 'UNVISUAL':
                        val = 'symbolic icon' # Fallback safety
                    df.at[index_df, '비주얼 프롬프트'] = val
                    
                df.to_excel(excel_path, index=False)
                success = True
                print("  ✅ Batch completed successfully.")
                
            except Exception as e:
                print(f"  ⚠️ Error in batch: {e}. Retrying in 10s...")
                time.sleep(10)
                retries -= 1
                
        if i + batch_size < len(rows_to_expand):
            print("  ⏳ Waiting 5 seconds before next batch...")
            time.sleep(5)

def main():
    args = parse_args()
    
    if not os.path.exists(excel_path):
        print(f"⚠️ Excel file not found: {excel_path}")
        return
        
    df = pd.read_excel(excel_path)
    
    if '이미지 키' not in df.columns:
        df['이미지 키'] = ''
    if '비주얼 프롬프트' not in df.columns:
        df['비주얼 프롬프트'] = ''
        
    df['이미지 키'] = df['이미지 키'].astype(str).replace('nan', '')
    df['비주얼 프롬프트'] = df['비주얼 프롬프트'].astype(str).replace('nan', '')
    
    # RESET 'UNVISUAL' entries so they get re-expanded with the new metaphor rule
    reset_count = 0
    for index, row in df.iterrows():
        if str(row['비주얼 프롬프트']).strip() == 'UNVISUAL':
            df.at[index, '비주얼 프롬프트'] = ''
            df.at[index, '이미지 키'] = ''
            reset_count += 1
    if reset_count > 0:
        df.to_excel(excel_path, index=False)
        print(f"🔄 Reset {reset_count} 'UNVISUAL' entries for metaphorical prompt expansion.")
        
    original_words = parse_existing_original_words()
    
    # 1. Expand prompts using Gemini in batch
    if api_key:
        client = genai.Client(api_key=api_key)
        expand_prompts_batch(df, client)
    else:
        print("⚠️ Warning: GEMINI_API_KEY not found. Skipping batch prompt expansion.")
        
    # 2. Identify how many images actually need to be generated
    words_to_generate = []
    for index, row in df.iterrows():
        w_id = str(row['ID']).strip()
        korean_word = str(row['한국어 뜻']).strip()
        
        kanji = str(row['한자']).strip() if pd.notna(row['한자']) else ''
        hira = str(row['히라가나']).strip()
        original_word = kanji if kanji != '' else hira
        clean_orig = clean_name(original_word)
        clean_kor = clean_name(korean_word)
        image_key = f"{w_id}_{clean_orig}_{clean_kor}"
        img_path = os.path.join(image_dir, f"{image_key}.png")
        has_image_on_disk = os.path.exists(img_path)
        
        current_img_key = str(row['이미지 키']).strip()
        current_prompt = str(row['비주얼 프롬프트']).strip()
        
        # Original words are kept as is
        if w_id.isdigit() and int(w_id) <= 45:
            continue
            
        if current_prompt == 'UNVISUAL' or current_prompt == '':
            continue
            
        if has_image_on_disk and current_img_key != '':
            continue
            
        words_to_generate.append((index, w_id, korean_word, current_prompt))
        
    if not words_to_generate:
        print("🎉 No new images to generate. All synced!")
        rebuild_code_files(df, original_words)
        return
        
    print(f"Need to process {len(words_to_generate)} words.")
    if args.limit is not None:
        words_to_generate = words_to_generate[:args.limit]
        print(f"Limited run: processing only first {len(words_to_generate)} words.")
        
    # 3. Lazy load Stable Diffusion pipeline
    print("Loading local Stable Diffusion model (dreamlike-art/dreamlike-anime-1.0)...")
    import torch
    import gc
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    
    pipe = StableDiffusionPipeline.from_pretrained(
        "dreamlike-art/dreamlike-anime-1.0", 
        torch_dtype=torch.float32,
        safety_checker=None,
        requires_safety_checker=False
    )
    pipe = pipe.to("mps")
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_attention_slicing()
    
    for index, w_id, korean_word, prompt_val in words_to_generate:
        print(f"\nProcessing '{korean_word}' ({w_id}) with prompt '{prompt_val}'...")
        
        # Local Stable Diffusion Image Generation
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
            
            kanji = str(row['한자']).strip() if pd.notna(row['한자']) else ''
            hira = str(row['히라가나']).strip()
            original_word = kanji if kanji != '' else hira
            clean_orig = clean_name(original_word)
            clean_kor = clean_name(korean_word)
            image_key = f"{w_id}_{clean_orig}_{clean_kor}"
            image_path = os.path.join(image_dir, f"{image_key}.png")
            image.save(image_path)
            
            print(f"  ✅ Image saved successfully!")
            df.at[index, '이미지 키'] = image_key
            df.to_excel(excel_path, index=False)
            
            rebuild_code_files(df, original_words)
            
            # MEMORY CLEANUP
            del image
            gc.collect()
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            
        except Exception as e:
            print(f"  ❌ Local generation failed: {e}")
            
    rebuild_code_files(df, original_words)
    print("\n🎉 Process completed successfully!")

if __name__ == "__main__":
    main()
