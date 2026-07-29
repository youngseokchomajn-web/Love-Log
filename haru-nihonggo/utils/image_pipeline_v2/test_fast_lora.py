import os
import json
import time
import torch
import gc
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler

def test_generation(steps, lora_name, cfg_scale, output_name):
    print(f"\n🚀 Testing: {lora_name} | Steps: {steps} | CFG: {cfg_scale}")
    
    # Setup pipe
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "cagliostrolab/animagine-xl-3.1",
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    
    # Load LoRA
    print(f"Loading {lora_name}...")
    pipe.load_lora_weights("ByteDance/Hyper-SD", weight_name=lora_name)
    pipe.fuse_lora()
    pipe = pipe.to("mps")
    
    # Test Word: 바람개비 (n1_0002)
    # Target tag: pinwheel, colorful, spinning, single object, centered, simple background, outdoors, blue sky, no humans
    prompt = "pinwheel, colorful, spinning, single object, centered, simple background, outdoors, blue sky, no humans, masterpiece, best quality, very aesthetic, absurdres, solo object, clear focus, studio lighting, highly detailed, (studio ghibli:1.3), (traditional media, watercolor:1.2)"
    negative_prompt = "lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, signature, multiple objects, crowd, (modern anime style, flat shading:1.2)"
    
    start_time = time.time()
    with torch.inference_mode():
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=cfg_scale,
            width=768,
            height=768
        ).images[0]
    
    elapsed = time.time() - start_time
    output_path = f"assets/images/words_v2/{output_name}.jpg"
    image.convert('RGB').save(output_path, format='JPEG', quality=90)
    print(f"✅ Saved to {output_path} (Took: {elapsed:.2f} seconds)")
    
    # Cleanup memory
    del pipe
    del image
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

def main():
    os.makedirs("assets/images/words_v2", exist_ok=True)
    
    # Test 4-Steps Hyper-SD
    try:
        test_generation(
            steps=4,
            lora_name="Hyper-SDXL-4steps-lora.safetensors",
            cfg_scale=1.2,
            output_name="test_hyper_sd_4steps"
        )
    except Exception as e:
        print(f"Error testing 4steps: {e}")
        
    # Test 2-Steps Hyper-SD
    try:
        test_generation(
            steps=2,
            lora_name="Hyper-SDXL-2steps-lora.safetensors",
            cfg_scale=1.0,
            output_name="test_hyper_sd_2steps"
        )
    except Exception as e:
        print(f"Error testing 2steps: {e}")

if __name__ == "__main__":
    main()
