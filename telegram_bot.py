import requests

BOT_TOKEN = "8676724645:AAFzZn3KqLucREwL0XWBJFaeoBpMiesAAro"
CHAT_ID = "7970673034"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            print("Telegram Message Sent")
        else:
            print("Telegram Error:", response.text)

    except Exception as e:
        print("Telegram Exception:", e)