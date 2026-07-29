import json
import os

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def fix_and_regen():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    base_ghibli = "studio ghibli style, warm color palette, soft volumetric lighting"
    
    # 1. 문제 (問題): 칠판/시험지 앞에서 연필을 들고 고민하는 학생 & 물음표
    tags_cache["n5_0002"] = f"student sitting at school desk with pencil, looking thoughtfully at a test paper with question marks and math equations, classroom background, {base_ghibli}"
    
    # 2. 팔다 (売る): 시장 가판대에서 물건을 손님에게 건네주고 거래하는 장면
    tags_cache["n5_0015"] = f"friendly shopkeeper handing a paper bag to a customer over a market stall counter, exchange of items, selling goods, active store, {base_ghibli}"
    
    # 3. 젓가락 (箸): 젓가락받침대 위에 놓인 원목 젓가락 선명한 클로즈업
    tags_cache["n2_0430"] = f"macro close-up focus on a pair of fine dark wooden chopsticks resting neatly on a ceramic chopstick rest, minimalist dining setting, clear single object, {base_ghibli}"
    
    # 4. 부엌 (台所): 인물 없이 선명하고 따뜻한 주방 조리대와 기구 인테리어
    tags_cache["n5_0005"] = f"cozy rustic Ghibli kitchen interior, clean wooden kitchen counter with stove, copper pots hanging on wall, vintage kitchen cabinets, warm ambient lighting, no people, {base_ghibli}"
    
    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print("[Success] 4개 단어 커스텀 프롬프트 재설정 완료!")

if __name__ == "__main__":
    fix_and_regen()
