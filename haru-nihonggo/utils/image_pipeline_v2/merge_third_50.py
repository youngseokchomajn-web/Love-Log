import json
import os

def merge_tags():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    # 27 curated tags designed directly by Antigravity for 3rd batch
    new_tags = {
        "n1_0846": "hand saw, cutting wood log, wood sawdust, workshop table, carpentry tools, no humans",
        "n1_0856": "shiny copper metal plates, raw copper ore, warm orange-brown sheen, refinery setup, macro shot, no humans",
        "n1_0858": "classroom school bell chime, wooden wall, hanging chime speaker, school corridor background, daytime, no humans",
        "n1_0859": "buying snacks, cute free keychain bonus toy inside, package box on wooden table, smiling mascot doll, no humans",
        "n1_0865": "railway tracks, cherry blossom trees blooming along the line, train station in distance, green grass fields, outdoors, scenic",
        "n1_0866": "1boy, professional office worker, name tag stating Chief, reviewing documents, smiling at desk, office interior, daytime",
        "n1_0869": "signing delivery receipt on clipboard, cardboard box, mail courier hands, house door entrance, warm lighting",
        "n1_0874": "first train of morning, quiet station platform, early dawn sky, blue hour glow, train lights approaching, empty station, scenic",
        "n1_0883": "folded white cloth napkin, elegant plate, fork and knife, dining table setting, restaurant background, no humans",
        "n1_0897": "traditional Japanese living room, tatami mats, low kotatsu table, tea cups, shoji doors sliding, cozy warm indoor, no humans",
        "n1_0899": "crowd of diverse people, smiling faces, citizens standing together under sunny sky, community harmony, outdoor",
        "n1_0900": "iron rod, heavy metal crowbar, construction ground, digging hole in dirt soil, industrial site, no humans",
        "n1_0903": "award gift box with ribbon, gold star emblem, teacher giving reward to child, classroom setting, joyful mood",
        "n1_0910": "ruler markings, measuring scale close-up, thermometer scale, numbers, graduation lines, macro shot, no humans",
        "n1_0911": "metallic coil spring, spring mattress inside layer, flexible coils, close-up, steel material, no humans",
        "n1_0914": "water-filled paddy field, green rice seedlings planted in rows, reflection of sky in water, mountains in background, rural countryside",
        "n1_0926": "lush green trees and shrubs, public park forest, walking path, sunlight filtering through leaves, peaceful nature scenery, no humans",
        "n1_0928": "wooden coat hanger, empty hanger hanging on clothes rack, wardrobe interior, soft lighting, simple background, no humans",
        "n1_0932": "mannequin torso, display dress form, tailor's workshop, measuring tape wrapped around waist, fabric studio, no humans",
        "n1_0945": "pencil sketch of plaster bust on easel, charcoal drawings on wall, art studio workshop, pencils, drawing paper, no humans",
        "n1_0946": "section of railway track under construction, warning road cone, barricade sign, asphalt road section, outdoors, no humans",
        "n1_0961": "x-ray film showing hand bone skeleton, illuminated light board in hospital room, medical clinic, clinical display, no humans",
        "n1_0965": "untranslated original book pages, old text script close-up, study desk, reading glasses on book, cozy library setting, no humans",
        "n1_0971": "close-up of bird's yellow beak, picking seeds from ground, detailed feathers, garden setting, macro shot, no humans",
        "n1_0982": "elderly grandfather, smiling face, walking stick in hand, strolling in park, morning sun, peaceful retirement",
        "n1_0988": "contact lens case, liquid drops, transparent contact lens on fingertip, close-up, bathroom setting",
        "n1_0989": "decorating Christmas tree, hanging colorful ornaments, shiny bells, sparkling lights, cozy living room, warm holiday vibe, no humans"
    }
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache.update(new_tags)
    
    # Atomic write
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    print(f"Successfully merged 3rd batch of 27 high-quality tags. New cache size: {len(cache)}")

if __name__ == "__main__":
    merge_tags()
