import os
import re
import glob
import pandas as pd
import unicodedata

excel_path = "data/jlpt_n4_clean_merged.xlsx"
seed_words_path = "data/seedWords.ts"
word_images_path = "data/wordImages.ts"
image_dir = "assets/images/words"

def clean_name(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFC', text)
    # Remove chars that are bad for filenames
    text = re.sub(r'[\\/*?:"<>|()\s,/]', '', text)
    return text.strip()

def parse_seed_words():
    words = []
    if not os.path.exists(seed_words_path):
        return words
        
    with open(seed_words_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Regex to find all word blocks
    pattern = r"\{\s*id:\s*'([^']+)',\s*kanji:\s*'([^']*)',\s*hiragana:\s*'([^']*)',\s*pronunciation:\s*'([^']*)',\s*korean:\s*'([^']*)'(?:,\s*english:\s*'([^']*)')?(?:,\s*imageKey:\s*'([^']*)')?.*?\}"
    matches = re.findall(pattern, content)
    
    for m in matches:
        w_id, kanji, hiragana, pronunciation, korean, english, image_key = m
        words.append({
            'id': w_id,
            'kanji': kanji,
            'hiragana': hiragana,
            'korean': korean,
            'imageKey': image_key if image_key else None
        })
    return words

def main():
    if not os.path.exists(seed_words_path):
        print(f"⚠️ {seed_words_path} not found.")
        return
        
    # Read seedWords.ts to get raw lines for rewriting
    with open(seed_words_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Load Excel to update image keys there too
    excel_updated = False
    df = None
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        if '이미지 키' not in df.columns:
            df['이미지 키'] = ''
        df['이미지 키'] = df['이미지 키'].astype(str).replace('nan', '')
        
    renamed_count = 0
    
    for i, line in enumerate(lines):
        m_id = re.search(r"id:\s*'([^']+)'", line)
        if m_id:
            w_id = m_id.group(1)
            
            # Find kanji, hiragana, korean
            m_kanji = re.search(r"kanji:\s*'([^']*)'", line)
            m_hira = re.search(r"hiragana:\s*'([^']*)'", line)
            m_korean = re.search(r"korean:\s*'([^']*)'", line)
            m_img = re.search(r"imageKey:\s*'([^']*)'", line)
            
            if m_kanji and m_hira and m_korean and m_img:
                kanji = m_kanji.group(1).strip()
                hira = m_hira.group(1).strip()
                korean = m_korean.group(1).strip()
                old_image_key = m_img.group(1).strip()
                
                if old_image_key == '':
                    continue
                    
                # Original word is kanji if exists, otherwise hiragana
                original_word = kanji if kanji != '' else hira
                
                clean_orig = clean_name(original_word)
                clean_kor = clean_name(korean)
                
                # New image key: {id}_{original}_{korean}
                new_image_key = f"{w_id}_{clean_orig}_{clean_kor}"
                
                # Rename file on disk if old one exists
                old_file = os.path.join(image_dir, f"{old_image_key}.png")
                new_file = os.path.join(image_dir, f"{new_image_key}.png")
                
                if os.path.exists(old_file):
                    if old_file != new_file: # Prevent renaming to same name
                        # If target already exists (unlikely, delete it first to avoid collision)
                        if os.path.exists(new_file):
                            os.remove(new_file)
                        os.rename(old_file, new_file)
                        renamed_count += 1
                
                # Update line in seedWords
                line = line.replace(f"imageKey: '{old_image_key}'", f"imageKey: '{new_image_key}'")
                lines[i] = line
                
                # Update Excel
                if df is not None:
                    # Find row by ID
                    # ID in Excel can be integer (legacy) or string (n4_xxx)
                    # Convert to string for match
                    matching_rows = df[df['ID'].astype(str).str.strip() == w_id]
                    if not matching_rows.empty:
                        for idx in matching_rows.index:
                            df.at[idx, '이미지 키'] = new_image_key
                            excel_updated = True
                            
    # Write back seedWords.ts
    with open(seed_words_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Renamed {renamed_count} files and updated {seed_words_path}.")
    
    # Save Excel if updated
    if excel_updated and df is not None:
        df.to_excel(excel_path, index=False)
        print(f"✅ Updated {excel_path} with new image keys.")
        
    # Rebuild wordImages.ts
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

if __name__ == "__main__":
    main()
