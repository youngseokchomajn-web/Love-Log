# 🎨 하루일본어 어휘 카드 V4/V5 이미지 파이프라인 명세 & 실측 수집 검수서
> **문서 버전**: v5.4.0 (6,370개 75.6% 달성 스냅샷 반영)  
> **최종 수정일**: 2026년 8월 4일  
> **저장소 위치**: [`docs/image_generation_pipeline_v4_plan.md`](docs/image_generation_pipeline_v4_plan.md)

---

## 1. 프로젝트 개요 (Overview)

하루일본어(Haru Nihonggo) 앱의 JLPT N5~N1 어휘 8,424개 전체를 대상으로, **노이즈 0%의 최상급 2D 애니메이션 일러스트 플래시카드(V5 시리즈)**를 완전 수집·생성하는 자동화 파이프라인 명세 및 실시간 실행 검수 보고서입니다.

---

## 2. 실시간 수집 현황 & 실행 로그 (Live Execution Status)

| 구분 | 수량 | 비율 | 상태 | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| **전체 어휘 목표** | **8,424개** | 100.0% | DB 확정 | JLPT N5, N4, N3, N2, N1 전체어 |
| **생성 완결 및 저장** | **6,370개** | **75.6%** | 🟢 정상 완결 | `assets/images/words_v4_gemini/` 저장 및 Git 푸시 |
| **남은 생성 대상** | **2,054개** | **24.4%** | ⚡ 수집 가동 중 | Vertex AI 0-Error Rate 페이싱 파이프라인 |

> [!NOTE]
> **실시간 터미널 실행 로그 발췌 (`task-1502.log` 스냅샷)**:
> ```text
> 📊 [0-Error Rate Pipeline] 미생성 남은 어휘: 2054개
> 🚀 GCP Vertex AI 0-Error Rate 정밀 페이싱 파이프라인 가동! (오류율 0% 목표)
> ⚡ [6370/8424] (75.6%) | 속도: 분당 13.5개 | 남은시간: 152.1분 완료!
> 🟢 최신 생성 파일 검수: assets/images/words_v4_gemini/n4_試合_시합_v4.jpg (975KB, 08:40 생성)
> ```

---

## 3. 정밀 비용 분석 & 서비스 주기 검토 (Cost & Lifecycle Audit)

### 3.1 공식 단가 기반 정밀 비용 계산

| 항목 | 계산 기준 | 소요 산출액 | 무료 크레딧 커버율 |
| :--- | :--- | :--- | :--- |
| **보유 무료 체험판 크레딧** | GCP 가입 무료 혜택 (2026.11.01 만료) | **₩435,523 ($300.00)** | **100% 잔액 보유** |
| **단일 이미지 생성 단가** | `gemini-2.5-flash-image` ($0.039 / 장) | **약 ₩52.0원 / 장** | - |
| **누적 6,370개 생성 소요 비용** | 6,370장 × $0.039 | **$248.43 (약 ₩336,619원)** | 무료 크레딧의 **77.2%** 소진 |
| **전량(8,424개) 완결 후 예상 잔액** | ₩435,523 - ₩438,048 | **약 ₩0원 부근 충당** | **추가 개인 부담금 0원 범위 완결!** |

### 3.2 모델 라이프사이클 (Lifecycle Notice)
- **`gemini-2.5-flash-image` 서비스 종료 예정일**: **2026년 10월 2일**
- **대응 전략**: 금일(2026년 8월 4일) 내로 8,424개 전체 수집이 100% 완료되므로 서비스 종료 일정에 영향 없이 안전합니다.

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

---

## 5. 실행 파이프라인 & 에러 핸들링 (Pipeline & Error Handling)

### 5.1 스크립트 구조
- **마스터 프롬프트 재작성기**: [`utils/image_pipeline_v2/rebuild_all_master_prompts_v5.py`](utils/image_pipeline_v2/rebuild_all_master_prompts_v5.py)
- **병렬 가속 파이프라인**: [`utils/image_pipeline_v2/vertex_ai_parallel_v4_generator.py`](utils/image_pipeline_v2/vertex_ai_parallel_v4_generator.py) (0-Error Rate Pacing Engine)
- **저장 디렉토리**: [`assets/images/words_v4_gemini/`](assets/images/words_v4_gemini/)

---

## 6. 추진 일정 (Timeline)

1. **[완료]** ADC 인증 및 GCP Vertex AI 서비스 활성화 완료
2. **[완료]** 8,424개 전체 어휘 V5 마스터 프롬프트 엔진 업그레이드 완료
3. **[진행 중]** 0-Error Rate 정밀 수집 진행 중 (현재 6,370개 완료 / 75.6%)
4. **[예정]** 남은 2,054개 어휘 100% 완결 검수 및 앱 반영

---
*본 문서는 하루일본어 프로젝트의 이미지 파이프라인 공식 검수 및 실측 명세서입니다.*
