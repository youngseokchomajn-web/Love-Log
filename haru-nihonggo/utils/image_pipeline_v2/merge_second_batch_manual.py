import json
import os

def merge_batch():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    # 49 curated tags engineered directly by Antigravity
    new_tags = {
        "n1_0160": "dried plum, umeboshi, red plum, single object, white bowl, pickle, sour food, close-up, no humans",
        "n1_0169": "calligraphy practice, master handwriting, paper model, brush painting, table, classroom, guidance, detailed, no humans",
        "n1_0170": "store sale corner, red discount sign, shelves stacked with goods, department store entrance, daytime, no humans",
        "n1_0174": "1boy, vintage clothing, holding suitcase, standing on ship deck, look back, ocean background, statue of liberty silhouette in distance",
        "n1_0175": "bar counter, liquor bottles, dim lighting, bar counter stool, warm lighting, cozy atmosphere, empty bar, indoor, no humans",
        "n1_0177": "kitchen timer, dial timer, ticking, numbers, 30 minutes, kitchen counter, single object, macro shot, no humans",
        "n1_0178": "desktop computer tower, pc case, metallic cover, power button, cables, floor, single object, simple background, no humans",
        "n1_0192": "various side dishes, small bowls, pickled vegetables, salad, cooked beans, dining table, colorful food, indoor, no humans",
        "n1_0197": "1boy, university student, carrying backpack, graduation cap silhouette, campus yard, cherry blossom petals, looking forward, daytime",
        "n1_0201": "abandoned mine entrance, wooden beam support, dark tunnel, pickaxe on ground, gold ore veins sparkling, mountain side, outdoors, no humans",
        "n1_0206": "red pen mark, correction symbol, notebook page, handwritten text, pencil on table, desk, close-up, no humans",
        "n1_0209": "movie theater audience, crowd, looking forward, smiling faces, dimmed screen light reflection, cinema hall, back view of seats",
        "n1_0219": "rainwater puddle, reflection of sky and clouds, wet asphalt road, green leaves floating, splash ripples, street side, no humans",
        "n1_0226": "antique golden crown, jeweled relic, display stand, velvet cushion, glass showcase, museum exhibit, glowing light, no humans",
        "n1_0228": "traditional japanese castle, tower house, small old town at foot of mountain, street with lanterns, historical shops, daytime, scenic landscape",
        "n1_0233": "metal pipe joint, dripping water drop, rusted pipe connector, wet pipe surface, industrial setting, close-up, no humans",
        "n1_0235": "pregnant woman, doctor, clinic room, ultrasound monitor showing baby silhouette, medical bed, white coat, warm lighting, gentle atmosphere",
        "n1_0244": "businessman bowing to senior, showing document, office desk, positive working relationship, smiling colleague, office interior",
        "n1_0256": "hardcover book, book cover art, library shelf, cozy study room, desk lamp glowing, open page, antique wooden desk, no humans",
        "n1_0263": "old copper water pipe, dripping water, damp basement wall, plumbing, rust textures, macro shot, no humans",
        "n1_0275": "young man wearing apron, elder father passing wooden store sign, standing at storefront, traditional shop entrance, smiling together",
        "n1_0281": "swallowtail butterfly, sitting on yellow flower, blooming garden, morning dew, detailed wings, close-up, sunny day, no humans",
        "n1_0297": "pheasant feathers, hunting trophy, wooden table, vintage hunting gear, cabin interior, log house, warm fireplace light, no humans",
        "n1_0298": "1girl, wind blowing hair, looking at sky, standing on cliff, cinematic shot, spotlight shining on her, epic fantasy background",
        "n1_0299": "clean modern bathroom, white bathtub, water steam, neat towels, window with sunlight, fresh plants, peaceful indoor, no humans",
        "n1_0300": "bright community center facility, barrier-free entrance, wheelchair ramp, glass automatic doors, garden path, sunny morning, no humans",
        "n1_0307": "ceramic pot, clay vase, antique pattern, museum display case, soft spotlight, archaeological relic, no humans",
        "n1_0309": "exquisite porcelain cups, blue pattern porcelain plates, wooden store shelf, shop interior, soft warm lighting, no humans",
        "n1_0314": "backstage green room, sofa, dressing table, mirror with light bulbs, quiet atmosphere, empty dressing room, indoor, no humans",
        "n1_0318": "1boy, young child, building wooden blocks, puzzle pieces on floor, bright playroom, smiling, playing alone",
        "n1_0325": "microscopic view of biological cells, glowing membrane, cell nucleus, science illustration, abstract neon blue and purple color, no humans",
        "n1_0328": "confident businessman, suit, luxury office interior, city skyline view from large window, arms crossed, smiling",
        "n1_0329": "gray steel battleship, destroyer warship, navy harbor, anchors down, ocean harbor, sunset sky, calm sea, no humans",
        "n1_0334": "glass ashtray, single cigarette butt, small wisp of smoke rising, wooden table, cafe terrace background, no humans",
        "n1_0337": "traditional japanese playing cards, karuta cards spread on tatami floor, beautiful poetry cards, sliding paper door background, no humans",
        "n1_0341": "historical official, simple robe, writing with ink brush, stacks of papers, low wooden desk, modest office room, focused expression",
        "n1_0344": "metal hex bolt, nut screwed on thread, steel screw, workbench, macro shot, industrial details, no humans",
        "n1_0349": "group photo of smiling students, high school club members, wearing matching club uniforms, holding banner, daytime",
        "n1_0351": "elderly village chief, holding staff, traditional tribal leader robe, sitting around council fireplace, ancient hall",
        "n1_0353": "japanese rice crackers, araki mix, colorful snack mix, wooden plate, green tea cup, tatami setting, no humans",
        "n1_0354": "bustling local street market, grocery shopping, ordinary family, friendly vendor, fresh vegetables stall, warm afternoon sun",
        "n1_0356": "child prodigy playing grand piano, spotlight shining, grand concert hall, floating musical notes visual effect, passionate expression",
        "n1_0363": "heavy lead metal ingot, gray metallic sheen, industrial refinery backdrop, solid lead bar, close-up, no humans",
        "n1_0382": "large yellow tower crane, lifting cargo box, construction site, harbor shipping yard, cargo ships, sunny sky, no humans",
        "n1_0384": "luxurious red carpet on wooden floor, clean living room interior, coffee table, soft lighting, cozy home, no humans",
        "n1_0401": "reading original english book, novel text pages close-up, study desk, holding mug cup, warm ambient light",
        "n1_0410": "wooden ladder leaning against brick wall, roof edge, garden scene, daytime, outdoors, house side, no humans",
        "n1_0413": "close-up texture of woven textile, detailed thread weave pattern, colorful traditional cotton cloth, macro shot, no humans",
        "n1_0415": "dalmatian dog pattern close-up, black spots on white fur, animal print textures, detailed, macro shot, no humans"
    }
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache.update(new_tags)
    
    # Atomic write
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    print(f"Successfully merged second batch of 49 manual tags. New cache size: {len(cache)}")

if __name__ == "__main__":
    merge_batch()
