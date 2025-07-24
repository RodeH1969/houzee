import os
import json

def save_winner(winner_data):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    winners_file = os.path.join(base_path, 'winners.json')
    current_file = os.path.join(base_path, 'current_house.json')

    # Ensure winners.json exists
    if not os.path.exists(winners_file):
        with open(winners_file, 'w') as f:
            json.dump([], f)

    # Load + append winner
    with open(winners_file, 'r') as f:
        winners = json.load(f)

    winners.append(winner_data)

    with open(winners_file, 'w') as f:
        json.dump(winners, f, indent=2)

    # ✅ CRITICAL FIX: Extract suburb from image path
    image_path = winner_data.get('image', '')
    suburb = None
    
    print(f"DEBUG: Processing image path: {image_path}")  # Debug log
    
    # Parse suburb from image path (e.g., "Ashgrove_houses/Ash1.png" → "Ashgrove")
    if '_houses/' in image_path:
        suburb_folder = image_path.split('_houses/')[0]
        print(f"DEBUG: Extracted suburb folder: {suburb_folder}")  # Debug log
        
        if suburb_folder == "Ashgrove":
            suburb = "Ashgrove"
        elif suburb_folder == "TheGap":
            suburb = "The Gap"
        elif suburb_folder == "RedHill":
            suburb = "Red Hill"
        elif suburb_folder == "Bardon":
            suburb = "Bardon"
        elif suburb_folder == "Paddington":
            suburb = "Paddington"
        elif suburb_folder == "Enoggera":
            suburb = "Enoggera"
        
        print(f"DEBUG: Mapped to suburb: {suburb}")  # Debug log
    
    if not suburb:
        print(f"ERROR: Could not determine suburb from image path: {image_path}")
        return winner_data

    # ✅ Load current house indices
    if not os.path.exists(current_file):
        with open(current_file, 'w') as f:
            json.dump({}, f)

    with open(current_file, 'r') as f:
        current = json.load(f)

    # ✅ ONLY increment house number for the CORRECT suburb
    current_index = current.get(suburb, 1)
    print(f"DEBUG: Current index for {suburb}: {current_index}")  # Debug log
    
    current[suburb] = current_index + 1
    print(f"DEBUG: New index for {suburb}: {current[suburb]}")  # Debug log

    with open(current_file, 'w') as f:
        json.dump(current, f, indent=2)

    print(f"DEBUG: Updated current_house.json: {current}")  # Debug log

    return winner_data