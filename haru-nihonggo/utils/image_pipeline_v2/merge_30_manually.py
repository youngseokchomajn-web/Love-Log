import json
import os

def merge_30():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    # 30 curated tags engineered directly by Antigravity
    new_tags = {
        "n1_0017": "shaking hands, two businessmen, suits, national flag, press conference, podium, indoor, photo op",
        "n1_0020": "1boy, wearing helmet, construction blueprint, holding clipboard, safety vest, discussing site, outdoor",
        "n1_0021": "raw beef steak, detailed meat texture, marble pattern, kitchen counter, rosemary herb, garlic, cooking ingredients, no humans",
        "n1_0027": "group of students, high school uniform, sitting around desk, study group, classroom, talking together, friendly atmosphere",
        "n1_0029": "holding steam iron, fabric steamer, hot steam rising, ironing board, white shirt, laundry room, detailed, no humans",
        "n1_0033": "storefront, beautiful bakery shop, flower baskets, open sign, glass door, modern architecture, street side, daytime, no humans",
        "n1_0035": "politician speaking, podium, microphone, passionate gesture, parliament hall, audience listening, political speech, warm lights",
        "n1_0039": "1boy, professional cameraman, holding video camera, shoulder rig, filming scene, studio lights, media broadcasting, focused expression",
        "n1_0046": "group of ministers, formal photo, staircase pose, government officials, black suits, official ceremony, indoor group photo",
        "n1_0048": "bath sponge, bubbles, soap lather, warm bath tub, steam water, bathroom interior, self care, cozy indoor, no humans",
        "n1_0052": "lavish feast, roasted chicken, pasta, wine glasses, salad, dining table, warm party atmosphere, glowing candles, no humans",
        "n1_0053": "glass tea pot, tea infuser, steeping red tea, porcelain teacup, steam rising, wooden table, cozy cafe, no humans",
        "n1_0057": "crescent moon, night sky, starry background, dark blue clouds, glowing moon, serene nature night, no humans",
        "n1_0062": "doctor hands, feeling wrist pulse, patient arm, stethoscope on table, clinical setting, caring gesture, close-up",
        "n1_0071": "antique wooden chest of drawers, closet drawer open, neatly folded clothes, bedroom corner, cozy morning sun, no humans",
        "n1_0076": "cartoon bacteria cells, cute green micro-organisms, viral spheres, microscope visual effect, science education, no humans",
        "n1_0077": "wrist watch, metallic case, dial, gear, close-up, scratch, small crack, detailed, no humans",
        "n1_0079": "large glowing full moon, night sky, silhouettes of pine trees, clouds drifting, golden moonlight reflection, serene, no humans",
        "n1_0093": "red ink stamp pad, hanko seal, pressing on paper document, contract signature line, wooden desk, close-up, no humans",
        "n1_0096": "bank robbery scene, cinematic drama, tied up hostage, dark vault background, shadow figure, tension mood",
        "n1_0104": "single flower vase, red rose, exact center of round wooden table, clean minimalist room background, bright room, no humans",
        "n1_0105": "hand wiping table with white dishcloth, water streaks on wood surface, kitchen counter, cleaning process, close-up",
        "n1_0110": "luxurious red carpet on wooden floor, clean living room interior, coffee table, soft lighting, cozy home, no humans",
        "n1_0121": "hot rice porridge bowl, steam rising, ceramic spoon, pickled plum on top, wooden tray, traditional table, no humans",
        "n1_0126": "golden ears of rice close-up, ripe rice stalks, autumn paddy field, sunset glow background, peaceful countryside, no humans",
        "n1_0127": "sumo grand champion, yokozuna rope, posing on ring, dohyo stadium, muscular figure, traditional costume, strong expression",
        "n1_0140": "studying kanji notebook, hand holding pencil, study desk, morning sunlight, writing japanese characters, close-up",
        "n1_0148": "1girl, wearing kimono, standing near traditional paper sliding door, japanese room, smiling, polite gesture",
        "n1_0153": "vintage military uniform, detailed jacket brass buttons, standing pose, sepia photo frame, historical shelf background, no humans",
        "n1_0155": "japanese food, breakfast, soup bowl, rice bowl, fish, chopsticks, food tray, table setting, indoor, no humans"
    }
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache.update(new_tags)
    
    # Atomic write
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    print(f"Successfully merged 30 curated high-quality tags into clean cache. Current cache size: {len(cache)}")

if __name__ == "__main__":
    merge_30()
