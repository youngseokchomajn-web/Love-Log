import json
import re

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def refined_sweep():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)

    cat_path = f"{ROOT_DIR}/utils/image_pipeline_v2/word_categories_all.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        categories_data = json.load(f)

    p1_text_fallback = []       # 한국어/한자 텍스트가 프롬프트의 핵심인 경우
    p2_verb_static_scene = []   # 동사인데 정적 배경/건물만 있고 동작이 전혀 없는 경우
    p3_small_obj_buried = []    # 소형 사물이 배경에 매몰된 경우
    p4_space_human_dominant = [] # 공간 명사인데 인물이 주역인 경우

    # ─── Pattern 1: 텍스트 폴백 (AI가 한국어/한자를 해석 못하는 근본 문제) ───
    # "iconic visual illustration representing '한국어'" 꼴이면 확실한 문제
    # 그런데 실제 시각 묘사 태그가 뒤에 전혀 없는 것만 잡아야 함
    TEXT_FALLBACK_PATTERN = re.compile(
        r"iconic visual illustration representing\s+['\"]",
        re.IGNORECASE
    )
    FOOD_FALLBACK_PATTERN = re.compile(
        r"delicious fresh food dish\s*\(",
        re.IGNORECASE
    )
    CLOTHING_FALLBACK_PATTERN = re.compile(
        r"neatly arranged clothing item\s*\(",
        re.IGNORECASE
    )

    # ─── Pattern 2: 동사인데 동작 묘사가 정말 없는 경우만 ───
    # 너무 넓게 잡으면 안 됨. action_verbs 카테고리이면서,
    # 프롬프트에 인물 동작을 암시하는 태그가 하나도 없는 경우만
    HUMAN_ACTION_INDICATORS = [
        "person", "boy", "girl", "man", "woman", "child", "people",
        "hand", "handing", "holding", "giving", "receiving", "throwing",
        "catching", "picking", "pointing", "pulling", "pushing", "lifting",
        "carrying", "walking", "running", "sitting", "standing", "eating",
        "drinking", "cooking", "reading", "writing", "talking", "speaking",
        "crying", "laughing", "smiling", "sleeping", "working", "playing",
        "dancing", "singing", "fighting", "swimming", "climbing", "opening",
        "closing", "cutting", "washing", "cleaning", "buying", "selling",
        "exchanging", "helping", "teaching", "learning", "looking",
        "watching", "listening", "reaching", "bowing", "waving",
        "expression", "gesture", "action", "motion", "movement",
        "1boy", "1girl", "anime character", "young", "old"
    ]

    # ─── Pattern 3: 소형 사물이 배경에 매몰 ───
    SMALL_OBJECTS = {
        "젓가락": "chopsticks", "숟가락": "spoon", "포크": "fork",
        "나이프": "knife", "안경": "glasses", "바늘": "needle",
        "단추": "button", "열쇠": "key", "반지": "ring",
        "지우개": "eraser", "우표": "stamp", "동전": "coin",
        "연필": "pencil", "볼펜": "pen", "가위": "scissors",
        "클립": "clip", "핀": "pin", "못": "nail",
        "나사": "screw", "성냥": "match", "라이터": "lighter",
        "컵": "cup", "숟가락": "spoon", "빗": "comb",
        "칫솔": "toothbrush", "소포": "parcel"
    }
    CLOSE_UP_INDICATORS = [
        "close-up", "close up", "closeup", "macro", "single object",
        "isolated", "centered", "solo object", "clear focus",
        "no humans", "no people", "1 object"
    ]

    # ─── Pattern 4: 공간 명사인데 인물이 주역 ───
    SPACE_NOUNS_KR = [
        "부엌", "주방", "공원", "도서관", "화장실", "욕실", "공장",
        "병원", "학교", "교실", "미술관", "박물관", "체육관", "정원",
        "식당", "사무실", "침실", "거실", "복도", "계단", "지하실",
        "옥상", "발코니", "창고", "서재", "연구실", "실험실"
    ]
    HUMAN_DOMINANT_TAGS = [
        "mother cooking", "doctor operating", "teacher teaching",
        "students sitting", "students chatting", "student studying",
        "children playing", "worker", "chef cooking", "nurse",
        "librarian", "swimmer", "player"
    ]
    SPACE_INDICATORS = [
        "interior", "exterior", "architecture", "no people", "no humans",
        "empty room", "quiet space", "panoramic", "wide shot"
    ]

    for cat_name, word_list in categories_data.items():
        for w in word_list:
            w_id = w["id"]
            prompt = tags_cache.get(w_id, "")
            prompt_lower = prompt.lower()
            korean = w.get("korean", "")
            kanji = w.get("kanji", "")
            english = w.get("english", "")
            level = w.get("level", "n5").upper()

            entry = {
                "id": w_id, "level": level, "kanji": kanji,
                "korean": korean, "category": cat_name,
                "prompt": prompt
            }

            # ── P1: 텍스트 폴백 ──
            if (TEXT_FALLBACK_PATTERN.search(prompt) or
                FOOD_FALLBACK_PATTERN.search(prompt) or
                CLOTHING_FALLBACK_PATTERN.search(prompt)):
                # 음식 관련 단어인데 food dish 템플릿이면 OK
                is_food = any(k in korean for k in ["죽", "음식", "요리", "밥", "과자", "국", "스프"])
                is_clothing = any(k in korean for k in ["옷", "정장", "양복", "양말", "신발", "모자", "코트"])
                if FOOD_FALLBACK_PATTERN.search(prompt) and is_food:
                    continue
                if CLOTHING_FALLBACK_PATTERN.search(prompt) and is_clothing:
                    continue
                p1_text_fallback.append(entry)

            # ── P2: 동사인데 동작 없음 (action_verbs 카테고리만) ──
            if cat_name == "action_verbs":
                has_human_action = any(ind in prompt_lower for ind in HUMAN_ACTION_INDICATORS)
                if not has_human_action:
                    p2_verb_static_scene.append(entry)

            # ── P3: 소형 사물 매몰 ──
            matched_small = False
            for kr_obj, en_obj in SMALL_OBJECTS.items():
                if kr_obj in korean:
                    matched_small = True
                    break
            if matched_small:
                has_closeup = any(ci in prompt_lower for ci in CLOSE_UP_INDICATORS)
                if not has_closeup:
                    p3_small_obj_buried.append(entry)

            # ── P4: 공간명사 인물우세 ──
            is_space = any(sn in korean for sn in SPACE_NOUNS_KR)
            if is_space:
                has_human_dominant = any(ht in prompt_lower for ht in HUMAN_DOMINANT_TAGS)
                has_space_framing = any(si in prompt_lower for si in SPACE_INDICATORS)
                if has_human_dominant and not has_space_framing:
                    p4_space_human_dominant.append(entry)

    # 중복 제거 (여러 패턴에 걸린 ID는 우선순위 높은 패턴만)
    all_ids = set()
    deduped = {"p1": [], "p2": [], "p3": [], "p4": []}
    for item in p1_text_fallback:
        all_ids.add(item["id"])
        deduped["p1"].append(item)
    for item in p2_verb_static_scene:
        if item["id"] not in all_ids:
            all_ids.add(item["id"])
            deduped["p2"].append(item)
    for item in p3_small_obj_buried:
        if item["id"] not in all_ids:
            all_ids.add(item["id"])
            deduped["p3"].append(item)
    for item in p4_space_human_dominant:
        if item["id"] not in all_ids:
            all_ids.add(item["id"])
            deduped["p4"].append(item)

    total = len(deduped["p1"]) + len(deduped["p2"]) + len(deduped["p3"]) + len(deduped["p4"])

    print("=== 정밀 재검증: 4대 패턴 전수 스윕 결과 ===\n")
    print(f"  P1. 추상어 텍스트 폴백 (AI가 한국어/한자 못 읽음)  : {len(deduped['p1'])}개")
    print(f"  P2. 동사인데 인물/동작 태그 완전 부재              : {len(deduped['p2'])}개")
    print(f"  P3. 소형 사물이 배경에 매몰 (close-up 없음)        : {len(deduped['p3'])}개")
    print(f"  P4. 공간 명사인데 인물 동작이 주역                 : {len(deduped['p4'])}개")
    print(f"\n  총 개선 필요 (중복 제거): {total}개 / 8,424개 (약 {total*100/8424:.1f}%)")

    # 각 패턴 샘플 5개씩 출력
    for pname, plist in deduped.items():
        print(f"\n--- {pname} 샘플 (최대 5개) ---")
        for item in plist[:5]:
            print(f"  {item['id']} | {item['kanji']} ({item['korean']}) [{item['category']}]")
            print(f"    → {item['prompt'][:100]}...")

    report = {
        "p1_text_fallback": deduped["p1"],
        "p2_verb_static": deduped["p2"],
        "p3_small_obj_buried": deduped["p3"],
        "p4_space_human": deduped["p4"],
        "total_unique": total
    }
    report_path = f"{ROOT_DIR}/utils/image_pipeline_v2/pattern_sweep_refined.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[Success] 정밀 리포트 저장: utils/image_pipeline_v2/pattern_sweep_refined.json")


if __name__ == "__main__":
    refined_sweep()
