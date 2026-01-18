# Music Analyzer - Vercel Deployment

Deze applicatie is geoptimaliseerd voor deployment op Vercel als serverless functions.

## 🚀 Deployment op Vercel

### Vereisten
- Vercel account (gratis tier is voldoende)
- Vercel CLI geïnstalleerd (`npm i -g vercel`)

### Stappen

1. **Login bij Vercel**
   ```bash
   vercel login
   ```

2. **Deploy de applicatie**
   ```bash
   vercel
   ```

3. **Voor productie deployment**
   ```bash
   vercel --prod
   ```

## 📦 Optimalisaties voor Vercel

### Bestandsgrootte
- **Onnodige dependencies verwijderd**: Flask is niet nodig (alleen werkzeug)
- **Pydub verwijderd**: Niet nodig als we alleen librosa gebruiken
- **Specifieke versies**: Vaste versies voor betere caching

### Bestandsopslag
- **Tijdelijke opslag**: Bestanden worden opgeslagen in `/tmp` (beschikbaar in Vercel serverless)
- **Geen permanente opslag**: Uploads worden automatisch verwijderd na verwerking
- **Images als base64**: Visualisaties worden als base64 data URI teruggestuurd (geen file storage nodig)

### Serverless Optimalisaties
- **Max duration**: 60 seconden (configureerbaar in `vercel.json`)
- **Memory efficient**: Images worden in-memory gegenereerd
- **CORS headers**: Automatisch geconfigureerd

## ⚙️ Configuratie

### vercel.json
- Routes geconfigureerd voor `/` en `/upload`
- Max duration: 60 seconden (voor lange audio analyses)
- Static files worden geserveerd via `/static/*`

### .vercelignore
- Uploads folder wordt genegeerd
- Audio bestanden worden niet geüpload
- Analysis images worden niet geüpload (worden in-memory gegenereerd)

## 🔧 Lokale Development

Voor lokale development kun je nog steeds de originele Flask app gebruiken:

```bash
python app.py
```

De applicatie draait dan op `http://localhost:5001`

## 📝 Notities

- **Audio bestanden**: Maximaal 500MB (configureerbaar in code)
- **Processing tijd**: Kan tot 60 seconden duren voor lange tracks
- **Memory**: Vercel serverless functions hebben beperkte memory, grote bestanden kunnen problemen geven

## 🐛 Troubleshooting

### "Function timeout"
- Verhoog `maxDuration` in `vercel.json` (max 60s op free tier)
- Overweeg Pro tier voor langere timeouts

### "Memory limit exceeded"
- Audio bestanden zijn mogelijk te groot
- Overweeg bestandscompressie of kleinere sample rates

### "Module not found"
- Controleer of alle dependencies in `requirements.txt` staan
- Vercel installeert automatisch dependencies tijdens build

## 📊 Kosten

De applicatie is geoptimaliseerd om kosten laag te houden:
- Geen permanente storage nodig
- Geen database nodig
- Alleen serverless function invocations
- Gratis tier: 100GB bandwidth, 100GB-hours function execution



