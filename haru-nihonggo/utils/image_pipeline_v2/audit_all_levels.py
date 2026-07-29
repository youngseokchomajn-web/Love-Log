import os
import json
import re

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def audit_all_levels():
    print("=== N2 ~ N5 전체 단어 데이터 및 이미지 프롬프트 전수 검수 시작 ===")
    
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    level_stats = {
        "n1": {"total": 0, "suspicious": []},
        "n2": {"total": 0, "suspicious": []},
        "n3": {"total": 0, "suspicious": []},
        "n4": {"total": 0, "suspicious": []},
        "n5": {"total": 0, "suspicious": []}
    }
    
    generic_patterns = ["notebook", "textbook", "dictionary", "studying kanji", "wooden desk background"]
    
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            w_id = w["id"]
            lvl = w.get("level", "n5").lower()
            if lvl not in level_stats:
                lvl = "n5"
                
            level_stats[lvl]["total"] += 1
            
            prompt = tags_cache.get(w_id, "")
            prompt_lower = prompt.lower()
            kanji = w.get("kanji", "")
            hiragana = w.get("hiragana", "")
            korean = w.get("korean", "")
            
            issues = []
            
            # Check 1: Missing prompt
            if not prompt:
                issues.append("Missing prompt")
                
            # Check 2: Generic fallback prompt used on specific word
            for gp in generic_patterns:
                if gp in prompt_lower and not any(k in korean for k in ["사전", "공부", "노트", "교과서", "책"]):
                    issues.append(f"Generic fallback prompt contains '{gp}'")
                    break
                    
            # Check 3: Semantic mismatches
            if any(food in korean for food in ["죽", "음식", "요리", "밥", "과자", "차"]) and not any(k in prompt_lower for k in ["food", "bowl", "dish", "meal", "plate", "soup", "rice", "snack", "eat", "tea"]):
                issues.append("Food/Meal word but prompt lacks food visuals")
                
            if any(cloth in korean for cloth in ["옷", "의복", "정장", "군복", "모자", "양말", "신발"]) and not any(k in prompt_lower for k in ["wear", "cloth", "suit", "jacket", "shirt", "uniform", "hat", "garment", "outfit", "shoe", "sock"]):
                issues.append("Clothing word but prompt lacks clothing visuals")
                
            # Check 4: POS parens in hiragana
            if "(" in hiragana or "（" in hiragana:
                issues.append(f"POS tag in hiragana field: {hiragana}")
                
            if issues:
                level_stats[lvl]["suspicious"].append({
                    "id": w_id,
                    "kanji": kanji,
                    "hiragana": hiragana,
                    "korean": korean,
                    "prompt": prompt,
                    "reasons": issues
                })
                
    print("\n📊 레벨별 전수 검수 결과 Summary:")
    total_suspicious = 0
    for lvl in ["n5", "n4", "n3", "n2", "n1"]:
        tot = level_stats[lvl]["total"]
        sus = len(level_stats[lvl]["suspicious"])
        total_suspicious += sus
        print(f"  - [{lvl.upper()}] 총 {tot}개 단어중 프롬프트/데이터 개선 필요: {sus}개")
        
    print(f"\n전체 레벨 재검토 필요 단어 총합: {total_suspicious}개")
    
    report_path = f"{ROOT_DIR}/utils/image_pipeline_v2/full_vocab_audit_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(level_stats, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] 전체 레벨 검수 리포트 저장 완료: utils/image_pipeline_v2/full_vocab_audit_report.json")

if __name__ == "__main__":
    audit_all_levels()
