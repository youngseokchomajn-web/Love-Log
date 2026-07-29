import json
import os

target_dir = '/Users/youngseok/Desktop/love-log/haru-nihonggo/utils/image_pipeline_v2'
words_file = os.path.join(target_dir, 'word_categories_all.json')
cache_file = os.path.join(target_dir, 'expanded_tags_cache.json')

with open(words_file, 'r', encoding='utf-8') as f:
    words = json.load(f)

if os.path.exists(cache_file):
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)
else:
    cache = {}

next_words = []
for category, items in words.items():
    if isinstance(items, list):
        for item in items:
            item_id = item.get('id')
            if item_id and item_id not in cache:
                next_words.append({
                    'id': item_id,
                    'word': item.get('kanji') or item.get('word') or item.get('hiragana'),
                    'meaning': item.get('english', '') + ' / ' + item.get('korean', ''),
                    'example': item.get('exampleJp', '') + ' / ' + item.get('exampleKo', '')
                })
                if len(next_words) >= 200:
                    break
    if len(next_words) >= 200:
        break

print(json.dumps(next_words, ensure_ascii=False, indent=2))
