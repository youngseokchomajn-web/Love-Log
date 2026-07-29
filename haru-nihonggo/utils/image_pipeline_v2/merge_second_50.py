import json
import os

def merge_tags():
    cache_path = "utils/image_pipeline_v2/expanded_tags_cache.json"
    
    # 27 curated tags designed directly by Antigravity
    new_tags = {
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
        "n1_0839": "assistant holding briefcase, walking behind businessman, airport lobby, modern corridor, executive business trip, daytime"
    }
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    cache.update(new_tags)
    
    # Atomic write
    temp_path = cache_path + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, cache_path)
    print(f"Successfully merged 2nd batch of 27 high-quality tags. New cache size: {len(cache)}")

if __name__ == "__main__":
    merge_tags()
