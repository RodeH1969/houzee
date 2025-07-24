import os
import json
import requests
import traceback
from datetime import datetime

def send_telegram_notification(winner_data, suburb):
    """Send Telegram notification of new winner"""
    
    print(f"🔍 TELEGRAM DEBUG: Function called with suburb={suburb}")
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    print(f"🔍 TELEGRAM DEBUG: bot_token exists: {bool(bot_token)}")
    print(f"🔍 TELEGRAM DEBUG: chat_id exists: {bool(chat_id)}")
    
    if not bot_token or not chat_id:
        print("❌ TELEGRAM ERROR: Missing bot token or chat ID")
        return False
    
    # Format the message
    message = f"""🏠 NEW HOUZEE WINNER!

Name: {winner_data.get('name', 'Unknown')}
Email: {winner_data.get('email', 'Unknown')}
Phone: {winner_data.get('phone', 'Unknown')}
Suburb: {suburb}
House: (guessed correctly)
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

They've won the $10 gift card!"""
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        print(f"🔍 TELEGRAM DEBUG: Sending to URL: {url}")
        print(f"🔍 TELEGRAM DEBUG: Payload: {payload}")
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"🔍 TELEGRAM DEBUG: Response status: {response.status_code}")
        print(f"🔍 TELEGRAM DEBUG: Response text: {response.text}")
        
        if response.status_code == 200:
            print("✅ TELEGRAM SUCCESS: Message sent!")
            return True
        else:
            print(f"❌ TELEGRAM ERROR: Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TELEGRAM EXCEPTION: {str(e)}")
        print(f"❌ TELEGRAM TRACEBACK: {traceback.format_exc()}")
        return False

def save_winner(winner_data):
    """Save winner data and return winner info with image path"""
    
    print(f"🔍 SAVE_WINNER DEBUG: Received data: {winner_data}")
    
    try:
        # Get suburb and generate image info
        suburb = winner_data.get('suburb', '')
        print(f"🔍 SAVE_WINNER DEBUG: Suburb from data: {suburb}")
        
        # Suburb to prefix mapping
        suburb_house_mappings = {
            'Ashgrove': 'Ash',
            'The Gap': 'Gap', 
            'Red Hill': 'RedHill',
            'Bardon': 'Bard',
            'Paddington': 'Padd',
            'Enoggera': 'Enog'
        }
        
        # Get current house number and advance to next
        current_house_file = 'data/current_houses.json'
        
        # Load current house numbers
        if os.path.exists(current_house_file):
            with open(current_house_file, 'r') as f:
                current_houses = json.load(f)
        else:
            # Initialize with house 1 for all suburbs
            current_houses = {suburb: 1 for suburb in suburb_house_mappings.keys()}
            os.makedirs('data', exist_ok=True)
        
        # Get current house number for this suburb
        current_house_num = current_houses.get(suburb, 1)
        prefix = suburb_house_mappings.get(suburb, suburb[:4])
        
        # Generate image path for the house they just won
        won_image_path = f"{suburb}_houses/{prefix}{current_house_num}.png"
        
        print(f"🔍 SAVE_WINNER DEBUG: Current house num: {current_house_num}")
        print(f"🔍 SAVE_WINNER DEBUG: Generated image path: {won_image_path}")
        
        # Create winner entry for JSON file
        winner_entry = {
            'name': winner_data.get('name', ''),
            'email': winner_data.get('email', ''),
            'phone': winner_data.get('phone', ''),
            'suburb': suburb,  # ✅ FIXED: Save suburb
            'image': won_image_path,  # ✅ FIXED: Save image path
            'address': f"House in {suburb}",  # ✅ FIXED: Add address
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"🔍 SAVE_WINNER DEBUG: Winner entry: {winner_entry}")
        
        # Load existing winners
        winners_file = 'data/winners.json'
        if os.path.exists(winners_file):
            with open(winners_file, 'r') as f:
                winners = json.load(f)
        else:
            winners = []
            os.makedirs('data', exist_ok=True)
        
        # Add new winner
        winners.append(winner_entry)
        
        # Save updated winners
        with open(winners_file, 'w') as f:
            json.dump(winners, f, indent=2)
        
        print(f"✅ SAVE_WINNER SUCCESS: Winner added to {winners_file}")
        
        # Advance to next house
        current_houses[suburb] = current_house_num + 1
        
        # Save updated house numbers
        with open(current_house_file, 'w') as f:
            json.dump(current_houses, f, indent=2)
        
        print(f"✅ SAVE_WINNER SUCCESS: Advanced {suburb} to house {current_house_num + 1}")
        
        # Send Telegram notification
        telegram_sent = send_telegram_notification(winner_data, suburb)
        
        return {
            'success': True,
            'winner': winner_entry,  # ✅ Return winner with image and suburb
            'telegram_sent': telegram_sent,
            'next_house': current_house_num + 1
        }
        
    except Exception as e:
        print(f"❌ SAVE_WINNER ERROR: {str(e)}")
        print(f"❌ SAVE_WINNER TRACEBACK: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
            'telegram_sent': False
        }