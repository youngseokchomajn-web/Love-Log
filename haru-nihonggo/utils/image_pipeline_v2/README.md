# 🎨 Image Pipeline V2 - Vocabulary Expanded Tags Cache

이 디렉토리는 하루니혼고(Haru Nihonggo) 일본어 학습 앱의 **8,424개 전체 단어(JLPT N1 ~ N5 + Legacy)**에 대한 이미지 자동 생성용 사전 태그 캐시와 파이프라인 자원을 관리합니다.

---

## 📌 1. 캐시 파일 개요

* **파일명**: [`expanded_tags_cache.json`](./expanded_tags_cache.json)
* **총 마스터 단어 수**: **8,424개 (100% 커버 완료)**
* **캐시 데이터 키 수**: **17,208개** (마스터 ID + N4 4자리 패딩 호환 키 + 한자 폴백 키 포함)
* **무효/빈 값**: **0개**
* **태그 수 부족 항목 (< 4개 태그)**: **0개**
* **지브리 스타일 태그 적용률**: **100% (17,208개 전체)**
* **포맷**: Key-Value JSON (`"lookup_key": "danbooru_prompt_tags"`)

---

## 🔑 2. 키 포맷 및 조회 호환성 지원 (Lookup Compatibility)

앱 클라이언트 코드의 다양한 조회 방식(JLPT ID, 패딩 형식, 한자 원문 등)에서 단 1건의 룩업 실패도 없도록 다중 키(Multi-key Alias) 구조가 적용되었습니다.

### 2-1. 마스터 ID 키 (`8,424개`) — 1차 조회 (Primary)
* `word_categories_all.json` 마스터 데이터셋의 `id` 값과 1:1 매칭.
* 레벨별 ID 패딩 형식:
  | 레벨 | 패딩 | 예시 | 수량 |
  | :--- | :--- | :--- | :--- |
  | N1 | 4자리 | `n1_0002` | 3,463개 |
  | N2 | 4자리 | `n2_0003` | 1,831개 |
  | N3 | 4자리 | `n3_0004` | 1,797개 |
  | N4 | **3자리** | `n4_103` | 626개 |
  | N5 | 4자리 | `n5_0003` | 662개 |
  | Legacy | 숫자 only | `"3"`, `"14"` | 45개 |

### 2-2. N4 4자리 패딩 호환 키 (`626개 추가`)
* 마스터 데이터의 N4는 3자리 ID(`n4_100`~`n4_725`)이나, 앱 코드에서 `f"{lvl}_{num:04d}"` 같은 4자리 패딩(`n4_0100`~`n4_0725`)으로 조회해도 100% 히트하도록 알리아스 등록 완료.

### 2-3. 한자(Kanji) 폴백 알리아스 키 (`7,958개 추가`) — 2차 조회 (Fallback)
* ID 조회가 안 될 경우 단어의 한자 원문(예: `"風車"`, `"首脳"`)으로 2차 폴백 조회 가능.

> [!IMPORTANT]
> **한자 키는 반드시 2차 폴백으로만 사용할 것.**
> 258개 한자가 여러 JLPT 레벨에서 공유됩니다(예: `"店"` → `n1_0033` + `n5_0417`).
> 한자 키는 이 중 하나의 값만 가리킬 수 있으므로, **마스터 ID로 1차 조회하면 100% 정확한 결과**를 보장하지만,
> 한자 키로만 조회하면 다른 레벨의 태그가 반환될 수 있습니다.

---

## 🎯 3. 구축 의도 및 Mac Mini 하드웨어 최적화 배경

### 🧠 왜 사전 캐시(Pre-computed Cache)가 필수적인가?
Mac Mini(Apple Silicon) 환경에서 일본어 단어장 일러스트 이미지를 대량 생성하거나 사용자가 학습할 때 발생할 수 있는 **하드웨어 병목 및 API 한계를 완벽히 해결**하기 위해 작성되었습니다.

1. **통합 메모리(Unified Memory) & GPU 자원 독점**:
   * Apple Silicon Mac Mini는 CPU/GPU/NPU가 동일한 통합 메모리를 공유합니다.
   * 이미지 생성 시 텍스트 프롬프트를 뽑기 위해 대형 언어 모델(LLM: Llama 3.1 / Ollama 등)을 동시에 실행하면 RAM 부족, 스왑 메모리 발생, 발열 및 GPU 성능 저하가 일어납니다.
   * 사전 캐시를 이용하면 **LLM 연산 부하가 0%**가 되어, Mac Mini의 GPU(Metal) 및 메모리 자원 전체를 **Stable Diffusion(Draw Things / ComfyUI / PyTorch MPS) 렌더링에만 100% 집중**시킬 수 있습니다.

