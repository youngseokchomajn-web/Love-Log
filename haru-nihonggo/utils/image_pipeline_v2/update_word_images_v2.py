import os
import glob

def main():
    words_v2_dir = "assets/images/words_v2"
    output_ts_path = "data/wordImagesV2.ts"
    
    if not os.path.exists(words_v2_dir):
        print(f"Directory {words_v2_dir} does not exist.")
        return
        
    # Get all jpg and png files
    extensions = ('*.jpg', '*.png', '*.jpeg')
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(words_v2_dir, ext)))
        
    # Sort files for deterministic output
    files.sort()
    
    entries = []
    for file_path in files:
        filename = os.path.basename(file_path)
        key, _ = os.path.splitext(filename)
        # Relative path from data/wordImagesV2.ts to assets/images/words_v2/filename
        # Path is ../assets/images/words_v2/filename
        entries.append(f"  '{key}': require('../assets/images/words_v2/{filename}'),")
        
    ts_content = f"""// This file is auto-generated. Do not edit manually.
export const wordImagesV2: Record<string, any> = {{
{chr(10).join(entries)}
}};
"""
    
    # Write to file
    with open(output_ts_path, "w", encoding="utf-8") as f:
        f.write(ts_content)
        
    print(f"Successfully generated {output_ts_path} with {len(files)} image entries.")

if __name__ == "__main__":
    main()
