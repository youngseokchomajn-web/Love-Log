import json
import os

def merge_batch_5():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    # Batch 5 curated tags designed directly by Antigravity
    new_tags = {
        "n1_0165": "eggshell, white egg broken in half, thin translucent membrane, kitchen table, close-up, macro shot, no humans",
        "n1_0416": "bank clerk, consulting table, computer screen, documents, office interior, professional outfit, smiling",
        "n1_0422": "teenage boy looking in mirror, touching face, reflection in bathroom mirror, acne close-up, morning light",
        "n1_0423": "new socks with labels, wooden floor, wrapping paper, cozy bedroom sunlight, colorful patterns, no humans",
        "n1_0432": "sparkling diamond gemstone, crystalline structure diagram background, science book, warm study light, macro shot, no humans",
        "n1_0434": "cherry blossom buds, spring tree branch, soft pink petals starting to show, warm sunlight, blurry park background, no humans",
        "n1_0440": "1girl, gentle smile, polite greeting gesture, business casual attire, modern office lobby, daytime, soft lighting",
        "n1_0441": "grand concert hall, empty rows of red seats, spacious stage, majestic ceiling lights, classic theater interior, no humans",
        "n1_0445": "1boy, wearing glasses, tweed jacket, reading antique book, wooden library shelves filled with books, cozy study desk, warm ambient light",
        "n1_0448": "natural cotton fabric rolls, linen threads, organic materials, tailoring workshop, sunlight from window, no humans",
        "n1_0462": "bowl of hot udon, thick noodles, green onions, fish cake slice, steaming broth, wooden table, chopsticks, lunch setting, no humans",
        "n1_0463": "highway exit offramp, road sign, curving asphalt road, sunny afternoon, green hills side, blue sky, highway scenery, no humans",
        "n1_0465": "script notebook, printed pages with lines, pen on desk, laptop keyboard, cozy study room, warm light, creative workspace, no humans",
        "n1_0468": "middle-aged woman lecturing, podium, microphone, presenting slides, business attire, smiling, confident stance, conference hall",
        "n1_0469": "night sky falling, deep blue horizon, silhouettes of trees, cozy streetlights turning on, twilight transition, peaceful evening, no humans",
        "n1_0475": "colorful textbooks, open pages with diagrams, pencils, study desk, bright classroom background, learning materials, no humans",
        "n1_0477": "open fashion magazine, colorful poster insert, bonus items on wooden table, lifestyle scene, warm light, no humans",
        "n1_0479": "memorial altar frame, white lilies, candle burning, peaceful and solemn room, memory photo backdrop, respectful mood, no humans",
        "n1_0482": "medical chart clipboard, doctor stethoscope, wooden desk, stethoscope, clinical office setting, health records, no humans",
        "n1_0487": "mountainside village, small houses nested on green slope, mist rising, pine trees, serene nature landscape, daytime",
        "n1_0491": "science experiment, chemical beaker, blue litmus paper dipping, color reaction, test tube racks, classroom lab, no humans",
        "n1_0493": "comforting hug, family members crying, holding hands, old portrait on wall, emotional support, warm home setting",
        "n1_0495": "elderly grandmother smiling, gentle age lines on face, warm lighting, kind eyes, silver hair, cozy cardigan, serene expression",
        "n1_0499": "framed oil painting on museum wall, vibrant landscape artwork, wooden floor, gallery lighting, art exhibition, no humans",
        "n1_0506": "bronze statue in public park, pedestal, green trees background, path walk, sunny day, historic monument, no humans",
        "n1_0510": "rolling green hills, pasture fields, wooden fences, grazing sheep in distance, clear blue sky with clouds, countryside scenery, no humans",
        "n1_0515": "gardening tools, colorful flowerbed, blooming tulips and pansies, garden soil, watering can, sunny morning, no humans",
        "n1_0518": "sheet music on piano stand, piano keys, warm desk lamp glowing, music notes close-up, cozy room, no humans",
        "n1_0519": "sleeping baby, swaddled in soft blanket, wooden crib, peaceful nursery, warm morning sun, gentle smile",
        "n1_0527": "cool mountain plateau, green grasslands, distant peaks, clear blue sky, refreshing breeze, summer scenic resort, no humans",
        "n1_0531": "crowded sports stadium, audience cheering, colorful flags waving, bright stadium lights, soccer field background, joyful faces",
        "n1_0540": "legal documents in folder, ink pen, metal cabinet storage, desk organizer, official papers close-up, no humans",
        "n1_0542": "medical lab test vial, yellow liquid sample, gloved hand, test tubes rack, clinic equipment, clinical analysis, no humans",
        "n1_0553": "sparrow perched on treetop, thin branch, green leaves budding, clear blue sky background, sunny morning, macro shot, no humans",
        "n1_0558": "cabinet secretary office, formal executive desk, national flag behind, leather chair, office bookcase, political workspace, no humans",
        "n1_0564": "shinjuku district street sign, high rise buildings background, bustling city crossing, traffic lights, Tokyo cityscape, daytime, no humans",
        "n1_0567": "1girl, dancing geisha, traditional kimono, holding fan, tatami room, sliding screen doors, geisha performance, elegant posture",
        "n1_0573": "group of mischievous boys, street corner, jackets, cool postures, neighborhood street, sunset background, tense atmosphere",
        "n1_0574": "boiling water pouring from kettle into cup noodles, steam rising, chopsticks resting on lid, kitchen counter, close-up, no humans",
        "n1_0576": "laundry hanging on bamboo pole, white sheets blowing in wind, sunny backyard garden, blue sky, domestic scene, no humans",
        "n1_0580": "tall golden reeds, riverbank scenery, flowing water reflection, autumn evening sunset sky, peaceful landscape, no humans",
        "n1_0581": "wooden observation deck, viewing binoculars, scenic mountain range vista, valley below, sun rays breaking clouds, no humans",
        "n1_0587": "original latin manuscript text close-up, magnifying glass, scholar desk, old books stacked, historic study room, no humans",
        "n1_0597": "small wooden Shinto shrine building, rustic forest setting, stone steps, torii gate in distance, tranquil morning sun, no humans",
        "n1_0598": "dramatic lightning bolt strike, dark stormy purple clouds, thunderstorm over silhouette mountains, evening sky, no humans",
        "n1_0603": "aerial view of a small island, crystal clear blue sea, territorial map border line effect, sunny day, scenic landscape, no humans",
        "n1_0606": "whirlpool swirl on river surface, rushing water current, autumn leaves floating, riverbank rocks, close-up, no humans",
        "n1_0613": "traditional wholesale store interior, wooden crates stacked, sacks of grain, busy warehouse, seller writing ledger, no humans",
        "n1_0614": "antique curios store, dusty brass telescope, vintage clock, old wooden chest, shelf items, warm dim lighting, no humans",
        "n1_0617": "aesthetic pendant light hanging, warm glowing filament bulb, cozy cafe interior background, modern lighting fixture, no humans"
    }
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache.update(new_tags)
    
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    print(f"Successfully merged 5th batch of 50 manual tags. New cache size: {len(cache)}")

if __name__ == "__main__":
    merge_batch_5()