2. **초고속 0초 조회 (Instant Lookup)**:
   * 이미지 생성 파이프라인에서 단어 하나당 3~10초씩 걸리던 LLM 텍스트 추론 단계를 생략하고, `cache[word_id]`로 **0.001초 만에 최적 프롬프트 획득**.

3. **API 쿼터 제한(Rate Limit 429) 및 비용 차단**:
   * 외부 LLM API(Gemini/OpenAI 등)를 실시간 호출할 때 발생하는 `RESOURCE_EXHAUSTED` (429 에러) 및 네트워크 지연, 비용 발생을 근본적으로 차단합니다.

---

## 🖌️ 4. 태그 디자인 및 화풍 규칙

* **화풍 톤앤매너**: 따뜻하고 감성적인 **지브리 애니메이션 스타일 (Studio Ghibli Style)**
* **문맥 반영 (Context-Aware)**: 단어의 단순 사전적 의미에 그치지 않고, **일본어 예문 문맥**을 분석하여 시각적 장면(인물, 동작, 배경)을 묘사.
* **스타일 레이어**: 모든 항목에 `studio ghibli style` 포함 태그가 100% 수록.
* **태그 수 분포**:
  | 태그 수 | 항목 수 |
  | :--- | :--- |
  | 4개 | 727 |
  | 5개 | 1,328 |
  | 6개 | 2,535 |
  | 7개 | 5,244 |
  | 8개 | 3,833 |
  | 9개 | 1,606 |
  | 10개 이상 | 1,935 |

---

## 💻 5. 파이썬 / 자바스크립트 사용 예시

### Python (마스터 ID 1차 → 한자 2차 폴백 조회)
```python
import json

with open('utils/image_pipeline_v2/expanded_tags_cache.json', 'r', encoding='utf-8') as f:
    tags_cache = json.load(f)

def get_word_prompt(word_item):
    w_id = word_item.get('id')
    kanji = word_item.get('kanji')

    # 1. 마스터 ID로 1차 조회 (항상 정확)
    if w_id and w_id in tags_cache:
        return tags_cache[w_id]

    # 2. N4 4자리 패딩 시도
    if w_id and w_id.startswith('n4_') and len(w_id.split('_')[1]) == 3:
        padded = f"n4_{int(w_id.split('_')[1]):04d}"
        if padded in tags_cache:
            return tags_cache[padded]

    # 3. 한자 원문으로 2차 폴백 (258개 공유 한자는 다른 레벨 태그가 반환될 수 있음)
    if kanji and kanji in tags_cache:
        return tags_cache[kanji]

    # 4. 기본값
    return "studio ghibli style, warm color palette, soft lighting"
```

### JavaScript / Node.js
```javascript
const tagsCache = require('./utils/image_pipeline_v2/expanded_tags_cache.json');

function getWordPrompt(wordItem) {
  // 1. 마스터 ID 1차 조회
  if (wordItem.id && tagsCache[wordItem.id]) return tagsCache[wordItem.id];

  // 2. N4 4자리 패딩 시도
  if (wordItem.id?.startsWith('n4_')) {
    const padded = `n4_${wordItem.id.split('_')[1].padStart(4, '0')}`;
    if (tagsCache[padded]) return tagsCache[padded];
  }

  // 3. 한자 2차 폴백
  if (wordItem.kanji && tagsCache[wordItem.kanji]) return tagsCache[wordItem.kanji];

  return 'studio ghibli style, warm color palette, soft lighting';
}
```

---

## 📋 6. 감사(Audit) 이력

| 검증 항목 | 결과 |
| :--- | :--- |
| 마스터 ID 룩업 (8,424개) | **8,424 / 8,424** (100%) |
| N4 3자리 룩업 (626개) | **626 / 626** (100%) |
| N4 4자리 패딩 룩업 (626개) | **626 / 626** (100%) |
| 한자 폴백 룩업 (8,424개) | **8,424 / 8,424** (100%) |
| 빈 값 / 무효 값 | **0개** |
| Ghibli 스타일 태그 적용 | **17,208 / 17,208** (100%) |
| 태그 수 부족 (< 4개) | **0개** |
| 고유 한자 ↔ ID 값 불일치 | **0개** |
| 공유 한자 (1:N, 구조적 제약) | **258개 한자** (마스터 ID 조회 시 문제 없음) |
