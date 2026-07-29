import os
import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

# Dictionary of specialized N1 prompt improvements
N1_PROMPT_FIXES = {
    "n1_0140": "handheld electric power drill, metal drill bit, wood workbench with sawdust, hardware repair shop, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0621": "roll of fine silk cloth, traditional kimono fabric bolt, vibrant textile dye, wooden weaving loom shop, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1696": "1girl wearing lightweight single layer unlined summer kimono (hitoe), walking in gentle breeze, sunny day, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1782": "hem of long skirt floating in gentle meadow wind, walking along mountain foot trail, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1861": "taking a deep breath of fresh mountain air, open arms on green hill, glowing lungs concept art, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2600": "single pure white lily flower resting on wooden table by quiet window, soft morning sunlight, peaceful memory, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2621": "tranquil bamboo forest in morning mist, sunbeams filtering through leaves, perfectly quiet and silent nature, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_3014": "glowing lightbulb and glowing brain thoughts, creative idea spark, starry night sky background, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0049": "vintage wall calendar with pages turned back two months, nostalgic autumn room window, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0067": "neatly arranged summary notes and pinned index cards on cork board, organized workplace, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0099": "untidy study desk, neglected books pushed aside, clock ticking, afternoon sun shadow, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0139": "boat sailing smoothly on calm river with wind in sails, steady progress, bright sunny day, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0199": "bullet point checklist on paper board with wooden pen, organized list, clean desk, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0206": "magnifying glass highlighting a specific spot on vintage map, detailed focus, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0255": "piggy bank and monthly family budget ledger with coins, cozy kitchen counter, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0465": "printed movie script bound with brads, theater stage curtain in background, spotlight glow, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0475": "stacks of colorful educational building blocks, globe, abacus, teaching tools, bright room, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0663": "fountain pen writing dictation on scroll paper, ink bottle, cozy library table, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0689": "round table conference, three people in active discussion, speech bubbles concept, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0693": "kind elderly mentor whispering friendly advice to young student, encouraging smile, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0701": "atomic model glow, glowing chemical element symbols floating in air, science lab beaker, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0706": "hand holding fountain pen, neat Japanese dictation writing, ink bottle, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0744": "curriculum chart with colorful subject icons (math, science, art), school hallway, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0764": "runner advancing along track toward finish line, milestone progress flags, sunny sky, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0795": "charming boutique shop window displaying cute sundries, teacups, clocks, small decorations, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_0951": "exam question paper with seal stamp, professor setting exam questions, university desk, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1046": "biological tree diagram of animal subfamilies, butterfly specimens in glass frame, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1072": "journalist holding vintage camera and press badge, interviewing craftsman, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1195": "single-minded focus, archer aiming bow at target center, serene temple garden, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1219": "vintage Japanese street sign showing district block number (Chome), retro town corner, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1358": "original manuscript scroll with wax seal, author desk, feather quill pen, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1413": "hourglass with almost all sand fallen to bottom, late afternoon sunlight, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1435": "neatly arranged tools in wooden box, perfectly aligned items, clean room, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1436": "illuminated dictionary definition icon, open book with glowing key term, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1478": "golden coins growing out of small potted plant, interest savings growth concept, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1530": "crossroads sign with two paths under sunset sky, thoughtful decision moment, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1550": "close-up of gentle resting eyes, soft closed eyelids, peaceful sleeping face, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1575": "golden coins payment on counter, receipt paper, cost expense concept, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1656": "index finger pointing directly at specific detail on blueprint map, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1790": "bound theater script with yellow highlighter marks, backstage dressing room mirror, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1840": "young sapling plant being watered and nurtured in greenhouse, growth training, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1845": "distinct red stamp mark logo on wooden tag, signpost symbol, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_1959": "personal wooden locker box with key tag, personal belongings inside, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2006": "spotlight illuminating single shining star object on dark velvet, attention focus, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2107": "lady justice scales of law and leather bound law book, wooden gavel, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2124": "official registration certificate paper with stamp seal, fountain pen signing, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2149": "calendar page showing today, tomorrow, and day after tomorrow highlighted with sun icon, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2267": "printing press machine, woodblock print impression on paper, edition publication, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2326": "neat long row of colorful lanterns lined up along festival street, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2363": "perfectly aligned colored pencils by rainbow gradient order, immaculate desk, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2542": "tangled ball of dark yarn unravelling near soothing cup of chamomile tea, stress relief, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2616": "playful kitten batting at yarn ball, mischievous frolic, sunny porch, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2649": "blackboard covered in academic scientific theory diagrams, university lecture hall, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2715": "grammar chart showing main verb connected to auxiliary verb particle, clear diagram, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2785": "ancient samurai armor display in museum, historical war banner, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2791": "detective trench coat, magnifying glass inspecting footprints, mystery puzzle, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2888": "skipping a stone across water surface, leaving gap in ripples, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2946": "vintage store ledger book with credit tally marks, old wooden counter, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_2949": "edited book manuscript with red correction marks, revised edition printing, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_3097": "young enthusiastic recruit bowing politely in modern office lobby, first day of work, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_3122": "glowing word tree with expanding branches of Japanese vocabulary terms, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_3201": "water overflowing over rim of glass mug onto wooden tray, sparkling water droplets, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_3372": "abbreviation diagram showing long phrase shortened to acronym letters, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_3402": "hand playfully turning gears of small brass clockwork toy, fidgeting, studio ghibli style, warm color palette, soft volumetric lighting",
    "n1_3426": "adding extra puzzle piece to complete picture, supplementary piece, studio ghibli style, warm color palette, soft volumetric lighting"
}

def apply_n1_fixes():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    updated_count = 0
    for w_id, new_prompt in N1_PROMPT_FIXES.items():
        tags_cache[w_id] = new_prompt
        updated_count += 1
        
    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print(f"[Success] N1 단어 {updated_count}개 시각 프롬프트 정밀 개선 완료!")

if __name__ == "__main__":
    apply_n1_fixes()
