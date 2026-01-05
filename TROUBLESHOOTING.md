# 🔧 Troubleshooting - Links Werken Niet

## ❌ Probleem: Links/URLs werken niet op Railway

### Stap 1: Check Railway Logs

1. Ga naar Railway dashboard
2. Klik op je **service**
3. Ga naar **"Deployments"** tab
4. Klik op de meest recente deployment
5. Bekijk de **logs** - zoek naar errors

### Veelvoorkomende Problemen:

#### 1. "Module not found" of Import Errors
**Oplossing:**
- Check of alle dependencies in `requirements.txt` staan
- Railway installeert automatisch, maar soms duurt het lang
- Wacht 3-5 minuten en refresh

#### 2. "Port already in use" of "Address already in use"
**Oplossing:**
- Railway zet automatisch de `PORT` environment variable
- De app gebruikt deze automatisch
- Check in logs of `PORT` is gezet

#### 3. "Template not found" of "Static files not found"
**Oplossing:**
- Zorg dat `templates/` en `static/` folders in je repository staan
- Check `.gitignore` - deze folders mogen niet genegeerd worden

#### 4. App start niet
**Oplossing:**
- Check de **Start Command** in Railway Settings
- Moet zijn: `gunicorn --bind 0.0.0.0:$PORT app:app`
- Of: `python app.py` (als fallback)

### Stap 2: Test de Health Endpoint

Je app heeft een health check endpoint:
```
https://jouw-url.up.railway.app/health
```

Als dit werkt, draait je app! Als dit niet werkt, check de logs.

### Stap 3: Test de Hoofdpagina

```
https://jouw-url.up.railway.app/
```

Dit zou de upload pagina moeten tonen.

### Stap 4: Check Environment Variables

In Railway dashboard → Service → Settings → Variables:
- `PORT` - wordt automatisch gezet door Railway
- Optioneel: `FLASK_ENV=production`

### Stap 5: Rebuild

Soms helpt een rebuild:
1. Railway dashboard → Service → Settings
2. Scroll naar beneden
3. Klik "Redeploy" of "Deploy Latest Commit"

## 🔍 Debug Checklist

- [ ] App start zonder errors in logs?
- [ ] Health endpoint (`/health`) werkt?
- [ ] Hoofdpagina (`/`) laadt?
- [ ] Static files worden geladen? (check browser console)
- [ ] Templates worden gevonden?

## 📝 Test Lokaal Eerst

Test de app lokaal voordat je deployt:

```bash
# Installeer dependencies
pip install -r requirements.txt

# Start de app
python app.py

# Of met gunicorn
gunicorn --bind 0.0.0.0:5001 app:app
```

Als het lokaal werkt, werkt het ook op Railway!

## 🆘 Nog Steeds Problemen?

1. **Check Railway Status**: [status.railway.app](https://status.railway.app)
2. **Bekijk Logs**: Service → Deployments → Logs
3. **Test Health Endpoint**: `/health` moet `{"status":"ok"}` returnen
4. **Check Browser Console**: F12 → Console voor JavaScript errors

---

**Meestal is het probleem:**
- App is nog aan het builden (wacht 2-5 minuten)
- Dependencies installeren duurt lang
- Check de logs voor specifieke errors

