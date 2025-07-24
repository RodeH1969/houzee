def send_telegram_notification(winner_data, suburb):
    """Send Telegram notification of new winner"""
    
    print(f"🔍 TELEGRAM DEBUG: Function called with suburb={suburb}")
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    print(f"🔍 TELEGRAM DEBUG: bot_token={'SET' if bot_token else 'NOT SET'}")
    print(f"🔍 TELEGRAM DEBUG: chat_id={'SET' if chat_id else 'NOT SET'}")
    
    if not bot_token or not chat_id:
        print("⚠️ Telegram not configured - skipping notification")
        return
    
    print(f"🔍 TELEGRAM DEBUG: About to send message for {winner_data.get('name')}")
    
    try:
        # Create rich Telegram message
        message = f"""🏆 *NEW HOUZEE WINNER!* 🏆

🏘️ *Suburb:* {suburb}
👤 *Winner:* {winner_data.get('name', 'Unknown')}
📱 *Mobile:* {winner_data.get('mobile', 'Not provided')}
🏠 *Address:* {winner_data.get('address', 'Unknown')}
🖼️ *House:* {winner_data.get('image', 'Unknown')}

⏰ *Time:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""

        # Send to Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        print(f"🔍 TELEGRAM DEBUG: Sending POST to {url}")
        
        response = requests.post(url, json=payload)
        
        print(f"🔍 TELEGRAM DEBUG: Response status: {response.status_code}")
        print(f"🔍 TELEGRAM DEBUG: Response text: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Telegram notification sent for {winner_data.get('name')} - {suburb}")
        else:
            print(f"❌ Telegram notification failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Telegram notification error: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")