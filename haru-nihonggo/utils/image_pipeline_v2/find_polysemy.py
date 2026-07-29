import json
import os
import re

def find_polysemous_words():
    path = "utils/image_pipeline_v2/word_categories_all.json"
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return
        
    with open(path, 'r', encoding='utf-8') as f:
        categories = json.load(f)
        
    polysemy_candidates = []
    
    # 1. Patterns that might suggest multi-meaning or easily confused words
    # - Contains commas, semicolons, slashes, or parentheses indicating different usage
    # - Korean meanings that have very broad translations
    for cat, words in categories.items():
        for w in words:
            korean = w.get('korean', '')
            english = w.get('english', '')
            kanji = w.get('kanji', '')
            hiragana = w.get('hiragana', '')
            w_id = w.get('id', '')
            
            # Count separator symbols which indicate multiple meanings
            separators = len(re.findall(r'[;,/]', korean))
            
            # Broad English words that often cause confusion when combined with specific Korean nuances
            confusing_english = ['head', 'case', 'side', 'arm', 'chest', 'plant', 'bank', 'key', 'spring', 'match', 'fair']
            eng_lower = english.lower()
            has_confusing_eng = any(x in eng_lower for x in confusing_english)
            
            # Condition for warning
            if separators >= 2 or (separators >= 1 and has_confusing_eng) or (has_confusing_eng and len(korean) <= 2):
                polysemy_candidates.append({
                    "id": w_id,
                    "cat": cat,
                    "kanji": kanji or hiragana,
                    "korean": korean,
                    "english": english,
                    "exampleJp": w.get('exampleJp', ''),
                    "exampleKo": w.get('exampleKo', '')
                })

    print(f"📊 Total polysemy candidates found: {len(polysemy_candidates)}")
    print("\n--- Top 20 Potential Confusing Words Sample ---")
    for idx, item in enumerate(polysemy_candidates[:20], 1):
        print(f"{idx}. [{item['id']}] {item['kanji']} ({item['korean']}) -> Eng: {item['english']}")
        if item['exampleJp']:
            print(f"   Ex: {item['exampleJp']} ({item['exampleKo']})")
        print("-" * 50)

if __name__ == "__main__":
    find_polysemous_words()
