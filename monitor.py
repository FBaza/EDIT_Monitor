import requests
import feedparser
import json
from datetime import datetime

TELEGRAM_TOKEN = "7979708157:AAEkoIFukGjf8KquWd5xy3Oce8_SBhrqG2A"
CHAT_ID = "7439260197"

EDIT_RSS = "https://ir.editasmedicine.com/rss/news-releases.xml"

# ----------------------------------------------------------
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

# ----------------------------------------------------------
def load_hitos_config():
    with open("hitos_config.json", "r") as f:
        return json.load(f)

# ----------------------------------------------------------
def update_panel(hito_id, evidence_link):
    with open("hitos_edit.md", "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith(f"| {hito_id} "):
            # Marcamos como cumplido y añadimos evidencia
            parts = line.split("|")
            parts[4] = " Cumplido "
            parts[5] = f" {evidence_link} |\n"
            new_line = "|".join(parts)
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    with open("hitos_edit.md", "w") as f:
        f.writelines(new_lines)

# ----------------------------------------------------------
def detect_hito(title, summary, config):
    text = (title + " " + summary).lower()
    for hito_id, hdata in config.items():
        for kw in hdata["keywords"]:
            if kw.lower() in text:
                return hito_id
    return None

# ----------------------------------------------------------
def check_edit_rss():
    feed = feedparser.parse(EDIT_RSS)
    if not feed.entries:
        return None, None, None

    latest = feed.entries[0]
    title = latest.title
    link = latest.link
    summary = latest.get("summary", "")
    date = latest.published

    # Evitar duplicados
    try:
        with open("last_title.txt", "r") as f:
            last_title = f.read().strip()
    except:
        last_title = ""

    if title == last_title:
        return None, None, None

    # Guardar último título
    with open("last_title.txt", "w") as f:
        f.write(title)

    return title, summary, link

# ----------------------------------------------------------
if __name__ == "__main__":
    title, summary, link = check_edit_rss()
    if not title:
        exit()

    # Enviar alerta Telegram
    alert_msg = f"🚨 ALERTA EDIT\n\n📰 {title}\n🔗 {link}"
    send_telegram(alert_msg)

    # Detectar hito
    config = load_hitos_config()
    detected = detect_hito(title, summary, config)

    if detected:
        update_panel(detected, link)
        send_telegram(f"📌 Hito actualizado automáticamente: {detected}")
