#!/usr/bin/env python3
"""
추상/기능어 프롬프트 오인 위험 전수조사 스크립트
================================================
목적: 현재 6대 카테고리(정도부사, 비교동사, 의문사, 지시어, 접속사, 시간/빈도/수량)로
      커버되지 않는 "서사가 개념을 덮어버리는" 문제 단어 유형이 추가로 있는지 탐색.

방법:
1. word_categories_all.json의 5개 카테고리에서 전체 단어 추출
2. expanded_tags_cache.json에서 해당 프롬프트 매칭
3. 의미(korean/english) 기반으로 세부 유형 자동 분류
4. 각 유형별 프롬프트 패턴 진단
"""

import json
import re
from collections import defaultdict

with open('utils/image_pipeline_v2/word_categories_all.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

with open('utils/image_pipeline_v2/expanded_tags_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

# ──────────────────────────────────────
# 1. 전체 단어를 플랫 리스트로 모으기
# ──────────────────────────────────────
all_words = []
for cat_name, word_list in categories.items():
    for w in word_list:
        w['_category'] = cat_name
        all_words.append(w)

print(f"총 단어 수: {len(all_words)}")
print(f"카테고리별: {', '.join(f'{k}={len(v)}' for k,v in categories.items())}")
print()

# ──────────────────────────────────────
# 2. 세부 유형 분류 규칙 정의
# ──────────────────────────────────────

def classify_semantic_type(w):
    """단어의 의미/품사를 기반으로 세부 유형 분류"""
    kanji = w.get('kanji', '')
    kana = w.get('hiragana', '')
    korean = w.get('korean', '')
    english = w.get('english', '')
    cat = w.get('_category', '')
    
    ko = korean.lower()
    en = english.lower()
    combined = ko + ' ' + en
    
    # ── 이미 식별된 6대 카테고리 ──
    
    # 1. 의문사
    interrogative_kanji = ['何', '誰', '幾']
    interrogative_kana = ['なに', 'なん', 'だれ', 'いつ', 'どこ', 'なぜ', 'どう', 'どれ', 'どの', 'どちら', 'いくつ', 'いくら', 'どなた']
    if any(kanji.startswith(k) for k in interrogative_kanji) or kana in interrogative_kana:
        return '의문사'
    if any(k in ko for k in ['무엇', '누구', '어디', '언제', '왜', '어째서', '어느', '어떻게', '어떤', '몇']):
        return '의문사'
    
    # 2. 지시대명사/장소지시어
    demonstrative_kana = ['これ', 'それ', 'あれ', 'ここ', 'そこ', 'あそこ', 'こちら', 'そちら', 'あちら', 'こっち', 'そっち', 'あっち', 'こう', 'そう', 'ああ', 'この', 'その', 'あの', 'こんな', 'そんな', 'あんな', 'こんなに', 'そんなに', 'あんなに']
    if kana in demonstrative_kana or kanji in demonstrative_kana:
        return '지시어'
    if any(k in ko for k in ['이것', '저것', '그것', '여기', '거기', '저기', '이쪽', '저쪽', '그쪽']):
        return '지시어'
    
    # 3. 접속사/논리연결어
    conjunction_kana = ['しかし', 'だから', 'そして', 'すると', 'ところが', 'ところで', 'それで', 'それに', 'つまり', 'なぜなら', 'けれども', 'もしくは', 'または', 'および', 'なお', 'ただし', 'ちなみに', 'むしろ', 'すなわち']
    if kana in conjunction_kana:
        return '접속사/논리연결어'
    if any(k in ko for k in ['하지만', '그러므로', '그리고', '그런데', '즉', '따라서', '게다가', '요컨대', '오히려', '또한']):
        return '접속사/논리연결어'
    
    # 4. 정도부사 (이미 수정된 것 포함)
    if any(k in ko for k in ['매우', '꽤', '상당히', '대단히', '조금', '약간', '아주', '몹시', '극히', '다소', '충분히', '너무', '겨우', '간신히', '별로', '그다지']):
        return '정도부사'
    
    # 5. 비교/관계
    if any(k in ko for k in ['닮다', '비슷하', '다르다', '같다', '관련', '비교', '대조', '반대', '상대', '맞먹']):
        return '비교/관계'
    
    # 6. 시간/빈도 부사
    if any(k in ko for k in ['가끔', '자주', '항상', '언제나', '요즘', '드디어', '마침내', '미리', '곧', '이제', '아직', '벌써', '일찍', '늦게', '나중에', '금방', '방금', '점차', '차차']):
        return '시간/빈도 부사'
    
    # ── 추가 탐색: 아직 식별되지 않은 유형들 ──
    
    # 7. 감정/심리 상태 (추상)
    if any(k in ko for k in ['기쁨', '슬픔', '분노', '불안', '걱정', '후회', '감사', '동정', '질투', '부끄러', '수치', '자존심', '자신감', '용기', '두려움', '공포', '희망', '절망', '만족', '불만', '외로움', '고독', '향수']):
        return '감정/심리 상태'
    
    # 8. 사회/제도 추상 명사
    if any(k in ko for k in ['법', '권리', '의무', '자유', '평등', '정의', '민주', '사회', '정치', '경제', '문화', '교육', '종교', '전통', '관습', '제도', '정책']):
        return '사회/제도 추상명사'
    
    # 9. 관계/상태 형용사 (추상 형용사)
    if cat == 'adjectives_states' and any(k in ko for k in ['중요', '필요', '적절', '충분', '불가능', '가능', '확실', '불확실', '명확', '애매', '모호', '당연', '불필요', '귀중', '소중', '사소']):
        return '추상 형용사'
    
    # 10. 양태/판단 부사
    if any(k in ko for k in ['아마', '혹시', '확실히', '틀림없이', '분명히', '설마', '반드시', '꼭', '물론', '당연히', '결코', '절대로', '전혀', '도저히', '과연', '역시', '오히려', '차라리', '만약', '만일']):
        return '양태/판단 부사'
    
    # 11. 수사/수량 관련
    if any(k in ko for k in ['권', '장', '개', '마리', '명', '번', '회', '켤레', '벌', '채', '대', '병', '잔', '그루', '자루', '척']):
        return '수량사/단위'
    if re.search(r'[0-9]|〜|ずつ', kanji + kana):
        return '수량사/단위'
    
    # 12. 정도/양적 개념 명사
    if any(k in ko for k in ['정도', '한도', '한계', '수준', '범위', '비율', '비중', '분량', '용량', '최소', '최대', '평균']):
        return '정도/양적 개념 명사'
    
    # 13. 상태변화/경과 동사
    if any(k in ko for k in ['되다', '변하다', '바뀌다', '증가', '감소', '늘다', '줄다', '높아지다', '낮아지다']):
        return '상태변화 동사'
    
    # 14. 인지/사고 동사 (추상)
    if any(k in ko for k in ['생각하', '깨닫', '이해하', '알다', '모르다', '믿다', '의심하', '판단하', '추측', '예상', '기억', '잊다', '연상', '상상']):
        return '인지/사고 동사'
    
    # 15. 의지/의향 표현
    if any(k in ko for k in ['~하려고', '의도', '결심', '각오', '의지', '다짐']):
        return '의지/의향'
    
    # 16. 존경어/겸양어 (기능어)
    if any(k in ko for k in ['~시다', '~드리다', '~해 주시다', '~하시다']):
        return '경어/기능어'
    if any(k in en for k in ['honorific', 'humble', 'polite']):
        return '경어/기능어'
    
    # 17. 조건/가정 표현
    if any(k in ko for k in ['만약', '가령', '만일', '가정', '~라면', '~한다면']):
        return '조건/가정'
    
    # 18. 논리/학술 추상 명사
    if any(k in ko for k in ['원인', '결과', '영향', '효과', '관계', '관련', '근거', '증거', '논리', '이론', '원리', '법칙', '개념', '정의', '분류', '구조', '체계', '과정', '방법', '수단', '대책', '해결']):
        return '논리/학술 추상명사'
    
    # 기타: 분류 안 됨
    if cat in ['abstract_nouns', 'adverbs_functional']:
        return '미분류 추상어'
    
    return None  # 구체적 단어(명사/동사/형용사)는 None


# ──────────────────────────────────────
# 3. 전수 분류 실행
# ──────────────────────────────────────
type_groups = defaultdict(list)
uncategorized_abstract = []

for w in all_words:
    stype = classify_semantic_type(w)
    if stype:
        type_groups[stype].append(w)

# ──────────────────────────────────────
# 4. 프롬프트 오인 위험 진단
# ──────────────────────────────────────

# 오인 위험 지표: 프롬프트에 구체적 서사 요소가 과다한지 체크
narrative_indicators = [
    'running', 'walking', 'sleeping', 'eating', 'cooking',
    'library', 'school', 'kitchen', 'bedroom', 'office', 'station', 'cafe',
    'friend', 'grandmother', 'mother', 'father', 'boy', 'girl',
    'cherry blossom', 'autumn leaves', 'rain', 'snow',
    'reading', 'studying', 'shopping',
]

def count_narrative_density(prompt):
    """프롬프트의 서사 밀도를 계산"""
    if not prompt or prompt == 'N/A':
        return 0
    prompt_lower = prompt.lower()
    return sum(1 for ind in narrative_indicators if ind in prompt_lower)

# ──────────────────────────────────────
# 5. 결과 리포트 생성
# ──────────────────────────────────────
print("=" * 70)
print("  추상/기능어 세부 유형별 분류 결과")
print("=" * 70)

report = {}

for stype in sorted(type_groups.keys(), key=lambda x: -len(type_groups[x])):
    words = type_groups[stype]
    
    # 프롬프트 분석
    high_risk = []
    for w in words:
        w_id = w.get('id', '')
        kanji = w.get('kanji', '')
        prompt = cache.get(w_id, cache.get(kanji, ''))
        density = count_narrative_density(prompt)
        if density >= 2:
            high_risk.append({
                'id': w_id,
                'kanji': kanji,
                'kana': w.get('hiragana', ''),
                'korean': w.get('korean', ''),
                'prompt': prompt,
                'narrative_density': density
            })
    
    high_risk.sort(key=lambda x: -x['narrative_density'])
    
    print(f"\n{'─' * 50}")
    print(f"📦 [{stype}] → 총 {len(words)}개 단어, 🚨 서사 과밀 {len(high_risk)}개")
    print(f"{'─' * 50}")
    
    # 상위 5개 오인 위험 사례 출력
    for item in high_risk[:5]:
        print(f"  [{item['id']}] {item['kanji']}({item['kana']}) = {item['korean']}")
        print(f"     서사밀도: {item['narrative_density']} | 프롬프트: {item['prompt'][:100]}...")
    
    report[stype] = {
        'total_words': len(words),
        'high_risk_count': len(high_risk),
        'high_risk_samples': high_risk[:10]
    }

# ──────────────────────────────────────
# 6. 미분류 추상어 확인
# ──────────────────────────────────────
if '미분류 추상어' in type_groups:
    unclassified = type_groups['미분류 추상어']
    print(f"\n{'=' * 70}")
    print(f"⚠️  미분류 추상/기능어: {len(unclassified)}개")
    print(f"{'=' * 70}")
    
    # 미분류 단어들의 한국어 의미를 패턴 분석
    meaning_words = defaultdict(int)
    for w in unclassified:
        korean = w.get('korean', '')
        # 단어 단위로 쪼개서 빈도 집계
        for tok in re.split(r'[;,/\s・~～〜()（）]+', korean):
            tok = tok.strip()
            if len(tok) >= 2:
                meaning_words[tok] += 1
    
    # 빈도 상위 출력
    print("\n미분류 단어 의미 키워드 빈도 (Top 40):")
    for kw, cnt in sorted(meaning_words.items(), key=lambda x: -x[1])[:40]:
        print(f"  {kw}: {cnt}")
    
    # 미분류 중 서사 과밀 사례
    print(f"\n미분류 중 서사 과밀 사례 (상위 15개):")
    unclassified_risk = []
    for w in unclassified:
        w_id = w.get('id', '')
        kanji = w.get('kanji', '')
        prompt = cache.get(w_id, cache.get(kanji, ''))
        density = count_narrative_density(prompt)
        if density >= 3:
            unclassified_risk.append({
                'id': w_id,
                'kanji': kanji,
                'kana': w.get('hiragana', ''),
                'korean': w.get('korean', ''),
                'prompt': prompt,
                'density': density
            })
    unclassified_risk.sort(key=lambda x: -x['density'])
    for item in unclassified_risk[:15]:
        print(f"  [{item['id']}] {item['kanji']}({item['kana']}) = {item['korean']}")
        print(f"     밀도: {item['density']} | {item['prompt'][:120]}...")

# ──────────────────────────────────────
# 7. 커버리지 요약
# ──────────────────────────────────────
print(f"\n{'=' * 70}")
print("  📊 커버리지 요약")
print(f"{'=' * 70}")

classified_count = sum(len(v) for k, v in type_groups.items() if k != '미분류 추상어')
unclassified_count = len(type_groups.get('미분류 추상어', []))
total_abstract = classified_count + unclassified_count
concrete_count = len(all_words) - total_abstract

print(f"전체 단어: {len(all_words)}")
print(f"구체적 단어 (커버 불필요): {concrete_count}")
print(f"추상/기능어 총계: {total_abstract}")
print(f"  ✅ 분류 완료: {classified_count} ({classified_count/total_abstract*100:.1f}%)")
print(f"  ❓ 미분류: {unclassified_count} ({unclassified_count/total_abstract*100:.1f}%)")

total_high_risk = sum(r['high_risk_count'] for r in report.values())
print(f"\n🚨 서사 과밀 위험 단어 총계: {total_high_risk}개")

# JSON으로 저장
with open('utils/image_pipeline_v2/abstract_coverage_audit.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"\n💾 상세 리포트 저장: abstract_coverage_audit.json")
