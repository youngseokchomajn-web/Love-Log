import json
import os

def merge_batch_7():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    # Batch 7 curated tags designed directly by Antigravity
    new_tags = {
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
        "n1_0911": "custom metallic coil spring, spring mattress inside layer, flexible coils, close-up, steel material, no humans",
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
        "n1_0989": "decorating Christmas tree, hanging colorful ornaments, shiny bells, sparkling lights, cozy living room, warm holiday vibe, no humans",
        "n1_1006": "bowl of warm white rice, chopsticks resting on side, small miso soup bowl, dining table, traditional japanese staple food, no humans",
        "n1_1008": "snow avalanche rushing down snowy mountain peak, white snow cloud, winter dramatic nature landscape, cold atmosphere, no humans",
        "n1_1014": "beautiful botanical garden, blooming rose garden path, stone archway, sunny afternoon, vibrant flower beds, peaceful landscape, no humans",
        "n1_1024": "child holding fingers crossed behind back, speaking to mother, playful guilty look, cozy living room setting, warm light",
        "n1_1031": "ancient stone temple ruins, towering greek pillars, ruined columns, green vines climbing, sunset sky backdrop, archeological site, no humans",
        "n1_1037": "polite employee presenting document folder to smiling senior manager, executive office desk, professional business relationship, daytime",
        "n1_1038": "thick leather bound Bible book, gold cross emblem on cover, resting on cozy nightstand, glowing warm bedside lamp, bedroom setting, no humans",
        "n1_1047": "large vintage encyclopedia books, open page with detailed animal illustration, study desk, wooden bookshelves background, no humans",
        "n1_1051": "bustling local community summer festival, colorful paper lanterns, wooden food stalls, happy villagers walking, warm evening glow",
        "n1_1057": "cute close-up of a sleeping baby's belly, soft baby onesie slightly open, tiny belly button, soft warm cotton blanket, no humans",
        "n1_1059": "hand writing name card, english alphabet letters on card, fountain pen, clean desk, detailed macro shot",
        "n1_1060": "applying soothing gel cream on minor arm burn, redness on skin, medicine tube on table, home aid care setting, close-up",
        "n1_1074": "cardboard boxes filled with food, canned goods, bottled water, disaster relief logistics center, stacks of relief goods, indoor, no humans",
        "n1_1076": "vintage home wall intercom phone, hand pressing button, wooden doorway hallway, sunlight from window, no humans",
        "n1_1085": "passengers boarding airplane, boarding gate bridge window view, large passenger plane on tarmac, sunset sky, airport landscape",
        "n1_1090": "monk kneeling in prayer, simple robe, ancient stone altar temple, incense smoke rising, humble gesture, serene ambient light",
        "n1_1091": "paper bus schedule poster on glass panel, bus stop pole, sunset sky background, street light turning on, no humans",
        "n1_1096": "colorful red and orange maple leaves fallen on stone path, autumn garden park, morning dew, detailed textures, soft lighting, no humans",
        "n1_1003": "giant ancient tree trunk close-up, detailed bark texture, green moss growing, sunlight filtering forest, macro shot, no humans",
        "n1_1105": "large computer monitor, showing a colorful landscape graphic art, clean home office desk, mechanical keyboard, warm desk lamp, no humans",
        "n1_1116": "worn out shoe heel close-up, bottom of leather dress shoe, shoe repair workbench, leather craft tools, detailed texture, no humans",
        "n1_1122": "peaceful coastal fishing village, wooden dock, small boats floating on calm water, drying fish nets, sunset seaside landscape, no humans",
        "n1_1130": "antique brass gear wheels interlocking, clockwork mechanism close-up, detailed watchmaker gears, metallic texture, no humans",
        "n1_1132": "young groom in traditional wedding attire, smiling, hand in hand with bride silhouette, formal garden ceremony backdrop",
        "n1_1138": "proud teacher putting gold star sticker on a student's perfect test paper, classroom desk, encouraging classroom atmosphere",
        "n1_1143": "antique family photo album, vintage sepia portraits of ancestors, old leather book cover, wooden table, nostalgia vibe, no humans"
    }
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache.update(new_tags)
    
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    print(f"Successfully merged 7th batch of 50 manual tags. New cache size: {len(cache)}")

if __name__ == "__main__":
    merge_batch_7()
