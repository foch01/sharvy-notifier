#!/usr/bin/env python3
"""Script Sharvy - Récupère la place de parking du jour et notifie sur Telegram."""

import json
import os
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

EMAIL = os.environ.get("SHARVY_EMAIL")
PASSWORD = os.environ.get("SHARVY_PASSWORD")
BASE = os.environ.get("SHARVY_BASE_URL")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET = os.environ.get("TELEGRAM_TARGET")

STATUS_LABELS = {
    0: "Pas de demande",
    1: "Place non attribuée / demande en attente",
    2: "Demande en cours / en attente d'attribution",
    3: "Place attribuée et confirmée",
    4: "Gérée par un service externe",
    5: "Jour passé / non travaillé",
}


TELEGRAM_API = "https://api.telegram.org/bot"


def send_telegram(message):
    try:
        url = f"{TELEGRAM_API}{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_TARGET,
            "text": message,
            "parse_mode": "Markdown",
        }
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"⚠️  Erreur envoi Telegram : {e}")


def login(session):
    resp = session.get(f"{BASE}/Login")
    soup = BeautifulSoup(resp.text, "html.parser")

    data = {
        "__VIEWSTATE": soup.find("input", {"id": "__VIEWSTATE"})["value"],
        "__VIEWSTATEGENERATOR": soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"],
        "__EVENTVALIDATION": soup.find("input", {"id": "__EVENTVALIDATION"})["value"],
        "inputEmail": EMAIL,
        "password": PASSWORD,
        "ButtonSignIn": "Sign in",
    }
    session.post(f"{BASE}/Login", data=data, allow_redirects=True)


def get_parking_data(session):
    resp = session.get(f"{BASE}/Requests")
    html = resp.text

    idx = html.find("initScript(")
    if idx == -1:
        print("❌ Impossible de trouver les données de parking.")
        return None

    start = idx + len("initScript(")

    bracket_count = 0
    first_array_start = start
    for i in range(start, len(html)):
        if html[i] == "[":
            first_array_start = i
            break

    bracket_count = 0
    first_array_end = first_array_start
    for i in range(first_array_start, len(html)):
        if html[i] == "[":
            bracket_count += 1
        elif html[i] == "]":
            bracket_count -= 1
            if bracket_count == 0:
                first_array_end = i + 1
                break

    second_array_start = first_array_end
    for i in range(first_array_end, len(html)):
        if html[i] == "[":
            second_array_start = i
            break

    bracket_count = 0
    second_array_end = second_array_start
    for i in range(second_array_start, len(html)):
        if html[i] == "[":
            bracket_count += 1
        elif html[i] == "]":
            bracket_count -= 1
            if bracket_count == 0:
                second_array_end = i + 1
                break

    second_arg = html[second_array_start:second_array_end]
    return json.loads(second_arg)


def main():
    missing = []
    if not EMAIL:
        missing.append("SHARVY_EMAIL")
    if not PASSWORD:
        missing.append("SHARVY_PASSWORD")
    if not BASE:
        missing.append("SHARVY_BASE_URL")
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TARGET:
        missing.append("TELEGRAM_TARGET")
    if missing:
        print("❌ Variables d'environnement manquantes :")
        for v in missing:
            print(f"   export {v}=...")
        sys.exit(1)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    session = requests.Session()
    print("🔐 Connexion à Sharvy...")
    login(session)
    print("✅ Connecté.")

    print(f"📅 Recherche des données pour le {today}...")
    data = get_parking_data(session)

    if not data:
        return

    for day in data:
        if day["Date"].startswith(today):
            am_spot = day.get("AmSpotName")
            pm_spot = day.get("PmSpotName")
            am_status = day.get("AmStatus", -1)
            pm_status = day.get("PmStatus", -1)

            date_str = day['Date'][:10]
            day_name = day['ShortDayName']
            am_label = am_spot or "Aucune"
            pm_label = pm_spot or "Aucune"
            am_status_label = STATUS_LABELS.get(am_status, "Inconnu")
            pm_status_label = STATUS_LABELS.get(pm_status, "Inconnu")

            print(f"\n--- Place de parking — {day_name} {date_str} ---")
            print(f"  Matin   : {am_label}  ({am_status_label})")
            print(f"  Après-midi : {pm_label}  ({pm_status_label})")

            has_spot = am_spot or pm_spot
            has_confirmed = am_status == 3 or pm_status == 3

            if has_spot and has_confirmed:
                spot = am_spot or pm_spot
                msg = f"🅿️ Ta place de parking aujourd'hui : *{spot}*"
                send_telegram(msg)
                print("📤 Résultat envoyé sur Telegram.")
            else:
                print("⏭️  Pas de place confirmée — aucun message Telegram envoyé.")
            return

    print("❌ Aucune donnée trouvée pour aujourd'hui.")


if __name__ == "__main__":
    main()
