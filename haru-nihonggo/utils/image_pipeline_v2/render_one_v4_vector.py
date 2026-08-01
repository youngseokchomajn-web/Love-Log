#!/usr/bin/env python3
"""
표준 SDXL 파라미터(steps=28, guidance=7.5) 1개 테스트 렌더링
"""

import os
import torch
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler

BASE_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"
OUTPUT_DIR = os.path.join(BASE_DIR, "assets/images/words_v4_gemini")
os.makedirs(OUTPUT_DIR, exist_ok=True)

prompt_text = (
    "masterpiece, best quality, 1boy, 1girl, studio ghibli style, clean line art, warm pastel colors, "
    "flat 2d vector illustration for mobile app, young Ghibli character looking up in thought, "
    "small subtle floating question mark, plain simple background, no text, no buildings"
)

negative_prompt = (
    "lowres, bad quality, text, watermark, signature, buildings, scenery, house, town, city, street, "
    "complex background, photorealistic, 3d render, detailed background, trees, forest, sky, mountains"
)

save_path = os.path.join(OUTPUT_DIR, "n5_何_무엇_v4.jpg")

print("🎨 표준 SDXL 파라미터로 1개 테스트 이미지 렌더링 중...")

model_id = "cagliostrolab/animagine-xl-3.1"
pipe = StableDiffusionXLPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    use_safetensors=True
)
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

if torch.backends.mps.is_available():
    pipe.to("mps")

image = pipe(
    prompt=prompt_text,
    negative_prompt=negative_prompt,
    num_inference_steps=28,
    guidance_scale=7.5,
    width=512,
    height=512
).images[0]

image.save(save_path, quality=95)
print(f"✅ 테스트 렌더링 완료: {save_path}")
