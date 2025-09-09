# Bitcoin Volume Tracker - Cloud Deployment Guide 🚀

## 📱 NOTIFICATIONS IPHONE AVEC TELEGRAM (GRATUIT)

### Étape 1: Créer un Bot Telegram
1. Ouvrez Telegram sur votre iPhone
2. Cherchez **@BotFather**
3. Envoyez `/newbot`
4. Choisissez un nom (ex: "Bitcoin Volume Alert")
5. Choisissez un username (ex: "MyBTCVolumeBot")
6. **Sauvegardez le token** (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Étape 2: Obtenir votre Chat ID
1. Cherchez **@userinfobot** sur Telegram
2. Envoyez `/start`
3. **Notez votre ID** (format: `123456789`)

### Étape 3: Tester en local
```bash
# Définir les variables
export TELEGRAM_BOT_TOKEN="votre_token_ici"
export TELEGRAM_CHAT_ID="votre_chat_id_ici"

# Lancer
python cloud_tracker.py
```

---

## 🌐 DÉPLOIEMENT GRATUIT 24/7

### **Option 1: GitHub Actions** ⭐ RECOMMANDÉ

**Avantages:** 100% gratuit, fiable, facile

1. **Créer un repo GitHub**
2. **Ajouter le workflow** `.github/workflows/tracker.yml`:

```yaml
name: Bitcoin Volume Tracker

on:
  schedule:
    # Relancer toutes les 5h50 (max 6h par run)
    - cron: '0 */6 * * *'
  workflow_dispatch: # Permet de lancer manuellement

jobs:
  track:
    runs-on: ubuntu-latest
    timeout-minutes: 350  # 5h50min
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install websocket-client requests
    
    - name: Run Tracker
      env:
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      run: |
        python cloud_tracker.py
```

3. **Ajouter les secrets** dans Settings → Secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

4. **Activer Actions** dans l'onglet Actions

---

### **Option 2: Replit.com** 

1. **Créer un compte** sur [replit.com](https://replit.com)
2. **Nouveau Repl** → Python
3. **Copier** `cloud_tracker.py`
4. **Ajouter les secrets** dans l'onglet Secrets
5. **Créer** `requirements.txt`:
```
websocket-client
requests
```
6. **Run** → Le tracker démarre!

**Pour garder actif 24/7:**
- Créer un compte sur [uptimerobot.com](https://uptimerobot.com)
- Ajouter un monitor HTTP(s) avec l'URL de votre Repl
- Check interval: 5 minutes

---

### **Option 3: Railway.app**

1. **Fork le repo** sur GitHub
2. **Connecter à Railway** via GitHub
3. **Ajouter les variables** d'environnement
4. **Deploy** → Automatique!

Budget: $5 crédit gratuit = ~500h/mois

---

### **Option 4: Oracle Cloud** (VPS Gratuit)

**Le plus technique mais 100% gratuit à vie!**

1. **Créer compte** Oracle Cloud (carte requise, non débitée)
2. **Créer une instance** Always Free (ARM 4 CPU, 24GB RAM)
3. **SSH et installer:**
```bash
# Installer Python
sudo apt update
sudo apt install python3-pip tmux

# Cloner le projet
git clone https://github.com/vous/bitcoin-tracker
cd bitcoin-tracker

# Installer dépendances
pip3 install websocket-client requests

# Lancer dans tmux (persiste après déconnexion)
tmux new -s tracker
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
python3 cloud_tracker.py

# Détacher: Ctrl+B puis D
# Rattacher: tmux attach -t tracker
```

---

## 🔧 CONFIGURATION AVANCÉE

### Modifier les seuils d'alerte

Dans `cloud_tracker.py`:
```python
# Alert settings
self.z_threshold = 3.0        # Z-score minimum
self.volume_threshold = 2.0   # Volume multiplier
self.alert_cooldown = 60      # Secondes entre alertes
```

### Ajouter d'autres cryptos

```python
# Changer le symbole
self.symbol = "ethusdt"  # Pour Ethereum
self.ws_url = "wss://fstream.binance.com/ws/ethusdt@aggTrade"
```

---

## 📊 MONITORING

### Dashboard simple
Créez `dashboard.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>BTC Tracker Status</title>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <h1>Bitcoin Volume Tracker</h1>
    <p>Status: 🟢 Running</p>
    <p>Last Update: <span id="time"></span></p>
    <script>
        document.getElementById('time').innerText = new Date().toLocaleString();
    </script>
</body>
</html>
```

---

## 🚨 EXEMPLES D'ALERTES

### Alert Volume
```
🚨 HIGH VOLUME ALERT 🚨

📊 Bitcoin: $98,453.21
📈 Volume (3s): $450,000
📉 Avg (60s): $85,000
⚡ Ratio: 5.3x
📐 Z-Score: 4.2

🕐 Time: 14:32:15
```

### Alert Whale
```
🐋 WHALE DETECTED 🐋

💰 Large Volume: $2,500,000
📊 Price: $98,500.00
📐 Z-Score: 8.5

🕐 Time: 14:35:22
```

---

## 🎯 CHECKLIST DÉPLOIEMENT

- [ ] Bot Telegram créé
- [ ] Token et Chat ID obtenus
- [ ] Test en local réussi
- [ ] Plateforme cloud choisie
- [ ] Variables d'environnement configurées
- [ ] Déploiement effectué
- [ ] Première notification reçue
- [ ] Monitoring actif

---

## 💡 TIPS

1. **Batterie iPhone**: Activez les notifications Telegram mais désactivez les sons pour économiser
2. **Multi-alertes**: Créez plusieurs bots pour différents seuils
3. **Logs**: Gardez les logs sur la plateforme cloud pour debug
4. **Sécurité**: Ne partagez jamais vos tokens!

---

## 🆘 SUPPORT

### Problème: Pas de notifications
- Vérifiez que le bot est dans votre chat
- Testez avec `/start` au bot
- Vérifiez les tokens

### Problème: Tracker s'arrête
- GitHub Actions: Vérifier les logs dans l'onglet Actions
- Replit: Vérifier UptimeRobot
- Railway: Vérifier les crédits restants

---

**Profitez de vos alertes Bitcoin 24/7 sur iPhone! 📱🚀**
