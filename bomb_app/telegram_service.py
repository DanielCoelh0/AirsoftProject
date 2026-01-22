
import requests
from . import telegram_config

class TelegramService:
    def __init__(self):
        self.token = telegram_config.TELEGRAM_BOT_TOKEN
        self.provider = telegram_config.TELEGRAM_PROVIDER
                
    def send_message(self, chat_id, message):
        """
        Sends a Telegram message to the specified chat ID.
        chat_id: String or Integer
        message: String content
        """
        print(f"[TELEGRAM SERVICE] Sending to {chat_id}: {message}")
        
        if self.provider == "MOCK":
            print(f"[TELEGRAM MOCK] SUCCESS")
            return True
            
        elif self.provider == "REAL":
            try:
                url = f"https://api.telegram.org/bot{self.token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": message
                }
                response = requests.post(url, data=payload)
                if response.status_code == 200:
                    print(f"[TELEGRAM REAL] Message sent to {chat_id}")
                    return True
                else:
                    print(f"[TELEGRAM REAL] Error {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                print(f"[TELEGRAM REAL] Exception: {e}")
                return False
        
        return False

# Singleton instance
telegram_service = TelegramService()
