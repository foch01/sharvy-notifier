# Sharvy Parking Notifier

Récupère automatiquement ta place de parking attribuée sur **Sharvy** et t'envoie une notification Telegram chaque matin.

## Prérequis

- Python 3.8+
- Un compte [Sharvy](https://app.sharvy.com/)
- Un bot Telegram (crée-le avec [@BotFather](https://t.me/BotFather) sur Telegram)

## Installation

```bash
git clone https://github.com/foch01/sharvy-notifier.git
cd sharvy-notifier
pip install -r requirements.txt
```

## Configuration

Crée un fichier `.env` ou exporte ces variables d'environnement :

```bash
export SHARVY_EMAIL="ton@email.com"
export SHARVY_PASSWORD="ton_mot_de_passe"
export SHARVY_BASE_URL="https://app.sharvy.com/ton-espace"
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
export TELEGRAM_TARGET="123456789"
```

## Utilisation

```bash
python3 sharvy_parking.py
```

Le script :

1. Se connecte à Sharvy avec tes identifiants
2. Récupère les données de parking du jour
3. Si une place est attribuée et confirmée, envoie une notification Telegram avec le nom de la place
4. Sinon, affiche dans la console qu'aucune place confirmée n'a été trouvée

## Notifications Telegram

Le script utilise l'API Telegram directement. Crée un bot via [@BotFather](https://t.me/BotFather) pour obtenir un token, puis définis-le dans `TELEGRAM_BOT_TOKEN`.

Le message est envoyé au destinataire configuré via la variable `TELEGRAM_TARGET` (ton ID Telegram).

## Statuts des places

| Code | Signification |
|------|---------------|
| 0 | Pas de demande |
| 1 | Place non attribuée / demande en attente |
| 2 | Demande en cours |
| 3 | Place attribuée et confirmée |
| 4 | Gérée par un service externe |
| 5 | Jour passé / non travaillé |

## Licence

MIT
