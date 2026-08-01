import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def inspect_degree_adverbs():
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    degree_keywords = ["매우", "대단히", "아주", "몹시", "굉장히", "심히", "극히", "꽤", "훨씬", "더", "가장"]
    
    found_adverbs = []
    
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            korean = w.get("korean", "")
            if any(dk in korean for dk in degree_keywords):
                w_id = w["id"]
                kanji = w.get("kanji", "")
                hiragana = w.get("hiragana", "")
                prompt = tags_cache.get(w_id, "")
                found_adverbs.append({
                    "id": w_id,
                    "level": w.get("level", "n5").upper(),
                    "kanji": kanji,
                    "hiragana": hiragana,
                    "korean": korean,
                    "prompt": prompt
                })
                
    print(f"=== 정도/수량 부사 단어 총 {len(found_adverbs)}개 검수 ===")
    for item in found_adverbs:
        print(f"[{item['level']}] ID: {item['id']} | {item['kanji']} ({item['hiragana']}) = {item['korean']}")
        print(f"  - Current Prompt: {item['prompt']}\n")

if __name__ == "__main__":
    inspect_degree_adverbs()
