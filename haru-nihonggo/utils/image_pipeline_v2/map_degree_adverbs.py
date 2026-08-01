import json
import os

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

DEGREE_ADVERB_MAPPING = {
    # === 최상급 (100% - MAX Red Gauge + Sparkle ✨) ===
    "n5_0030": { # たいへん (매우, 대단히)
        "stage": "100%",
        "prompt": "Ghibli style illustration of scale contrast, tiny human silhouette standing next to a colossal epic mountain footprint, glowing vertical bar gauge on right side filled to MAX red with subtle sparkles, dramatic contrast, warm lighting, clear scale comparison"
    },
    "n5_0233": { # とても (매우, 아주)
        "stage": "100%",
        "prompt": "Ghibli style illustration of scale contrast, small tiny candle flame on left compared to a massive roaring sun-like bonfire on right, vertical bar gauge filled to MAX red with glowing sparkles, dramatic scale contrast, warm aesthetic"
    },
    "n4_603": { # 非常に (매우)
        "stage": "100%",
        "prompt": "Ghibli style illustration of intensity contrast, a small quiet lightbulb next to a blazing blinding lighthouse beam, vertical bar gauge filled to MAX red with subtle sparkles, intense comparison, warm color palette"
    },
    "n3_0991": { # 大変 (매우, 대단히)
        "stage": "100%",
        "prompt": "Ghibli style scale comparison, tiny person standing in front of a gigantic epic stone monument, vertical bar gauge on right filled to MAX red with glowing sparkles, dramatic scale contrast, warm lighting"
    },
    "n3_1525": { # 大いに (대단히, 크게)
        "stage": "100%",
        "prompt": "Ghibli style comparison, small tiny stream of water next to a massive roaring waterfall cascade, vertical bar gauge on right filled to MAX red with subtle sparkles, grand scale contrast, warm aesthetic"
    },
    "n2_0155": { # 大層 (매우, 대단히)
        "stage": "100%",
        "prompt": "Ghibli style comparison, a small handheld gift box next to a colossal room-sized wrapped gift box, vertical bar gauge filled to MAX red with sparkles, dramatic scale contrast, warm lighting"
    },
    "n1_0776": { # 甚だ (매우, 심히)
        "stage": "100%",
        "prompt": "Ghibli style intensity comparison, a small calm ripple on water next to a giant crashing ocean wave, vertical bar gauge on right filled to MAX red with sparkles, dramatic scale contrast, warm lighting"
    },
    "n1_1196": { # 極めて (극히, 매우)
        "stage": "100%",
        "prompt": "Ghibli style comparison, a single tiny pebble next to a colossal giant monolith, vertical bar gauge filled to MAX red with subtle sparkles, extreme scale contrast, warm aesthetic"
    },

    # === 상급 (75% - High Orange Gauge) ===
    "n4_406": { # ずいぶん (대단히, 상당히)
        "stage": "75%",
        "prompt": "Ghibli style scale comparison, a short young plant next to a tall mature tree, vertical bar gauge filled to 75% orange, clear side by side growth contrast, warm sunlight, clean composition"
    },
    "n4_539": { # 中々 (꽤)
        "stage": "75%",
        "prompt": "Ghibli style scale comparison, a small stack of 3 books next to a tall stack of 10 books, vertical bar gauge on right filled to 75% orange, clear comparison, warm lighting"
    },
    "n3_0421": { # 随分 (상당히, 꽤)
        "stage": "75%",
        "prompt": "Ghibli style comparison, a small village house next to a large clocktower building, vertical bar gauge on right filled to 75% orange, clear scale contrast, warm aesthetic"
    },
    "n3_1136": { # なかなか (꽤, 좀처럼)
        "stage": "75%",
        "prompt": "Ghibli style comparison, a simple 4-piece puzzle next to a complex 100-piece puzzle, vertical bar gauge filled to 75% orange, clear level comparison, warm lighting"
    },
    "n3_1218": { # かなり (꽤, 상당히)
        "stage": "75%",
        "prompt": "Ghibli style comparison, a small water glass filled 75% high, vertical bar gauge on right filled to 75% orange, clear comparison, warm ambient light"
    },
    "n2_0550": { # 大分 (상당히, 꽤)
        "stage": "75%",
        "prompt": "Ghibli style comparison, a small sapling next to a medium sturdy oak tree, vertical bar gauge filled to 75% orange, side by side contrast, warm aesthetic"
    },
    "n1_3178": { # 可成 (かなり) (꽤, 상당히)
        "stage": "75%",
        "prompt": "Ghibli style scale comparison, a short wooden ladder next to a tall extension ladder, vertical bar gauge filled to 75% orange, clear side by side comparison, warm lighting"
    },

    # === 중간 (50% - Mid Yellow Gauge) ===
    "n2_1172": { # 割と (비교적, 꽤)
        "stage": "50%",
        "prompt": "Ghibli style comparison, two equal sized cups filled to 50% half level, vertical bar gauge in middle filled to 50% yellow, balanced comparison, warm lighting"
    },

    # === 하급 (25% - Low Blue Gauge) ===
    "n5_0246": { # ちょっと (조금, 잠시)
        "stage": "25%",
        "prompt": "Ghibli style scale comparison, a full measuring cup next to a cup with just 25% water at bottom, vertical bar gauge filled low to 25% cool blue, subtle minimal contrast, warm aesthetic, no sparkles"
    },
    "n5_0356": { # 少し (조금)
        "stage": "25%",
        "prompt": "Ghibli style scale comparison, a full bowl of rice next to a bowl with just a small 25% portion, vertical bar gauge filled low to 25% cool blue, subtle contrast, warm lighting, no sparkles"
    },
    "n4_650": { # やや (약간, 조금)
        "stage": "25%",
        "prompt": "Ghibli style comparison, two nearly identical apples where one is just slightly 25% larger, vertical bar gauge filled low to 25% cool blue, subtle difference, warm aesthetic"
    },

    # === 최하급 (10% - Minimal Grey Gauge) ===
    "n3_0739": { # 極 (극히, 아주/살짝)
        "stage": "10%",
        "prompt": "Ghibli style comparison, two nearly identical wooden blocks with a barely visible 10% size difference, vertical bar gauge at bottom 10% muted grey, minimal subtle difference, warm lighting"
    }
}

def apply_mapping():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    applied_count = 0
    for w_id, data in DEGREE_ADVERB_MAPPING.items():
        tags_cache[w_id] = data["prompt"]
        applied_count += 1
        
    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] 정도부사 시각 연출 규칙에 따라 {applied_count}개 단어 프롬프트 업그레이드 완료!")
    
    # Save list of target IDs for regeneration
    regen_list = list(DEGREE_ADVERB_MAPPING.keys())
    print(f"Target IDs for regeneration: {','.join(regen_list)}")
    
    with open(f"{ROOT_DIR}/utils/image_pipeline_v2/degree_adverb_regen_ids.txt", "w") as f:
        f.write(','.join(regen_list))

if __name__ == "__main__":
    apply_mapping()
