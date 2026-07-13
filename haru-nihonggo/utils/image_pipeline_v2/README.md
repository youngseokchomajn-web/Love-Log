# 단어 카드 이미지 생성 파이프라인 (v2)

JLPT 단어(N1~N5, 8,424개)의 학습용 카드 이미지를 생성한다.
**머리(태그/프롬프트)는 Claude/Gemini, 렌더링은 로컬 SDXL(Animagine XL 3.1)** 구조.

## 구성
- `word_categories_all.json` — 전 레벨 단어를 5개 카테고리로 분류한 파일
  (`concrete_nouns` / `abstract_nouns` / `action_verbs` / `adjectives_states` / `adverbs_functional`).
  카테고리마다 프롬프트 스타일 템플릿이 다르다.
- `curated_tags.json` — 손으로 작성한 단어별 Danbooru 태그(id→tags). **있으면 최우선 사용.**
- `generator_v2.py` — 태그 확장(큐레이션 우선 → 없으면 Gemini) 후 SDXL로 렌더.

## 실행 (렌더링은 로컬 GPU 필요, macOS MPS)
```bash
# venv 활성화된 python 사용 (word_card_generator/venv)
cd haru-nihonggo

# 특정 단어들만
python utils/image_pipeline_v2/generator_v2.py \
  --categories utils/image_pipeline_v2/word_categories_all.json \
  --ids n5_0003,n5_0010

# 카테고리 전체에서 앞 N개(테스트용)
python utils/image_pipeline_v2/generator_v2.py \
  --categories utils/image_pipeline_v2/word_categories_all.json --count 20

# 이미 있으면 건너뜀. 다시 뽑으려면 --overwrite
```
출력: `assets/images/words_v2/{id}_{category}_{일본어}_{한국어}.png` (832×1216).
파일명이 앱의 `getWordImage`(id 기반 매칭)와 호환되므로, 다 뽑은 뒤
`wordImages.ts`를 `words_v2/` 기준으로 재생성하면 앱에 바로 반영된다.

## 품질을 높이려면
헷갈리는 단어는 `curated_tags.json`에 id→태그를 직접 추가하면 Gemini보다 우선 적용된다
(예: 사과하다는 "인사"와 구분되도록 깊은 사죄 포즈 태그를 지정).
