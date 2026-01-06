# 🚀 Hoe start je de applicatie?

Er zijn twee manieren om de applicatie te gebruiken:
1. **Lokaal testen** (voor development)
2. **Deployen naar Vercel** (voor productie)

---

## 📍 Optie 1: Lokaal testen

### Stap 1: Installeer dependencies

Eerst moet je de Python dependencies installeren:

```bash
# Installeer Flask voor lokale ontwikkeling (als dat nog niet gebeurd is)
pip install Flask

# Installeer alle andere dependencies
pip install -r requirements.txt
```

### Stap 2: Start de applicatie

```bash
python app_simple.py
```

### Stap 3: Open in browser

De applicatie draait nu op: **http://localhost:5000**

Je kunt nu:
- Audio bestanden uploaden via de web interface
- Zie de analyse resultaten (songnaam, BPM, key, duur)

---

## ☁️ Optie 2: Deployen naar Vercel (Productie)

### Stap 1: Installeer Vercel CLI

```bash
npm install -g vercel
```

### Stap 2: Login bij Vercel

```bash
vercel login
```

### Stap 3: Deploy naar Vercel

```bash
# Test deployment
vercel

# Productie deployment
vercel --prod
```

### Stap 4: Open je applicatie

Na deployment krijg je een URL (bijv. `https://jouw-app.vercel.app`)

---

## 🔧 Troubleshooting

### Probleem: "ModuleNotFoundError: No module named 'Flask'"
**Oplossing**: Installeer Flask
```bash
pip install Flask
```

### Probleem: "ModuleNotFoundError: No module named 'librosa'"
**Oplossing**: Installeer alle dependencies
```bash
pip install -r requirements.txt
```

### Probleem: Port al in gebruik
**Oplossing**: Wijzig de poort in `app_simple.py` (regel 52)

### Probleem: Audio bestand niet geladen
**Oplossing**: Controleer of het bestand een ondersteund formaat heeft:
- MP3
- WAV
- M4A
- FLAC

---

## 📝 Snel overzicht

### Lokaal:
```bash
pip install Flask -r requirements.txt
python app_simple.py
# Open http://localhost:5000
```

### Vercel:
```bash
vercel login
vercel --prod
# Open de URL die Vercel geeft
```

---

## 🎵 Testen met een audio bestand

1. Start de applicatie (lokaal of op Vercel)
2. Sleep een audio bestand in het upload gebied
3. Klik op "Analyseer Track"
4. Wacht op de resultaten (kan even duren bij lange tracks)
5. Zie: Songnaam, BPM, Key en Duur

