import requests

def send_telegram_message(message):
    bot_token = '7808231868:AAHNf2dvyAm697DyB2wfLlrUS-PpniK29YI'
    chat_id = '-4770597616'
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    requests.post(url, data=payload)
