import json
import os

def merge_batch_6():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    # Batch 6 curated tags designed directly by Antigravity
    new_tags = {
        "n1_0634": "honey dripping from wooden dipper, glass jar of honey, honeycomb piece, wooden table, warm golden glow, close-up, no humans",
        "n1_0638": "tired laborer sitting on bench, wipes sweat from forehead, muscular arms, worn out clothes, construction site background, sunset lighting",
        "n1_0639": "constable wearing historical edo period patrol uniform, holding jitte staff, chasing suspect down old street, cinematic action shot",
        "n1_0645": "hand holding glass of orange juice with striped straw, cafe table, ice cubes, cold drink close-up, sunny daylight",
        "n1_0648": "friendly landlord talking to tenant, holding keys, showing cozy apartment room, window with bright sunlight",
        "n1_0657": "glorious fantasy hero holding glowing sword, dramatic cape blowing, standing on mountain peak, dramatic epic sky, spotlight",
        "n1_0658": "classic white steamship sailing on calm sea, steam rising from funnel, nostalgic harbor, sunset sky, no humans",
        "n1_0664": "warm hands clasped together, visible skin texture, heartbeat pulse line graphic, close-up, caring and human gesture",
        "n1_0669": "vintage teletypewriter machine, printed paper rolls, office desk setting, 1970s interior, communication equipment, no humans",
        "n1_0673": "cute single fluffy white sheep, green grass pasture, wooden fence, sunny day, clear sky, no humans",
        "n1_0674": "focused archer drawing traditional kyudo bow, arrow aimed, serene bamboo garden background, traditional uniform, calm stance",
        "n1_0678": "wooden shogi board, holding a pawn shogi tile, hand placing tile forward, focus on shogi pieces, traditional japanese game",
        "n1_0683": "1boy, polite gentleman wearing classic suit and fedora hat, holding umbrella, street background, elegant gesture, smiling",
        "n1_0684": "golden retriever puppy wagging tail, back view, fluffy tail blur, running on green park lawn, daytime",
        "n1_0691": "traditional wedding matchmaker, wearing kimono, happy couple sitting in background, japanese tea room, auspicious decor",
        "n1_0696": "regal monarch holding scepter, gold crown, sitting on throne in palace, majestic royal hall, warm ambient lights",
        "n1_0700": "baby bottle filled with milk, cozy baby crib background, soft blanket, warm nursery room lighting, no humans",
        "n1_0701": "periodic table chart on study wall, chemistry textbook open, molecular model spheres on table, cozy science room, no humans",
        "n1_0704": "living room TV screen playing a colorful soda drink commercial, cozy room at night, screen glowing reflection, no humans",
        "n1_0716": "pair of round spectacles resting on open book page, study desk, soft warm desk lamp light, close-up, no humans",
        "n1_0720": "gardening bag of organic plant food, spilling soil nutrients, green plant in pot, garden trowel, sunny backyard, no humans",
        "n1_0721": "shiny aluminum pot, steaming soup inside, kitchen stove counter, steel cookware, modern kitchen setting, no humans",
        "n1_0723": "wealthy person, tuxedo, luxury mansion interior, marble floor, holding champagne glass, smiling, high-class atmosphere",
        "n1_0742": "interior, spacious hall, high ceiling, elegant stairs, glass windows, sunny interior, neat room, indoor, no humans",
        "n1_0750": "skilled workers, smart recruits, diverse professionals standing together, business casual, bright office hall, confident smiles, daytime",
        "n1_0751": "linen shirt, white linen fabric, detailed thread texture, clothes hanger, sunlight from window, warm breeze, cozy house, no humans",
        "n1_0754": "police patrol car, police sedan, red lights flashing, city street at day, outdoors, security, patrol, no humans",
        "n1_0756": "dessert plate, slice of strawberry shortcake, fork, mint leaf, white table, cafe setting, delicious sweet food, no humans",
        "n1_0763": "green plant seedling, growing sprout in soil, small pot, soil hands, sunlight, gardening close-up, no humans",
        "n1_0766": "sovereign ruler, elegant historical throne, palace hall, crown emblem, state room, formal setting, indoor, no humans",
        "n1_0773": "ancient currency, cowrie shells, antique coins, wooden table, historical exchange, museum collection, detailed, no humans",
        "n1_0775": "cute ghost silhouette, floating translucent white figure, old abandoned house hall, wooden corridor, moonlight from window, soft glow, no humans",
        "n1_0780": "pebbles on ground, gravel path, small stones, grey and brown colors, macro shot, garden ground, outdoors, no humans",
        "n1_0781": "pair of leather winter boots, cozy wooden floor, fireplace warm light background, boots side by side, no humans",
        "n1_0783": "smiling father and mother, middle-aged parents, standing side by side, warm home background, casual clothes, gentle look",
        "n1_0785": "mountain summit, peak, blue sky, snow capped top, clouds below, majestic view, outdoors, scenic, no humans",
        "n1_0787": "old village boundary map, paper scroll on wooden table, hand pointing at section, ink calligraphy, historical study",
        "n1_0788": "cows and sheep grazing, farm animals, green grass field, wooden fence, sunny day, farm background, outdoors, no humans",
        "n1_0791": "1girl, tour guide, holding small flag, pointing forward, historic landmark background, tourists listening in background, daytime",
        "n1_0795": "cute miscellaneous goods, wooden shelves, colorful cups, notebooks, stationary items, small gift shop interior, warm glow, no humans",
        "n1_0797": "fresh domestic vegetables, farm basket, local farm sign, tomatoes, cucumbers, wooden table, sunny outdoor, no humans",
        "n1_0798": "santa claus, red suit, white beard, holding gift sack, fireplace background, smiling, warm holiday atmosphere",
        "n1_0802": "plastic document folders, neat binder files on shelf, office organization, labels, office interior, clean desk, no humans",
        "n1_0810": "anatomical cell wall, healthy intestine microvilli, science illustration, medical graphics, light blue color tone, no humans",
        "n1_0814": "virus particle under microscope, viral sphere, spike proteins, science lab screen visual, abstract neon colors, no humans",
        "n1_0815": "red torii gate, Shinto shrine entrance, forest background, stone path, serene morning sun, traditional japanese, no humans",
        "n1_0822": "corporate executives meeting, boardroom table, suit and ties, discussing documents, modern office glass wall, professional setting",
        "n1_0838": "elderly grandmother, smiling face, silver hair, wearing cozy cardigan, sitting in rocking chair, warm sun from window",
        "n1_0839": "assistant holding briefcase, walking behind businessman, airport lobby, modern corridor, executive business trip, daytime",
        "n1_0845": "hand saw, cutting wood log, wood sawdust, workshop table, carpentry tools, no humans"
    }
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache.update(new_tags)
    
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    print(f"Successfully merged 6th batch of 50 manual tags. New cache size: {len(cache)}")

if __name__ == "__main__":
    merge_batch_6()
