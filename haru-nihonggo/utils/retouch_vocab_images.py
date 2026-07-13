import os
import pandas as pd
import glob

excel_path = "data/jlpt_n4_clean_merged.xlsx"
image_dir = "assets/images/words"

# Comprehensive list of 71 words to retouch for 100% intuitive visual guessability
retouch_mapping = {
    # Original 24 (Ambiguous / Homonym / Error fixes)
    'n4_101': 'small green sprout growing between two large stones',
    'n4_102': 'glowing green checkmark icon',
    'n4_106': 'hand pouring water out of a glass cup to empty it',
    'n4_129': 'multiple people talking with colored speech bubbles showing ideas',
    'n4_132': 'ascending arrow pointing up from a flat base line',
    'n4_133': 'a person running while looking at a pocket watch with sweat drops',
    'n4_134': 'a cute dog bringing a rolled newspaper in its mouth to owner',
    'n4_135': 'hand receiving a gift box from another hand',
    'n4_148': 'a wind-up toy robot walking with motion lines',
    'n4_149': 'Pinocchio cartoon character with a very long wooden nose',
    'n4_295': 'magnifying glass pointing at a spark starting a fire',
    'n4_296': 'two angry kids pulling a teddy bear in opposite directions',
    'n4_483': 'hand holding a checklist clipboard and ticking boxes with red pen',
    'n4_484': 'strong muscular arm lifting a heavy dumbbell',
    'n4_492': 'police officer catching a thief by the shoulder',
    'n4_494': 'colorful refrigerator magnets sticking tightly to a metal surface',
    'n4_495': 'hand putting raw cucumber slices into glass jar with pickle liquid',
    'n4_500': 'hands wrapping a gift box with brown paper and twine',
    'n4_503': 'fishing rod pulling a splashing fish out of the water',
    'n4_558': 'sneaky thief in black mask running with a sack of money',
    'n4_559': 'butter knife spreading yellow butter smoothly on a slice of toast',
    'n4_560': 'wet soaked cat sitting in the rain under a large green leaf',
    'n4_567': 'single slice of pizza left in an empty cardboard pizza box',
    'n4_645': 'scoreboard showing 0 to 5 and a player sitting on the field with head down',
    
    # New 47 (Abstract nouns, verbs, adverbs, and generic icons)
    'n4_100': 'two business people bowing politely to each other',
    'n4_103': 'cute baby lying in a crib with a baby bottle',
    'n4_104': 'hiker climbing up a steep mountain trail',
    'n4_288': 'delicious birthday cake with glowing candles',
    'n4_289': 'person with a white bandage on their arm and a band-aid on their cheek',
    'n4_429': 'wooden gavel resting on a law book next to a ballot box',
    'n4_436': 'mother gently tucking her sleeping child into a cozy bed',
    'n4_437': 'hand drawing a straight line on paper with a ruler',
    'n4_439': 'two small toy soldiers facing each other on a table',
    'n4_440': 'older university student helping a younger student with books',
    'n4_442': 'doctor or counselor sitting in a chair talking to a patient',
    'n4_443': 'hand watering a small green plant seedling in a pot',
    'n4_444': 'black graduation cap flying in the blue sky',
    'n4_445': 'old man with a grey beard and glasses smiling',
    'n4_446': 'fluffy white pillow and soft clouds',
    'n4_447': 'old woman knitting with yarn and glasses',
    'n4_459': 'red circle, blue square, and green triangle grouped together',
    'n4_462': 'a tower of wooden blocks falling and collapsing down',
    'n4_466': 'person ringing a doorbell of a house holding a gift box',
    'n4_470': 'hand setting a bowling pin upright on the floor',
    'n4_471': 'workers building a brick wall with trowel and bricks',
    'n4_473': 'wooden wall shelves holding books and potted plants',
    'n4_474': 'group of friends laughing and throwing hands in the air',
    'n4_479': 'piggy bank overflowing with gold coins',
    'n4_480': 'gentleman with a mustache, glasses, and a top hat',
    'n4_481': 'radiator heater glowing with warm orange waves',
    'n4_482': 'single red blood drop dripping down',
    'n4_489': 'medical syringe needle with a drop of liquid',
    'n4_490': 'cars parked neatly in parking spaces with blue P sign',
    'n4_491': 'desktop globe of the earth showing continents',
    'n4_497': 'reporter holding a microphone and speaking to camera',
    'n4_501': 'woman wearing a wedding ring holding hands with husband',
    'n4_504': 'tour guide leading a group of tourists holding a flag',
    'n4_507': 'scales perfectly balanced with equal weights',
    'n4_546': 'basket overflowing with fresh fruits and vegetables',
    'n4_557': 'cute fabric ragdoll with button eyes on a bed',
    'n4_561': 'paper price tag with dollar sign hanging on clothes',
    'n4_562': 'person lying down with a cooling gel pad on forehead',
    'n4_563': 'student studying hard under a desk lamp at night',
    'n4_565': 'cute kitten yawning widely on a soft blanket',
    'n4_566': 'person sleeping peacefully in a cozy bed under a blanket',
    'n4_568': 'hand gently touching throat or neck',
    'n4_570': 'giant ferris wheel spinning in an amusement park',
    'n4_571': 'single green maple leaf with clear veins',
    'n4_573': 'cashier working behind a convenience store counter',
    'n4_579': 'an envelope with a letter showing a green checkmark reply',
    'n4_587': 'teacher sticking a gold star sticker on student paper'
}

def main():
    if not os.path.exists(excel_path):
        print(f"⚠️ Excel not found: {excel_path}")
        return
        
    df = pd.read_excel(excel_path)
    
    reset_count = 0
    deleted_files = 0
    
    for index, row in df.iterrows():
        w_id = str(row['ID']).strip()
        if w_id in retouch_mapping:
            new_prompt = retouch_mapping[w_id]
            current_img_key = str(row['이미지 키']).strip()
            
            # Delete old files if they exist on disk
            old_files = glob.glob(os.path.join(image_dir, f"{w_id}_*.png"))
            for f in old_files:
                try:
                    os.remove(f)
                    deleted_files += 1
                    print(f"  🗑️ Deleted old image: {f}")
                except Exception as e:
                    print(f"  ⚠️ Error deleting {f}: {e}")
                        
            # Update Excel row
            df.at[index, '비주얼 프롬프트'] = new_prompt
            df.at[index, '이미지 키'] = ''
            reset_count += 1
            
    if reset_count > 0:
        df.to_excel(excel_path, index=False)
        print(f"🔄 Reset {reset_count} rows in Excel and deleted {deleted_files} files.")
    else:
        print("💡 No rows to retouch.")

if __name__ == "__main__":
    main()
