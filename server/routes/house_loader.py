import os
import json

SUBURB_PREFIXES = {
    "Ashgrove": "Ash",
    "The Gap": "TheGap", 
    "Red Hill": "RedHill",
    "Bardon": "Bardon",
    "Paddington": "Padd",
    "Enoggera": "Enog",
    "Alderley": "Ald",
    "Sherwood": "Sher",
    "Corinda": "Cor",
    "Oxley": "Oxley",
    "Jindalee": "Jind",
    "Chapel Hill": "ChapelHill",
    "Kenmore": "Ken",
    "Brookfield": "Brookfield",
    "Toowong": "Toowong"
}

def get_current_house_data(suburb_name):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    clean_name = suburb_name.replace(" ", "")
    suburb_folder = f"{clean_name}_houses"
    suburb_path = os.path.join(base_path, suburb_folder)

    if not os.path.exists(suburb_path):
        return None

    # Load current house index
    ch_file = os.path.join(base_path, 'current_house.json')
    if not os.path.exists(ch_file):
        with open(ch_file, 'w') as f:
            json.dump({}, f)

    with open(ch_file, 'r') as f:
        current = json.load(f)

    current_index = current.get(suburb_name, 1)

    prefix = SUBURB_PREFIXES.get(suburb_name)
    if not prefix:
        # Fallback: use first part of folder name as prefix
        prefix = clean_name[:4]

    image_file = f"{prefix}{current_index}.png"
    address_file = f"{prefix}{current_index}_address.txt"

    full_image_path = f"{suburb_folder}/{image_file}"
    address_path = os.path.join(suburb_path, address_file)

    if not os.path.exists(address_path) or not os.path.exists(os.path.join(base_path, full_image_path)):
        return None  # No more houses available

    with open(address_path, 'r', encoding='utf-8') as f:
        answer = f.read().strip()

    return {
        'image_path': full_image_path,
        'answer': answer
    }
