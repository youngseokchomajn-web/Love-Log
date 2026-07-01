import os
import time
import pandas as pd
from google import genai
from dotenv import load_dotenv

# 1. .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ 오류: .env 파일에 GEMINI_API_KEY가 설정되어 있지 않습니다!")
    print("Google AI Studio에서 키를 발급받아 .env 파일에 넣어주세요.")
    exit(1)

# 최신 google-genai 클라이언트 초기화
client = genai.Client(api_key=api_key)

# 2. 단어장 CSV 로드
csv_path = "words.csv"
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"⚠️ 오류: {csv_path} 파일을 찾을 수 없습니다.")
    exit(1)

output_dir = "images_api_ghibli"
os.makedirs(output_dir, exist_ok=True)

print(f"🚀 총 {len(df)}개의 단어 이미지 자동 생성을 시작합니다... (API 방식)")

# 3. 자동 생성 루프
for index, row in df.iterrows():
    korean_word = row['korean']
    visual_prompt = row['visual_prompt']
    
    # 프롬프트 구성 (지브리 스타일 수채화)
    prompt = f"Studio Ghibli style, beautiful watercolor anime background, {visual_prompt}, soft lighting, nostalgic, masterpiece, best quality, highly detailed, no people"
    
    print(f"[{index+1}/{len(df)}] '{korean_word}' 이미지 생성 중...")
    
    image_path = os.path.join(output_dir, f"{korean_word}.png")
    
    # 이미 파일이 있으면 건너뛰기
    if os.path.exists(image_path):
        print(f"  👉 이미지가 이미 존재하여 건너뜁니다: {image_path}")
        continue
        
    try:
        # Gemini (Imagen 4) 최신 SDK 이미지 생성 API 호출
        result = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=dict(
                number_of_images=1,
                aspect_ratio="1:1",
                output_mime_type="image/png"
            )
        )
        
        # 이미지 파일로 저장
        if result.generated_images:
            image_bytes = result.generated_images[0].image.image_bytes
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            print(f"  ✅ 저장 완료: {image_path}")
        else:
            print(f"  ❌ 이미지 생성 실패: 반환된 이미지가 없습니다.")
            
    except Exception as e:
        print(f"  ⚠️ API 오류 발생: {e}")
        print(f"  1분당 요청 한도(Rate Limit) 초과일 수 있으므로 더 길게 대기합니다...")
        time.sleep(30)
        
    # 무료 티어 분당 요청 한도(Rate Limit) 방지를 위해 15초 대기
    if index < len(df) - 1:
        print("  ⏳ 무료 API 한도 초과 방지를 위해 15초 대기 중...\n")
        time.sleep(15)

print("\n🎉 모든 이미지 생성이 성공적으로 완료되었습니다!")
