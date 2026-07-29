import json

ROOT_DIR = "/Users/youngseok/Desktop/love-log/haru-nihonggo"

def fix_awkward_adverbs():
    tags_path = f"{ROOT_DIR}/utils/image_pipeline_v2/expanded_tags_cache.json"
    with open(tags_path, "r", encoding="utf-8") as f:
        tags_cache = json.load(f)
        
    base_ghibli = "studio ghibli style, warm color palette, soft volumetric lighting"
    
    # 1. たいへん (매우, 대단히): 엄청난 양의 책 탑에 둘러싸여 대단히 놀라는 표정과 열정
    tags_cache["n5_0030"] = f"anime character sitting at desk surrounded by an extraordinarily tall towering stack of books, wide amazed eyes, dramatic scale, {base_ghibli}"
    
    # 2. なかなか (꽤, 좀처럼): 퍼즐 조각을 대보며 꽤 만만치 않은 표정으로 생각하는 명쾌한 연출
    tags_cache["n3_1136"] = f"thoughtful anime character holding chin looking intently at a challenging jigsaw puzzle piece on wooden table, deep focus, {base_ghibli}"
    
    # 3. 非常に (매우): 엄청난 규모의 환한 햇살과 감탄하는 표정 연출
    tags_cache["n4_603"] = f"character with wide starry eyes of extreme wonder looking at a breathtaking massive glowing rainbow sky, grand scale, {base_ghibli}"

    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_cache, f, ensure_ascii=False, indent=2)
        
    print("[Success] 어색한 부사(たいへん, なかなか, 非常に) 커스텀 프롬프트 개선 완료!")

if __name__ == "__main__":
    fix_awkward_adverbs()
