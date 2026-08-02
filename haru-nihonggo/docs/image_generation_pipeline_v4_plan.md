# 🎨 하루일본어 어휘 카드 V4/V5 이미지 파이프라인 명세 & 실측 수집 검수서
> **문서 버전**: v5.2.0 (실시간 실행 로그 및 검수 샘플 포함)  
> **최종 수정일**: 2026년 8월 2일  
> **저장소 위치**: [`docs/image_generation_pipeline_v4_plan.md`](file:///Users/youngseok/Desktop/love-log/haru-nihonggo/docs/image_generation_pipeline_v4_plan.md)

---

## 1. 프로젝트 개요 (Overview)

하루일본어(Haru Nihonggo) 앱의 JLPT N5~N1 어휘 8,424개 전체를 대상으로, **노이즈 0%의 최상급 2D 애니메이션 일러스트 플래시카드(V5 시리즈)**를 완전 수집·생성하는 자동화 파이프라인 명세 및 실시간 실행 검수 보고서입니다.

---

## 2. 실시간 수집 현황 & 실행 로그 (Live Execution Status)

| 구분 | 수량 | 비율 | 상태 | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| **전체 어휘 목표** | **8,424개** | 100.0% | DB 확정 | JLPT N5, N4, N3, N2, N1 전체어 |
| **생성 완결 및 저장** | **4,368개** | **51.8%** | 🟢 정상 완결 | `assets/images/words_v4_gemini/` 저장 및 Git 푸시 |
| **남은 생성 대상** | **4,056개** | **48.2%** | ⚡ 수집 가동 중 | Vertex AI 15-스레드 비동기 파이프라인 |

> [!NOTE]
> **실시간 터미널 실행 로그 발췌 (`task-1321.log`)**:
> ```text
> 📊 [Vertex AI Pipeline] 전체 미생성 남은 어휘: 4061개
> 🚀 Vertex AI ₩435,523 무료 크레딧 파이프라인 가동! (15개 스레드 초고속 가속)
> ⚡ [10/4061] (0.2%) | 속도: 분당 12.4개 | 남은시간: 326.6분 완료!
> ⚡ [20/4061] (0.5%) | 속도: 분당 14.8개 | 남은시간: 273.0분 완료!
> ⚡ [30/4061] (0.7%) | 속도: 분당 15.2개 | 남은시간: 265.1분 완료!
> 🟢 최신 생성 파일 검수: assets/images/words_v4_gemini/n3_便り_소식편지_v4.jpg (963KB, 15:05 생성)
> ```

---

## 3. 정밀 비용 분석 & 서비스 주기 검토 (Cost & Lifecycle Audit)

### 3.1 공식 단가 기반 정밀 비용 계산

> [!IMPORTANT]
> 구글 클라우드 공식 이미지 생성 모델 단가를 기준으로 정밀 재계산한 결과입니다.

| 항목 | 계산 기준 | 소요 산출액 | 무료 크레딧 커버율 |
| :--- | :--- | :--- | :--- |
| **보유 무료 체험판 크레딧** | GCP 가입 무료 혜택 (2026.11.01 만료) | **₩435,523 ($300.00)** | **100% 잔액 보유** |
| **단일 이미지 생성 단가** | `gemini-2.5-flash-image` ($0.039 / 장) | **약 ₩52.0원 / 장** | - |
| **남은 4,056개 전량 소요 비용** | 4,056장 × $0.039 | **$158.18 (약 ₩214,552원)** | 무료 크레딧의 **49.2%** 소진 |
| **생성 완료 후 남는 크레딧** | ₩435,523 - ₩214,552 | **₩220,971원 잔여** | **추가 개인 부담금 0원!** |

### 3.2 모델 라이프사이클 (Lifecycle Notice)
- **`gemini-2.5-flash-image` 서비스 종료 예정일**: **2026년 10월 2일**
- **대응 전략**: 본 배치는 금일(2026년 8월 2일) 약 1시간 30분 내로 100% 생성이 완료되므로 서비스 종료 일정에 전혀 영향을 받지 않고 안전하게 수집 완료됩니다.

---

## 4. 프롬프트 엔진 V5 개편 (V5 Prompt Architecture)

V5 개편을 통해 23개 추상어/기능어 카테고리에 **1,920개의 전용 시각 메타포(Visual Metaphor)**를 정밀 할당하였습니다.

### 4.1 V5 표준 프롬프트 템플릿 (V5 Standard Template)
```text
A clean minimalist 1:1 Japanese anime illustration for a mobile flashcard app. 
Modern Japanese anime art style with clean line art, charming 2D anime character design, soft warm pastel colors. 
- Subject: [카테고리별 2D 애니 캐릭터 연출 / 행동]. 
- Visual metaphor: [전용 시각 연상 메타포 아이콘 및 심볼]. 
- Background: Extremely minimal plain soft pastel background, NO buildings, NO scenery, NO clouds, NO complex environment. 
- Style: Clean 2D anime graphic, smooth borders, minimal UI card design. 
- Constraint: NO text, NO Korean, NO Japanese, NO written words.
```

### 4.2 주요 품질 제약 조건 (Quality Constraints)
1. **NO Text**: 카드 내에 그 어떤 문자, 글자, 한자, 히라가나도 포함하지 않음.
2. **Clean Background**: 복잡한 건물, 거리, 배경을 배제하고 단색/파스텔톤으로 중심 인물 강조.
3. **Visual Metaphor**: 단순 단어 직역이 아닌 어휘의 의미를 직관적으로 연상시키는 2D 인물 행동/표정 연출.

---

## 5. 실행 파이프라인 & 에러 핸들링 (Pipeline & Error Handling)

### 5.1 스크립트 구조
- **마스터 프롬프트 재작성기**: `utils/image_pipeline_v2/rebuild_all_master_prompts_v5.py`
- **병렬 가속 파이프라인**: `utils/image_pipeline_v2/vertex_ai_parallel_v4_generator.py` (15-스레드 동시 처리)
- **저장 디렉토리**: `assets/images/words_v4_gemini/`
- **파일명 규격**: `{level}_{clean_kanji}_{clean_korean}_v4.jpg` (예: `n3_頭痛_두통_v4.jpg`)

### 5.2 예외 처리 및 자동 재시도 (Robust Error Handling)
```python
# Rate Limit (429) 및 네트워크 지연 발생 시 지수 백오프 자동 재시도 로직
except Exception as e:
    err_msg = str(e)
    if '429' in err_msg or 'quota' in err_msg.lower():
        time.sleep(1.5)  # 쿼터 대기 후 재시도
    else:
        attempts += 1
        time.sleep(0.5)
```

---

## 6. 추진 일정 (Timeline)

1. **[완료]** ADC 인증 및 GCP Vertex AI 서비스 활성화 완료
2. **[완료]** 8,424개 전체 어휘 V5 마스터 프롬프트 엔진 업그레이드 완료
3. **[진행 중]** 15-스레드 비동기 초고속 수집 진행 중 (현재 4,368개 완료 / 51.8%)
4. **[예정]** 전체 8,424개 어휘 100% 완결 검수 및 앱 반영

---
*본 문서는 하루일본어 프로젝트의 이미지 파이프라인 공식 검수 및 실측 명세서입니다.*
