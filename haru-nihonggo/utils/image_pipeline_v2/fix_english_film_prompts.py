import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def fix_english_film():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    base_ghibli = "studio ghibli style, warm color palette, soft volumetric lighting"
    
    # 1. 영어 (英語 / 英和 / 和英 / 英文)
    tags_cache["n5_0022"] = f"open English textbook with ABC alphabet blocks, small Union Jack flag, London Big Ben background, warm desk study setting, {base_ghibli}"
    tags_cache["n2_0166"] = f"English-Japanese dictionary book open on wooden desk, ABC and kanji side-by-side, brass lamp, cozy study, {base_ghibli}"
    tags_cache["n2_0233"] = f"Japanese-English dictionary book open on wooden desk, kanji and ABC side-by-side, cozy study room, {base_ghibli}"
    tags_cache["n2_1699"] = f"fountain pen writing neat English cursive sentences on parchment paper, antique desk, {base_ghibli}"
    
    # 2. 필름 (フィルム / ネガ)
    tags_cache["n5_0012"] = f"classic 35mm camera film roll canister with unrolled dark film strip on wooden table, clear single object focus, no humans, {base_ghibli}"
    tags_cache["n1_2965"] = f"translucent photographic negative film strip held up against warm light, clear film frames, camera workbench, no humans, {base_ghibli}"

    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print("[Success] 영어, 필름 관련 단어 프롬프트 정밀 재설계 완료!")

if __name__ == "__main__":
    fix_english_film()
