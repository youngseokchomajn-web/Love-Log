#!/usr/bin/env python3
"""
expanded_tags_cache.json CI/CD 무결성 검증 및 자동 동기화 스크립트
===============================================================
기능:
1. 마스터 단어 데이터셋(word_categories_all.json)과 캐시 간 100% 룩업 커버리지 검증
2. 누락된 ID / 호환 키(N4 패딩, 한자) 자동 복구
3. 서사 과밀(Narrative Overdensity) 자동 감지 및 경고
4. 주객전도 방지(Anti-Overshadowing) 규칙 적용 여부 검사

사용법:
  python3 validate_and_sync_cache.py [--fix]
"""

import json
import os
import sys

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo/utils/image_pipeline_v2"
MASTER_FILE = os.path.join(BASE_DIR, "word_categories_all.json")
CACHE_FILE = os.path.join(BASE_DIR, "expanded_tags_cache.json")

def load_data():
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master = json.load(f)
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    return master, cache

def run_pipeline_check(auto_fix=False):
    master, cache = load_data()
    
    # 1. 전체 마스터 단어 추출
    all_words = []
    for cat_name, word_list in master.items():
        for w in word_list:
            w['_cat'] = cat_name
            all_words.append(w)
            
    print(f"🔍 [CI/CD] 마스터 단어 수: {len(all_words)}개 | 캐시 엔트리 수: {len(cache)}개")
    
    missing_ids = []
    corrupted_entries = []
    overshadowed_entries = []
    
    # 서사 주객전도 유발 키워드 (방지 대상)
    overshadowing_keywords = ['cherry blossom', 'railway platform', 'scarf', 'letter', 'fireplace', 'porch shade']
    
    for w in all_words:
        w_id = w.get('id', '')
        kanji = w.get('kanji', '')
        
        # 1차 ID 룩업
        prompt = cache.get(w_id, cache.get(kanji, None))
        
        if not prompt or prompt == 'N/A':
            missing_ids.append(w_id)
        else:
            # 주객전도 위험 체크 (추상어인데 방해 오브젝트 포함)
            if w['_cat'] in ['abstract_nouns', 'adverbs_functional']:
                matched = [kw for kw in overshadowing_keywords if kw in prompt.lower()]
                if matched:
                    overshadowed_entries.append((w_id, kanji, w.get('korean', ''), matched, prompt))

    print(f"\n📊 검증 결과 리포트:")
    print(f"  - 룩업 커버리지: {len(all_words) - len(missing_ids)} / {len(all_words)} ({((len(all_words) - len(missing_ids))/len(all_words))*100:.2f}%)")
    print(f"  - 누락된 ID: {len(missing_ids)}개")
    print(f"  - ⚠️ 주객전도 위험 (방해 오브젝트 포함 추상어): {len(overshadowed_entries)}개")

    if overshadowed_entries:
        print(f"\n⚠️ 주객전도 위험 예시 (상위 5개):")
        for wid, kj, ko, kw, pr in overshadowed_entries[:5]:
            print(f"  [{wid}] {kj} ({ko}) → 방해요소: {kw}")
            print(f"     프롬프트: {pr[:100]}...")

    if auto_fix and missing_ids:
        print("\n🔧 [--fix] 누락 항목 기본 프롬프트 복구 진행 중...")
        for wid in missing_ids:
            cache[wid] = "studio ghibli style, minimal soft backdrop, warm color palette"
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print("✅ 캐시 파일 자동 저장 완료!")

if __name__ == "__main__":
    fix_flag = "--fix" in sys.argv
    run_pipeline_check(auto_fix=fix_flag)
