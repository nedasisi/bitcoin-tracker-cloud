# Bitcoin Volume Tracker Cloud ☁️ 🚀

Tracker Bitcoin 24/7 avec notifications iPhone via Telegram.

## 🎯 Features

- ✅ Monitoring 24/7 du volume Bitcoin
- 📱 Notifications instantanées sur iPhone (Telegram)
- 🐋 Détection des whales
- 📊 Analyse Z-score et OBI
- 🆓 100% Gratuit (GitHub Actions)

## 🚀 Quick Start

### 1. Fork ce repo

Cliquez sur "Fork" en haut à droite

### 2. Configurez Telegram

1. Créez un bot avec [@BotFather](https://t.me/botfather)
2. Obtenez votre Chat ID avec [@userinfobot](https://t.me/userinfobot)

### 3. Ajoutez les Secrets

Dans votre fork : Settings → Secrets → Actions

- `TELEGRAM_BOT_TOKEN` : Votre token bot
- `TELEGRAM_CHAT_ID` : Votre chat ID

### 4. Activez GitHub Actions

Actions → Enable Actions

### 5. Lancez manuellement

Actions → Bitcoin Volume Tracker → Run workflow

## ⚙️ Configuration

Modifiez `cloud_tracker.py` :

```python
self.z_threshold = 3.0        # Seuil Z-score
self.volume_threshold = 2.0   # Multiplicateur volume
self.alert_cooldown = 60      # Cooldown entre alertes
```

## 📱 Notifications

### Volume Alert
```
🚨 HIGH VOLUME ALERT
Bitcoin: $98,453
Volume: $450,000
Z-Score: 4.2
```

### Whale Alert
```
🐋 WHALE DETECTED
Large Volume: $2,500,000
```

## 📊 Monitoring

Le tracker tourne 24/7 et redémarre automatiquement toutes les 6h.

## 📝 License

MIT

## 🤝 Support

Créez une Issue si vous avez des problèmes.

---
*Powered by GitHub Actions* ⚡
