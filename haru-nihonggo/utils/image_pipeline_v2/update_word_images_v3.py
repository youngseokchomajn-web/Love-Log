import os
import glob
import json
import unicodedata

def main():
    words_v3_dir = "assets/images/words_v3"
    output_ts_path = "data/wordImagesV3.ts"
    
    if not os.path.exists(words_v3_dir):
        print(f"Directory {words_v3_dir} does not exist.")
        return
        
    extensions = ('*.webp', '*.jpg', '*.png', '*.jpeg')
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(words_v3_dir, ext)))
        
    files = [f for f in files if not f.endswith('failed_generation.json')]
    files.sort()
    
    seen_keys = set()
    entries = []
    for file_path in files:
        filename = os.path.basename(file_path)
        raw_key, _ = os.path.splitext(filename)
        key = unicodedata.normalize('NFC', raw_key)
        
        if key in seen_keys:
            continue
        seen_keys.add(key)
        
        req_path = f"../assets/images/words_v3/{filename}"
        entries.append(f"  {json.dumps(key)}: require({json.dumps(req_path)}),")
        
    ts_content = f"""// This file is auto-generated. Do not edit manually.
export const wordImagesV3: Record<string, any> = {{
{chr(10).join(entries)}
}};
"""
    
    with open(output_ts_path, "w", encoding="utf-8") as f:
        f.write(ts_content)
        
    print(f"Successfully generated {output_ts_path} with {len(entries)} unique image entries.")

if __name__ == "__main__":
    main()
