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
    
    print(f"🔍 TELEGRAM DEBUG: bot_token={'SET' if bot_token else 'MISSING'}")
    print(f"🔍 TELEGRAM DEBUG: chat_id={'SET' if chat_id else 'MISSING'}")
    
    if not bot_token or not chat_id:
        print("❌ TELEGRAM DEBUG: Missing environment variables")
        return False
        
    # Create suburb mappings for house prefixes
    suburb_house_mappings = {
        'Ashgrove': 'Ash',
        'The Gap': 'Gap', 
        'Red Hill': 'RedHill',
        'Bardon': 'Bard',
        'Paddington': 'Padd',
        'Enoggera': 'Enog'
    }
    
    house_prefix = suburb_house_mappings.get(suburb, suburb)
    print(f"🔍 TELEGRAM DEBUG: house_prefix={house_prefix}")
    
    message = f"""🏆 NEW HOUZEE WINNER! 🏆

👤 Name: {winner_data.get('name', 'Unknown')}
📧 Email: {winner_data.get('email', 'Unknown')}  
📱 Phone: {winner_data.get('phone', 'Unknown')}
🏠 Suburb: {suburb}
🏡 House: {house_prefix} (guessed correctly)
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎉 They've won the $10 gift card!"""
    
    print(f"🔍 TELEGRAM DEBUG: Message created, length: {len(message)}")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        
        print(f"🔍 TELEGRAM DEBUG: About to send request...")
        response = requests.post(url, json=payload, timeout=10)
        print(f"🔍 TELEGRAM DEBUG: Response status: {response.status_code}")
        print(f"🔍 TELEGRAM DEBUG: Response text: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Telegram notification sent for {winner_data.get('name')} - {suburb}")
            return True
        else:
            print(f"❌ Telegram failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram exception: {str(e)}")
        print(f"🔍 Exception traceback: {traceback.format_exc()}")
        return False

def save_winner(winner_data):
    """Save winner data and send notifications"""
    
    print(f"🔍 DEBUG: save_winner called with data: {winner_data}")
    
    try:
        # Get base directory path  
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        winners_file = os.path.join(base_path, 'winners.json')
        current_house_file = os.path.join(base_path, 'current_house.json')
        
        print(f"🔍 DEBUG: Winners file path: {winners_file}")
        
        # Load existing winners
        if os.path.exists(winners_file):
            with open(winners_file, 'r') as f:
                winners = json.load(f)
                print(f"🔍 DEBUG: Loaded {len(winners)} existing winners")
        else:
            winners = []
            print("🔍 DEBUG: Creating new winners list")
        
        # Create winner entry
        winner_entry = {
            'name': winner_data.get('name', ''),
            'email': winner_data.get('email', ''),
            'phone': winner_data.get('phone', ''),
            'suburb': winner_data.get('suburb', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        winners.append(winner_entry)
        print(f"🔍 DEBUG: Added winner: {winner_entry}")
        
        # Save winners
        with open(winners_file, 'w') as f:
            json.dump(winners, f, indent=2)
        print(f"🔍 DEBUG: Saved {len(winners)} total winners")
        
        # Update current house tracking
        if os.path.exists(current_house_file):
            with open(current_house_file, 'r') as f:
                current_house_data = json.load(f)
        else:
            current_house_data = {}
        
        suburb = winner_data.get('suburb', '')
        if suburb in current_house_data:
            current_house_data[suburb] += 1
        else:
            current_house_data[suburb] = 2  # Next house after win
        
        with open(current_house_file, 'w') as f:
            json.dump(current_house_data, f, indent=2)
        
        print(f"🔍 DEBUG: Updated {suburb} to house {current_house_data[suburb]}")
        
        # Send Telegram notification
        print(f"🔍 DEBUG: Sending Telegram notification for {suburb}")
        telegram_sent = send_telegram_notification(winner_data, suburb)
        
        return {
            'success': True,
            'winner': winner_entry,
            'total_winners': len(winners),
            'telegram_sent': telegram_sent
        }
        
    except Exception as e:
        error_msg = f"ERROR in save_winner: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e)
        }