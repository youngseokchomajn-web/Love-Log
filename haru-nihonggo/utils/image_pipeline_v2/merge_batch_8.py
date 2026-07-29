import json
import os

def merge_batch_8():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    # Batch 8 curated tags designed directly by Antigravity
    new_tags = {
        "n1_0852": "hand saw, cutting wood log, wood sawdust, workshop table, carpentry tools, no humans",
        "n1_0856": "shiny copper metal plates, raw copper ore, warm orange-brown sheen, refinery setup, macro shot, no humans",
        "n1_0858": "classroom school bell chime, wooden wall, hanging chime speaker, school corridor background, daytime, no humans",
        "n1_1103": "giant ancient tree trunk close-up, detailed bark texture, green moss growing, sunlight filtering forest, macro shot, no humans",
        "n1_1123": "large earthenware pot, clay jar, rustic kitchen corner, traditional ceramic storage, detailed, no humans",
        "n1_1127": "young wealthy boy wearing smart vest, combed hair, standing inside elegant mansion parlor, polite smile",
        "n1_1128": "clear blue potion liquid, glowing glass vial, laboratory beaker, science lab, colorful droplets, close-up, no humans",
        "n1_1131": "1girl, sad looking down face, eyes closed, shadow lighting, quiet expression, close-up, cinematic atmosphere",
        "n1_1146": "cozy home garage interior, parked red vintage car, tools hanging on pegboard, warm interior lights, no humans",
        "n1_1150": "dripping water drop from green leaf tip, dewdrop, macro reflection of garden, morning soft light, close-up, no humans",
        "n1_1152": "professional female secretary, holding tablet and stylus, neat glasses, office hallway, scheduling, smiling",
        "n1_1164": "stacks of empty brown cardboard boxes, warehouse shelves, inventory tags, neat storage room, no humans",
        "n1_1168": "pot of boiling broth on stove, hand skimming off foam with mesh skimmer, kitchen cooking process, detailed close-up",
        "n1_1171": "foreign ministers meeting, shaking hands, official flags, mahogany desk, diplomat signing papers, formal room",
        "n1_1178": "rolls of colorful synthetic polyester fabrics, glowing fabric sheen, sewing thread spools, modern textile store, no humans",
        "n1_1184": "smiling city hall clerk, uniform badge, standing at public reception desk, helping client, clean lobby interior",
        "n1_1189": "small sparrow perched on very tip of thin tree branch, winter bare branch, soft morning sky background, close-up, no humans",
        "n1_1199": "vintage Japanese hand-woven thread ball, temari ball, colorful geometric patterns, resting on tatami mat, no humans",
        "n1_1202": "electronic transistor components close-up, copper legs, circuit board soldering, retro radio repair table, macro shot, no humans",
        "n1_1217": "traditional paper uchiwa fan, summer wind chime hanging, wooden porch, blue sky background, hot summer vibe, no humans",
        "n1_1218": "pressing wooden hanko stamp onto paper document, bright red ink pad, signature block, close-up, no humans",
        "n1_1227": "corgi dog tail wagging, cute fluffy dog butt, running on green grass field, back view, warm sunny park",
        "n1_1233": "flash of lightning striking night sky, rolling dark clouds, thunderstorm, silhouette mountains in distance, no humans",
        "n1_1234": "giant granite rock boulder on mountain peak, steep cliffside path, blue sky with clouds, alpine landscape, no humans",
        "n1_1236": "mysterious shadow beast with glowing eyes, standing in deep misty forest at night, cinematic dark mood",
        "n1_1239": "traditional compass needle pointing East, old maps spread on table, sunlight coming from window, study room",
        "n1_1240": "empty iron cage door, open lock, zoo enclosure, overgrown vines, stone walls, sunlight breaking through bars, no humans",
        "n1_1243": "graph paper with X and Y axis, hand drawing line with pencil and ruler, engineering desk setup, close-up",
        "n1_1244": "scrolling through catalog index book, library catalog cards drawers, stacks of old paper books, reading room, no humans",
        "n1_1247": "high school tennis club, group of students holding rackets, wearing sports uniforms, tennis court, sunny afternoon",
        "n1_1249": "crumpled paper ball thrown in trash can, paint splattered canvas on floor, messy artist studio, frustrated creation mood, no humans",
        "n1_1251": "antique book scroll, Genji Monogatari scroll, detailed calligraphies, opened on wooden table, historic library, no humans",
        "n1_1267": "cozy bonfire camp fire at night, crackling orange flames, glowing embers, wooden logs, camping site, forest background, no humans",
        "n1_1272": "two police officers standing at crosswalk, street side, uniform, discussing route, city street, daytime",
        "n1_1275": "ink pen signing name on paper guestbook sheet, names column, wooden table, formal hall entrance, close-up, no humans",
        "n1_1282": "younger brother carrying backpack, high school uniform, running and looking back with a smile, sunny morning street",
        "n1_1292": "night highway coach bus, interior glowing with dim blue lights, window showing city night lights silhouette, empty seats",
        "n1_1297": "man wearing black mask disguise, dark clothing, hiding face, thief shadow silhouette, dramatic night lighting",
        "n1_1299": "electric circuit board diagram, copper paths, soldering iron smoke, workbench tools, detailed engineering, no humans",
        "n1_1300": "large white passenger ferry ship on ocean, sea waves, seagulls flying, distant island, sunny day, scenic travel",
        "n1_1301": "night sky curtain, deep blue sunset sky, silhouettes of forest, twilight glow, quiet landscape, no humans",
        "n1_1302": "carving woodblock print, hand holding chisel, wood carving process, paper print of anime portrait, art studio close-up",
        "n1_1304": "kid with bandage on knee, scraped skin, playground background, sitting on park bench, gentle care",
        "n1_1306": "tourist holding open travel guidebook, map graphics, historic city street backdrop, sightseeing, sunny day",
        "n1_1326": "colorful cocktail glass, lemon slice, mint leaf, bar counter background, glowing lights reflection, no humans",
        "n1_1332": "grand mosque dome silhouette, arabian nights scenery, starry sky, warm desert oasis backdrop, scenic landscape, no humans",
        "n1_1336": "grassy river embankment hill, walking path, clouds in blue sky, calm river flowing, green summer meadow, no humans",
        "n1_1357": "published book, author signature page, pen resting on desk, cozy study room bookshelf backdrop, no humans",
        "n1_1358": "original handwritten novel pages, fountain pen, open pages, stacks of notebooks, creative desk, soft sunlight, no humans"
    }
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache.update(new_tags)
    
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    print(f"Successfully merged 8th batch of 49 manual tags. New cache size: {len(cache)}")

if __name__ == "__main__":
    merge_batch_8()
