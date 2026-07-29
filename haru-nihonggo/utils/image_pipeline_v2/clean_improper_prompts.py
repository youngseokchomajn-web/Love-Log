import os
import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def clean_improper_prompts():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    base_ghibli = "studio ghibli style, warm color palette, soft volumetric lighting"
    
    fixed = 0
    for w_id, prompt in list(tags_cache.items()):
        if "delicious fresh food dish" in prompt:
            # Check if really food
            if w_id == "n5_0282":
                tags_cache[w_id] = f"train ticket on wooden counter, station ticket barrier background, {base_ghibli}"
                fixed += 1
            elif w_id == "n3_0748":
                tags_cache[w_id] = f"shocked expression, oops moment, wallet left on table, {base_ghibli}"
                fixed += 1
            elif w_id == "n2_0191":
                tags_cache[w_id] = f"quiet silent room, sunbeams through window, serene atmosphere, {base_ghibli}"
                fixed += 1
            elif w_id == "n1_0157":
                tags_cache[w_id] = f"chef kneading bread dough on wooden counter, flour dusting air, {base_ghibli}"
                fixed += 1
            elif w_id == "n1_2600":
                tags_cache[w_id] = f"single pure white lily flower on wooden table by quiet window, {base_ghibli}"
                fixed += 1
            elif w_id == "n1_2621":
                tags_cache[w_id] = f"tranquil bamboo forest in morning mist, quiet nature, {base_ghibli}"
                fixed += 1
                
    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] Fixed {fixed} improper prompt templates!")

if __name__ == "__main__":
    clean_improper_prompts()
