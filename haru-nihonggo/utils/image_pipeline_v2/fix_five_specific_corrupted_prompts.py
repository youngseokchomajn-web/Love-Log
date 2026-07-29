import json
import os

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def fix_five_corrupted():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    base_ghibli = "studio ghibli style, warm color palette, soft volumetric lighting"
    
    # 1. 편리하다 (便利): 원터치 버튼으로 간편하게 작동하는 스마트 기기 / 캐리어
    tags_cache["n5_0033"] = f"hand pressing a convenient one-touch smart button, instant bright light, sleek helpful gadget, easy and convenient, {base_ghibli}"
    
    # 2. 지우다, 끄다 (消す): 칠판지우개로 칠판의 글씨를 슥슥 지우거나 조명 스위치를 끄는 순간
    tags_cache["n5_0350"] = f"hand holding a blackboard eraser wiping away white chalk marks on a green blackboard, clear erasing action, {base_ghibli}"
    
    # 3. 닫다 (閉める): 창문/문을 손으로 닫는 동작
    tags_cache["n5_0352"] = f"hand gently closing a wooden window shutter, shutting out the evening wind, warm cozy indoor, clear action, {base_ghibli}"
    
    # 4. 숫자 9 (九 / 9): 선명한 숫자 9 그래픽과 달력
    tags_cache["n5_0009"] = f"large bold numeral '9' clearly displayed on a wooden desk calendar, crisp number 9, clear focus, {base_ghibli}"
    tags_cache["n5_0028"] = f"large bold numeral '9' clearly displayed on a desk clock pointing to 9 o'clock, crisp number 9, {base_ghibli}"
    
    # 5. 집 (家 / うち): 아늑한 빨간 지붕 집 외관 및 따뜻한 우리집 거실
    tags_cache["n5_0041"] = f"cozy Ghibli house exterior with red tiled roof, chimney with gentle smoke, small garden path, warm glowing windows, home sweet home, {base_ghibli}"
    tags_cache["n5_0137"] = f"warm cozy home interior living room with wooden kotatsu table, tea pot, warm family house atmosphere, {base_ghibli}"

    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print("[Success] 지적하신 5개 단어군(편리하다, 지우다/끄다, 닫다, 9, 집) 프롬프트 정밀 교정 완료!")

if __name__ == "__main__":
    fix_five_corrupted()
