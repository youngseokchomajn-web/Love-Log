#!/usr/bin/env python3
"""
미분류 3,144개 추상어 심층 분석 - 빠진 카테고리 탐색
"""

import json
import re
from collections import defaultdict

with open('utils/image_pipeline_v2/word_categories_all.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

with open('utils/image_pipeline_v2/expanded_tags_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

all_words = []
for cat_name, word_list in categories.items():
    for w in word_list:
        w['_category'] = cat_name
        all_words.append(w)

# ──────────────────────────────────
# 확장된 분류 규칙 (기존 6개 + 신규)
# ──────────────────────────────────

def classify_v2(w):
    kanji = w.get('kanji', '')
    kana = w.get('hiragana', '')
    ko = w.get('korean', '')
    en = w.get('english', '').lower()
    cat = w.get('_category', '')

    # ─── 기존 6대 ───
    # 1. 의문사
    if any(kanji.startswith(k) for k in ['何', '誰', '幾']) or kana in ['なに','なん','だれ','いつ','どこ','なぜ','どう','どれ','どの','どちら','いくつ','いくら','どなた']:
        return '의문사'
    if any(k in ko for k in ['무엇', '누구(를|에|의)?', '어디', '언제', '왜', '어째서', '어느', '어떻게', '어떤', '몇']):
        return '의문사'

    # 2. 지시어
    if kana in ['これ','それ','あれ','ここ','そこ','あそこ','こちら','そちら','あちら','こっち','そっち','あっち','こう','そう','ああ','この','その','あの','こんな','そんな','あんな']:
        return '지시어'
    
    # 3. 접속사/논리연결어
    if kana in ['しかし','だから','そして','すると','ところが','ところで','それで','それに','つまり','なぜなら','けれども','もしくは','または','および','なお','ただし','ちなみに','むしろ','すなわち','それでも','したがって','ゆえに','そこで','さて','では','じゃ','それとも','あるいは','もっとも','要するに']:
        return '접속사/논리연결어'
    
    # 4. 정도부사
    if any(k in ko for k in ['매우', '꽤', '상당히', '대단히', '조금', '약간', '아주', '몹시', '극히', '다소', '충분히', '너무', '겨우', '간신히', '별로', '그다지', '얼마나', '대체로', '꽤나']):
        return '정도부사'
    
    # 5. 비교/관계
    if any(k in ko for k in ['닮다', '비슷하', '다르다', '같다', '비교', '대조', '반대', '상대', '맞먹']):
        return '비교/관계'
    
    # 6. 시간/빈도 부사
    if any(k in ko for k in ['가끔', '자주', '항상', '언제나', '요즘', '드디어', '마침내', '미리', '곧', '이제', '아직', '벌써', '일찍', '늦게', '나중에', '금방', '방금', '점차', '차차', '이따금', '종종', '늘', '줄곧', '수시로']):
        return '시간/빈도 부사'

    # ─── 신규 카테고리 후보 ───

    # 7. 감정/심리 추상어
    emotion_ko = ['기쁨','기쁘','슬픔','슬프','분노','화나','불안','걱정','후회','감사','질투','부끄러','수치','자존심','자신감','용기','두려움','공포','희망','절망','만족','불만','외로움','고독','향수','동정','동감','흥분','우울','짜증','허탈','감동','안심','긴장','초조','침착','차분','설렘','기대']
    if any(k in ko for k in emotion_ko):
        return '감정/심리 추상어'

    # 8. 인지/사고/판단 동사
    cognition_ko = ['생각하','깨닫','이해하','알다','모르다','믿다','의심','판단','추측','예상','기억','잊다','연상','상상','인식','인지','추리','성찰','반성','착각','오해']
    if any(k in ko for k in cognition_ko):
        return '인지/사고 동사'
    
    # 9. 양태/확신 부사 (아마, 반드시, 확실히, 설마 등)
    modality_ko = ['아마','혹시','확실히','틀림없이','분명히','설마','반드시','꼭','물론','당연히','결코','절대로','전혀','도저히','과연','역시','차라리','만약','만일','어쨌든','어차피','아무래도','어쩐지','마치','이를테면','다만','단지','그저','마침','우연히','갑자기','순간']
    if any(k in ko for k in modality_ko):
        return '양태/확신 부사'

    # 10. 추상 형용사 (판단/평가)
    abs_adj_ko = ['중요','필요','적절','충분','불가능','가능','확실','불확실','명확','애매','모호','당연','귀중','소중','사소','긴급','급','곤란','편리','불편','적당','부적절','정확','불명','미묘']
    if any(k in ko for k in abs_adj_ko):
        return '추상 형용사'

    # 11. 수량/단위/카운터
    counter_ko = ['권','장','개','마리','명','번','회','켤레','벌','채','대','병','잔','그루','자루','척','세는','단위','번째','배(倍)']
    if any(k in ko for k in counter_ko):
        return '수량사/단위'
    if re.search(r'〜|ずつ|counter|counting', kanji + kana + en):
        return '수량사/단위'
    
    # 12. 논리/학술 추상명사
    logic_ko = ['원인','결과','영향','효과','관계','관련','근거','증거','논리','이론','원리','법칙','개념','정의','분류','구조','체계','과정','방법','수단','대책','해결','문제','상황','조건','전제','가설','결론','분석','평가','기준','가치','의미','목적','이유','본질','특징','성질','기능','역할','차이','공통','유형','종류']
    if any(k in ko for k in logic_ko):
        return '논리/학술 추상명사'

    # 13. 의지/태도/자세 표현
    attitude_ko = ['결심','각오','의지','다짐','노력','끈기','인내','포기','체념','신중','대담','겸손','오만','성실','불성실','태도','자세','근면','게으름','의욕','열정']
    if any(k in ko for k in attitude_ko):
        return '의지/태도 표현'

    # 14. 경어/인사/예의 기능어
    if any(k in en for k in ['honorific', 'humble', 'polite']):
        return '경어/기능어'
    polite_ko = ['인사','존경','겸양','예의','실례','사양','정중']
    if any(k in ko for k in polite_ko):
        return '경어/기능어'

    # 15. 사회/제도 추상명사
    society_ko = ['법','권리','의무','자유','평등','정의','민주','사회','정치','경제','문화','교육','종교','전통','관습','제도','정책','규칙','규정','법률','헌법','조약','외교','선거','투표','여론']
    if any(k in ko for k in society_ko):
        return '사회/제도 추상명사'

    # 16. 상태변화/경과 동사
    change_ko = ['되다','변하다','바뀌다','증가','감소','늘다','줄다','높아지다','낮아지다','넓어지다','좁아지다','깊어지다','강해지다','약해지다','나아지다','악화','향상','저하','발전','쇠퇴','진행','진전']
    if any(k in ko for k in change_ko):
        return '상태변화 동사'
    
    # 17. 관계/대인관계 추상어
    relation_ko = ['짝사랑','사랑','우정','관계','이별','재회','약속','신뢰','배신','화해','갈등','협력','경쟁','대립','동료','상사','부하','선배','후배','동갑','연상','연하']
    if any(k in ko for k in relation_ko):
        return '관계/대인 추상어'

    # 18. 동작양태 부사 (방법/모습 부사)
    manner_ko = ['일부러','열심히','천천히','빨리','서둘러','조용히','몰래','살짝','갑자기','느닷없이','대충','꼼꼼히','조심스럽게','무심코','어쩔 수 없이','억지로','기꺼이','마지못해','슬쩍','번갈아','잔뜩','이윽고','문득','우연히','무심결에','도중','그대로']
    if any(k in ko for k in manner_ko):
        return '동작양태 부사'
    
    # 19. 부정/긍정 표현
    negpos_ko = ['아니','못','안','불','무','비','반','초']
    if any(k in ko for k in ['부정', '긍정', '찬성', '반대', '거부', '승인', '허가', '금지']):
        return '부정/긍정 표현'

    # 20. 시간대/기간 명사
    time_noun_ko = ['아침','저녁','낮','밤','새벽','오전','오후','정오','자정','주말','평일','내일','어제','모레','글피','올해','작년','내년','이번','지난','다음','과거','미래','현재','당시','최근','이전','이후','기간','시간','순간','시기','시대','세기','시절','요즘','예전']
    if any(k in ko for k in time_noun_ko):
        return '시간대/기간 명사'

    # 21. 방향/위치 추상어
    direction_ko = ['위','아래','옆','앞','뒤','안','밖','속','겉','사이','중간','중심','가운데','주변','근처','부근','맞은편','건너편','방향','쪽','편','이편','저편']
    if any(k in ko for k in direction_ko):
        return '방향/위치'

    # 22. 정도/양적 개념
    quant_ko = ['정도','한도','한계','수준','범위','비율','비중','분량','용량','최소','최대','평균','합계','총','전부','모두','일부','절반','전체','나머지','대부분','소수','다수','대다수']
    if any(k in ko for k in quant_ko):
        return '정도/양적 개념'

    # 23. 발화/커뮤니케이션 동사 (추상)
    comm_ko = ['말하다','전하다','알리다','보고','설명','발표','주장','반론','답변','질문','의논','상담','협의','논의','토론','소개','언급','지적','비판','칭찬','격려','위로','비난','고백','선언','요청','부탁','명령','지시','제안','권유','충고','경고','허락']
    if any(k in ko for k in comm_ko):
        return '발화/커뮤니케이션'

    # 24. 결과/성취 추상어
    result_ko = ['성공','실패','달성','완성','완료','종료','시작','착수','도전','극복','승리','패배','합격','불합격','채용','해고','취업','퇴직','졸업','입학']
    if any(k in ko for k in result_ko):
        return '결과/성취 추상어'

    # 25. 경제/거래 추상어
    econ_ko = ['가격','비용','요금','수입','지출','이익','손해','세금','급여','월급','연봉','예산','저축','투자','할인','판매','구매','거래','수출','수입','무역']
    if any(k in ko for k in econ_ko):
        return '경제/거래 추상어'

    # ─── 원래 카테고리가 abstract/adverb인데 분류 안 된 것 ───
    if cat in ['abstract_nouns', 'adverbs_functional']:
        return '미분류 추상어'
    
    return None

# ──────────────────────────────────
# 실행
# ──────────────────────────────────
narrative_indicators = [
    'running', 'walking', 'sleeping', 'eating', 'cooking',
    'library', 'school', 'kitchen', 'bedroom', 'office', 'station', 'cafe',
    'friend', 'grandmother', 'mother', 'father', 'boy', 'girl',
    'cherry blossom', 'autumn leaves', 'rain', 'snow',
    'reading', 'studying', 'shopping',
]

def count_narrative_density(prompt):
    if not prompt or prompt == 'N/A':
        return 0
    pl = prompt.lower()
    return sum(1 for ind in narrative_indicators if ind in pl)

type_groups = defaultdict(list)
for w in all_words:
    stype = classify_v2(w)
    if stype:
        type_groups[stype].append(w)

print("=" * 70)
print("  확장 분류 결과 (v2)")
print("=" * 70)

for stype in sorted(type_groups.keys(), key=lambda x: -len(type_groups[x])):
    words = type_groups[stype]
    
    high_risk_count = 0
    for w in words:
        w_id = w.get('id', '')
        kanji = w.get('kanji', '')
        prompt = cache.get(w_id, cache.get(kanji, ''))
        if count_narrative_density(prompt) >= 2:
            high_risk_count += 1
    
    flag = "🚨" if high_risk_count > 5 else "⚠️" if high_risk_count > 0 else "✅"
    print(f"  {flag} [{stype:20s}] 총 {len(words):4d}개 │ 서사과밀: {high_risk_count:3d}개")

classified = sum(len(v) for k,v in type_groups.items() if k != '미분류 추상어')
unclassified = len(type_groups.get('미분류 추상어', []))
total_abstract = classified + unclassified
concrete = len(all_words) - total_abstract

print(f"\n{'=' * 70}")
print(f"  커버리지: {classified}/{total_abstract} 추상어 분류 완료 ({classified/total_abstract*100:.1f}%)")
print(f"  미분류 잔여: {unclassified}개 ({unclassified/total_abstract*100:.1f}%)")
print(f"  구체적 단어(커버 불필요): {concrete}개")
print(f"{'=' * 70}")

# 미분류 잔여 의미 키워드 빈도
if unclassified > 0:
    meaning_words = defaultdict(int)
    for w in type_groups['미분류 추상어']:
        ko = w.get('korean', '')
        for tok in re.split(r'[;,/\s・~～〜()（）]+', ko):
            tok = tok.strip()
            if len(tok) >= 2:
                meaning_words[tok] += 1
    
    print(f"\n미분류 잔여 의미 키워드 빈도 (Top 30):")
    for kw, cnt in sorted(meaning_words.items(), key=lambda x: -x[1])[:30]:
        print(f"  {kw}: {cnt}")
    
    # 미분류 중 서사 과밀 상위
    print(f"\n미분류 서사 과밀 (밀도 ≥ 3, 상위 20개):")
    risks = []
    for w in type_groups['미분류 추상어']:
        w_id = w.get('id','')
        kanji = w.get('kanji','')
        prompt = cache.get(w_id, cache.get(kanji, ''))
        d = count_narrative_density(prompt)
        if d >= 3:
            risks.append((d, w_id, kanji, w.get('hiragana',''), w.get('korean',''), prompt[:120]))
    risks.sort(reverse=True)
    for d, wid, kj, kn, ko, pr in risks[:20]:
        print(f"  [{wid}] {kj}({kn}) = {ko} │ 밀도:{d}")
        print(f"    {pr}...")
