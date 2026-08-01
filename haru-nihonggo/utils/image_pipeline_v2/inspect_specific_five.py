import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def inspect_specific():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    target_ids = ["n5_0033", "n5_0350", "n5_0352", "n5_0009", "n5_0028", "n5_0041", "n5_0137"]
    
    print("=== 특정 5개 단어 ID별 프롬프트 검수 ===")
    for w_id in target_ids:
        print(f"ID: {w_id} | Prompt: {tags_cache.get(w_id, 'NOT FOUND')}\n")

if __name__ == "__main__":
    inspect_specific()
