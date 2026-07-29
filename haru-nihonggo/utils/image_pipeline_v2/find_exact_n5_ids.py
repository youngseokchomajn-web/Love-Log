import re

with open("data/words/n5.ts", "r", encoding="utf-8") as f:
    text = f.read()
    
target_words = ["問題", "売る", "箸", "台所"]

print("=== N5 단어장에서 정확한 ID 검색 ===")
for tw in target_words:
    pattern = rf'id:\s*["\']([^"\']+)["\'],\s*kanji:\s*["\']([^"\']*' + tw + r'[^"\']*)["\']'
    matches = re.findall(r'id:\s*["\']([^"\']+)["\'],\s*kanji:\s*["\'][^"\']*' + tw + r'[^"\']*["\']', text)
    if not matches:
        # Try matching korean
        matches = re.findall(r'id:\s*["\']([^"\']+)["\'][^}}]+korean:\s*["\'][^"\']*' + tw + r'[^"\']*["\']', text)
    print(f"단어 '{tw}': {matches}")
