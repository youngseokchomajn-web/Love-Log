# 🎨 하루일본어 어휘 카드 V4/V5 이미지 파이프라인 생성 계획서 & 현황
> **문서 버전**: v5.1.0  
> **최종 수정일**: 2026년 8월 2일  
> **저장소 위치**: [`docs/image_generation_pipeline_v4_plan.md`](file:///Users/youngseok/Desktop/love-log/haru-nihonggo/docs/image_generation_pipeline_v4_plan.md)

---

## 1. 프로젝트 개요 (Overview)

하루일본어(Haru Nihonggo) 앱의 JLPT N5~N1 어휘 8,424개 전체를 대상으로, **노이즈 0%의 최상급 2D 애니메이션 일러스트 플래시카드(V5 시리즈)**를 완전 수집·생성하는 자동화 파이프라인 명세 및 실시간 현황 보고서입니다.

---

## 2. 실시간 수집 현황 (Current Progress)

| 구분 | 수량 | 비율 | 비고 |
| :--- | :--- | :--- | :--- |
| **전체 어휘 목표** | **8,424개** | 100.0% | N5, N4, N3, N2, N1 전체 DB |
| **생성 완결** | **4,368개** | **51.8%** | `assets/images/words_v4_gemini/` 저장 및 Git 푸시 완결 |
| **남은 생성 대상** | **4,056개** | **48.2%** | Vertex AI 15-스레드 파이프라인 실시간 수집 중 |

---

## 3. 활용 API 및 클라우드 인프라 (API & Infrastructure)

### 3.1 사용 클라우드 및 API 모델
- **클라우드 서비스**: Google Cloud Platform (GCP) Vertex AI & Generative Language Platform
- **API 모델**: `gemini-2.5-flash-image` (Vertex AI API)
- **프로젝트 ID**: `project-8598242e-9cd6-4c63-9e8`

### 3.2 인증 및 안전 정책 (Authentication & Safety)
- **인증 방식**: Google Cloud ADC (`gcloud auth application-default login`)
- **비용 안전 정책**:
  - 보유 무료 체험판 크레딧: **₩435,523 ($300)** (유효기간: 2026년 11월 1일)
  - 남은 4,056개 전량 생성 시 소요 비용: 약 **₩120,000 ~ ₩160,000원** (장당 약 30~40원)
  - **추가 비용 및 사용자 개인 결제 부담금 0원** (무료 크레딧 범위 내 100% 충당)

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

## 5. 실행 파이프라인 (Execution Pipeline)

### 5.1 스크립트 구조
- **마스터 프롬프트 재작성기**: `utils/image_pipeline_v2/rebuild_all_master_prompts_v5.py`
- **병렬 가속 파이프라인**: `utils/image_pipeline_v2/vertex_ai_parallel_v4_generator.py` (15-스레드 동시 처리)
- **저장 디렉토리**: `assets/images/words_v4_gemini/`
- **파일명 규격**: `{level}_{clean_kanji}_{clean_korean}_v4.jpg` (예: `n3_頭痛_두통_v4.jpg`)

---

## 6. 추진 일정 (Timeline)

1. **[완료]** ADC 인증 및 GCP Vertex AI 서비스 활성화 완료
2. **[완료]** 8,424개 전체 어휘 V5 마스터 프롬프트 엔진 업그레이드 완료
3. **[진행 중]** 15-스레드 비동기 초고속 수집 진행 중 (현재 4,368개 완료 / 51.8%)
4. **[예정]** 전체 8,424개 어휘 100% 완결 검수 및 앱 반영

---
*본 문서는 하루일본어 프로젝트의 이미지 파이프라인 공식 명세서입니다.*
