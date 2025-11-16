import requests
import time
import feedparser

TELEGRAM_TOKEN = "7979708157:AAEkoIFukGjf8KquWd5xy3Oce8_SBhrqG2A"
CHAT_ID = "7439260197"

EDIT_RSS = "https://ir.editasmedicine.com/rss/news-releases.xml"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

def check_edit_rss():
    feed = feedparser.parse(EDIT_RSS)
    if not feed.entries:
        return None
    latest = feed.entries[0]
    title = latest.title
    link = latest.link
    date = latest.published

    # Guardamos el estado para no duplicar notificaciones
    try:
        with open("last_edit.txt", "r") as f:
            last_title = f.read().strip()
    except:
        last_title = ""

    if title != last_title:
        with open("last_edit.txt", "w") as f:
            f.write(title)
        return f"🚨 NUEVO HITÓ DE EDIT\n\n📰 {title}\n🗓 {date}\n🔗 {link}"
    return None

if __name__ == "__main__":
    alert = check_edit_rss()
    if alert:
        send_telegram(alert)
