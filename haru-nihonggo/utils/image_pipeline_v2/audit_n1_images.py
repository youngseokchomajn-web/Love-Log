import os
import json
import re

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def audit_n1():
    print("=== N1 단어 카드 이미지 적절성 정밀 분석 시작 ===")
    
    # 1. Load N1 words from data/words/n1.ts
    n1_path = f"{ROOT_DIR}/data/words/n1.ts"
    with open(n1_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract item objects
    pattern = re.compile(
        r'\{\s*id:\s*["\'](n1_\d+)["\'],\s*'
        r'kanji:\s*["\']([^"\'\\]*(?:\\.[^"\'\\]*)*)["\'],\s*'
        r'hiragana:\s*["\']([^"\'\\]*(?:\\.[^"\'\\]*)*)["\'],\s*'
        r'korean:\s*["\']([^"\'\\]*(?:\\.[^"\'\\]*)*)["\'],\s*'
        r'english:\s*["\']([^"\'\\]*(?:\\.[^"\'\\]*)*)["\']',
        re.DOTALL
    )
    
    n1_words = pattern.findall(content)
    print(f"n1.ts 내 단어 개수: {len(n1_words)}개")
    
    # Load prompts
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    audit_results = []
    suspicious_count = 0
    
    # Suspicious prompt patterns:
    # 1. Generic placeholder prompts (e.g. studying notebook, textbook, dictionary) for concrete N1 concepts
    generic_patterns = ["notebook", "textbook", "dictionary", "studying kanji", "wooden desk background"]
    
    # 2. Words with negative or violent meanings mapped to inappropriate visual prompts
    
    for w_id, kanji, hiragana, korean, english in n1_words:
        prompt = tags_cache.get(w_id, "")
        issues = []
        
        # Check 1: Missing prompt
        if not prompt:
            issues.append("Missing prompt")
            
        prompt_lower = prompt.lower()
        
        # Check 2: Generic fallback prompt used on abstract/specific N1 word
        for gp in generic_patterns:
            if gp in prompt_lower and not any(k in korean for k in ["사전", "공부", "노트", "교과서", "책"]):
                issues.append(f"Generic fallback prompt contains '{gp}'")
                break
                
        # Check 3: Mismatch between Korean meaning and prompt key visuals
        # E.g. word means vehicle/food/clothing but prompt is classroom/office
        if any(food in korean for food in ["죽", "음식", "요리", "밥", "과자"]) and not any(k in prompt_lower for k in ["food", "bowl", "dish", "meal", "plate", "soup", "rice", "snack", "eat"]):
            issues.append("Food/Meal word but prompt lacks food visuals")
            
        if any(cloth in korean for cloth in ["옷", "의복", "정장", "군복", "모자"]) and not any(k in prompt_lower for k in ["wear", "cloth", "suit", "jacket", "shirt", "uniform", "hat", "garment", "outfit"]):
            issues.append("Clothing word but prompt lacks clothing visuals")
            
        if issues:
            suspicious_count += 1
            audit_results.append({
                "id": w_id,
                "kanji": kanji,
                "hiragana": hiragana,
                "korean": korean,
                "english": english,
                "prompt": prompt,
                "reasons": issues
            })
            
    print(f"\n📊 N1 이미지 검수 결과:")
    print(f"  - 총 N1 단어: {len(n1_words)}개")
    print(f"  - 프롬프트/시맨틱 적절성 재검토 필요한 단어: {suspicious_count}개")
    
    # Save report
    out_path = f"{ROOT_DIR}/utils/image_pipeline_v2/n1_image_audit_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_n1_words": len(n1_words),
            "suspicious_count": suspicious_count,
            "items": audit_results
        }, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] N1 검수 리포트 저장 완료: utils/image_pipeline_v2/n1_image_audit_report.json")

if __name__ == "__main__":
    audit_n1()
