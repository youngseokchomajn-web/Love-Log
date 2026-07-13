import pandas as pd
import requests
import json
import time

csv_path = "words.csv"
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"⚠️ 오류: {csv_path} 파일을 찾을 수 없습니다.")
    exit(1)

print(f"🚀 총 {len(df)}개의 단어에 대해 Llama 3.1을 사용하여 시각적 프롬프트 영작을 시작합니다...")

# 사용자 확정 시스템 프롬프트
SYSTEM_PROMPT = """추상적인 단어나 장소를 입력받으면, 그 단어를 가장 직관적으로 '구별'할 수 있는 핵심 특징을 포함한 구체적 사물/건물의 영어 명사구(2~5단어)로 출력하라.

[필수 규칙]
1. 단순히 'building'이라고 뭉뚱그리지 말고, 그 장소만의 독특한 외형적 특징이나 대표 사물을 반드시 포함할 것. (예: 회사 -> modern tall glass skyscraper, 학교 -> classic school building with a clock tower, 시간 -> vintage pocket watch)
2. 주변 배경 묘사나 사람(person) 묘사는 배제하고, 오직 메인 사물/건물의 외형 특징에만 집중할 것.
3. 절대 문장으로 쓰지 말고, 오직 명사구(Noun phrase)만 딱 뱉을 것."""

# 로컬 Ollama API 주소
OLLAMA_API_URL = "http://localhost:11434/api/chat"

for index, row in df.iterrows():
    korean_word = row['korean']
    english_word = row.get('english', '')
    
    print(f"[{index+1}/{len(df)}] '{korean_word}({english_word})' 영작 중...", end=" ")
    
    user_message = f"단어: {korean_word} ({english_word})"
    
    payload = {
        "model": "llama3.1",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "stream": False,
        "options": {
            "temperature": 0.3 # 약간 일관성 있게
        }
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        generated_prompt = result["message"]["content"].strip()
        
        # 불필요한 따옴표 제거나 줄바꿈 처리
        generated_prompt = generated_prompt.replace('"', '').replace('\n', ' ')
        
        df.at[index, 'visual_prompt'] = generated_prompt
        print(f"-> {generated_prompt}")
        
    except Exception as e:
        print(f"-> ❌ 실패: {e}")
        
# 덮어쓰기 저장
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n✅ 프롬프트 자동 팽창 완료! 결과가 {csv_path} 에 저장되었습니다.")
