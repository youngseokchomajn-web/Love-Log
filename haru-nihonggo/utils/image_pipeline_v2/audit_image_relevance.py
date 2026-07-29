import os
import json
import re

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def run_image_relevance_audit():
    print("=== 1단계: 단어 카드 이미지 적절성 및 시맨틱 일치도 자동 스캔 ===")
    
    # Load categories and words
    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)
        
    # Load prompts
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    all_words = {}
    for cat_name, word_list in categories_data.items():
        for w in word_list:
            w_id = w["id"]
            w["category"] = cat_name
            all_words[w_id] = w
            
    print(f"총 분석 대상 단어: {len(all_words)}개")
    print(f"생성된 프롬프트 개수: {len(tags_cache)}개")
    
    missing_prompts = []
    suspicious_fallbacks = []
    polysemy_warnings = []
    
    # Common generic fallback prompts that indicate failure during tag extraction
    generic_patterns = [
        "studying kanji notebook",
        "japanese textbook",
        "dictionary on wooden desk"
    ]
    
    for w_id, w in all_words.items():
        prompt = tags_cache.get(w_id, "")
        if not prompt:
            missing_prompts.append(w)
            continue
            
        kanji = w.get("kanji", "")
        korean = w.get("korean", "")
        cat = w.get("category", "")
        
        for gp in generic_patterns:
            if gp in prompt.lower() and cat in ["concrete_nouns", "action_verbs", "food_nature"]:
                suspicious_fallbacks.append({
                    "id": w_id,
                    "kanji": kanji,
                    "korean": korean,
                    "prompt": prompt,
                    "reason": f"Generic fallback prompt '{gp}' used for {cat}"
                })
                break
                
        if korean == "값, 가격" and "price" not in prompt.lower() and "value" not in prompt.lower() and "cost" not in prompt.lower():
            polysemy_warnings.append({
                "id": w_id,
                "kanji": kanji,
                "korean": korean,
                "prompt": prompt,
                "reason": "Meaning 'price/value' but prompt lacks money/price keywords"
            })
            
    print(f"\n📊 [1단계 스캔 결과 Summary]")
    print(f"  - 누락된 프롬프트: {len(missing_prompts)}개")
    print(f"  - 의심스러운 범용 폴백 프롬프트 (재정의 필요): {len(suspicious_fallbacks)}개")
    print(f"  - 다의어/뜻 불일치 의심 건수: {len(polysemy_warnings)}개")
    
    report = {
        "summary": {
            "total_words": len(all_words),
            "prompts_found": len(tags_cache),
            "missing_prompts": len(missing_prompts),
            "suspicious_fallbacks": len(suspicious_fallbacks),
            "polysemy_warnings": len(polysemy_warnings)
        },
        "suspicious_fallbacks": suspicious_fallbacks,
        "polysemy_warnings": polysemy_warnings
    }
    
    report_path = f"{ROOT_DIR}/utils/image_pipeline_v2/audit_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    print(f"\n[Success] 리포트 저장 완료: utils/image_pipeline_v2/audit_report.json")

if __name__ == "__main__":
    run_image_relevance_audit()
