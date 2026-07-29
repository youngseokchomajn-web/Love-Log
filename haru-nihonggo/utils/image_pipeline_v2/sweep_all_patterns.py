import os
import json
import re

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def sweep_all_vocab():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    pattern1_text_fallback = []
    pattern2_verb_no_action = []
    pattern3_small_object_clutter = []
    pattern4_space_human_clutter = []
    
    # Target keywords for pattern detection
    action_verb_keywords = ["팔다", "사다", "빌리다", "빌려주다", "전하다", "싸우다", "만나다", "던지다", "줍다", "헤어지다", "초대하다", "선물하다", "가르치다", "배우다"]
    interaction_tags = ["person", "people", "hand", "handing", "giving", "buying", "selling", "holding", "talking", "meeting", "throwing", "picking", "teaching", "learning", "exchanging", "fighting", "running"]
    
    small_objects_korean = ["젓가락", "숟가락", "포크", "나이프", "안경", "바늘", "단추", "열쇠", "반지", "지우개", "우표", "동전", "연필", "지우개", "바늘", "실", "손톱깎이"]
    
    space_nouns_korean = ["부엌", "주방", "공원", "도서관", "화장실", "욕실", "공장", "병원", "학교", "교실", "미술관", "박물관", "체육관", "정원"]
    human_action_tags = ["cooking", "mother", "doctor", "operating", "teacher", "student", "swimming", "running"]
    
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            w_id = w["id"]
            prompt = tags_cache.get(w_id, "")
            prompt_lower = prompt.lower()
            kanji = w.get("kanji", "")
            hiragana = w.get("hiragana", "")
            korean = w.get("korean", "")
            english = w.get("english", "")
            level = w.get("level", "n5").upper()
            
            # Pattern 1 Check: Text fallback in prompt ('단어' (한자) in prompt)
            if "iconic visual illustration representing" in prompt_lower or re.search(r"['\"][^'\"]+['\"]\s*\([^)]+\)", prompt):
                pattern1_text_fallback.append({
                    "id": w_id, "level": level, "kanji": kanji, "korean": korean, "prompt": prompt
                })
                
            # Pattern 2 Check: Action verb without dynamic interaction tags
            if cat_name == "action_verbs" or any(vk in korean for vk in action_verb_keywords):
                if not any(it in prompt_lower for it in interaction_tags):
                    pattern2_verb_no_action.append({
                        "id": w_id, "level": level, "kanji": kanji, "korean": korean, "prompt": prompt
                    })
                    
            # Pattern 3 Check: Small object clutter without macro/close-up
            if any(so in korean for so in small_objects_korean):
                if not any(cu in prompt_lower for cu in ["close-up", "macro", "close up", "single object", "clear focus", "isolated"]):
                    pattern3_small_object_clutter.append({
                        "id": w_id, "level": level, "kanji": kanji, "korean": korean, "prompt": prompt
                    })
                    
            # Pattern 4 Check: Space noun dominated by human action instead of interior/exterior architecture
            if any(sn in korean for sn in space_nouns_korean):
                if any(ht in prompt_lower for ht in human_action_tags) and "no people" not in prompt_lower and "architecture" not in prompt_lower:
                    pattern4_space_human_clutter.append({
                        "id": w_id, "level": level, "kanji": kanji, "korean": korean, "prompt": prompt
                    })

    total_detected = len(pattern1_text_fallback) + len(pattern2_verb_no_action) + len(pattern3_small_object_clutter) + len(pattern4_space_human_clutter)
    
    print("=== 4대 패턴 교훈 기반 전체 8,424개 단어 전수 스윕 결과 ===")
    print(f"1. [추상어 텍스트 폴백 패턴]: {len(pattern1_text_fallback)}개 단어 적발")
    print(f"2. [동사-동작 묘사 누락 패턴]: {len(pattern2_verb_no_action)}개 단어 적발")
    print(f"3. [소형 사물 배경 매몰 패턴]: {len(pattern3_small_object_clutter)}개 단어 적발")
    print(f"4. [공간 단어 인물 동작 우세 패턴]: {len(pattern4_space_human_clutter)}개 단어 적발")
    print(f"\n총 개선 필요 후보 단어: {total_detected}개")
    
    report = {
        "pattern1_text_fallback": pattern1_text_fallback,
        "pattern2_verb_no_action": pattern2_verb_no_action,
        "pattern3_small_object_clutter": pattern3_small_object_clutter,
        "pattern4_space_human_clutter": pattern4_space_human_clutter,
        "total_detected": total_detected
    }
    
    report_path = f"{ROOT_DIR}/utils/image_pipeline_v2/pattern_sweep_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] 패턴 스윕 리포트 저장 완료: utils/image_pipeline_v2/pattern_sweep_report.json")

if __name__ == "__main__":
    sweep_all_vocab()
