import os
import pandas as pd
import torch
from diffusers import StableDiffusionPipeline

def main():
    # 1. Load the words dataset
    csv_path = 'words.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    df = pd.read_csv(csv_path)

    # 2. Setup the Stable Diffusion Pipeline for Apple Silicon (MPS)
    print("Loading Stable Diffusion model (this might take a while on the first run to download)...")
    # 스튜디오 지브리 풍의 수채화/애니메이션 배경에 특화된 모델로 교체합니다.
    model_id = "dreamlike-art/dreamlike-anime-1.0"
    
    # M4 칩(Apple Silicon)의 GPU 가속을 위해 'mps' 디바이스를 사용합니다.
    # MPS에서 float16 사용 시 NaN 에러로 인해 검은 화면이 나오는 이슈를 방지하기 위해 float32를 사용합니다.
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, 
        torch_dtype=torch.float32,
        safety_checker=None,
        requires_safety_checker=False
    )
    pipe = pipe.to("mps")
    
    # 메모리 최적화를 위해 attention slicing 활성화
    pipe.enable_attention_slicing()

    # 3. Create output directory
    output_dir = "images_ghibli"
    os.makedirs(output_dir, exist_ok=True)

    # 4. Generate Images
    print("Starting image generation...")
    for index, row in df.iterrows():
        visual_prompt = row['visual_prompt']
        korean_word = row['korean']
        english_word = row['english']
        
        # 프롬프트: 스튜디오 지브리 스타일, 수채화, 부드러운 조명, 고품질 애니메이션 배경
        prompt = f"Studio Ghibli style, beautiful watercolor anime background, {visual_prompt}, soft lighting, nostalgic, masterpiece, best quality, highly detailed, no people"
        # 네거티브 프롬프트: 사람 등장 방지, 저품질 텍스트 등 배제
        negative_prompt = "person, people, character, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
        
        print(f"[{index+1}/{len(df)}] Generating image for: {korean_word} ({english_word})...")
        
        # 이미지 생성 (추론 스텝 25회)
        image = pipe(
            prompt=prompt, 
            negative_prompt=negative_prompt, 
            num_inference_steps=25, 
            guidance_scale=7.5
        ).images[0]
        
        # 이미지 저장
        image_path = os.path.join(output_dir, f"{korean_word}.png")
        image.save(image_path)
        print(f"Saved: {image_path}")

    print("All images generated successfully!")

if __name__ == "__main__":
    main()
