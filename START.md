# 🚀 Hoe start je dit project?

## Snelle start (Python equivalent van `npm run dev`)

### Optie 1: Gebruik het start script
```bash
./run_dev.sh
```

### Optie 2: Direct met Python
```bash
python3 app.py
```

Of als `python` werkt:
```bash
python app.py
```

## Stap-voor-stap

### 1. Installeer dependencies (als je dat nog niet gedaan hebt)
```bash
pip3 install -r requirements.txt
```

Of handmatig:
```bash
pip3 install Flask librosa numpy scipy werkzeug mutagen matplotlib
```

### 2. Start de server
```bash
python3 app.py
```

### 3. Open in browser
De server draait op: **http://localhost:5001**

## Wat gebeurt er?

- De Flask web server start op poort 5001
- Je kunt de web interface openen in je browser
- Audio bestanden uploaden via de web interface
- Resultaten zien (BPM, Key, Duur, etc.)

## Stoppen

Druk op `Ctrl+C` in de terminal om de server te stoppen.

## Troubleshooting

**Probleem:** `python3: command not found`  
**Oplossing:** Gebruik `python` in plaats van `python3`

**Probleem:** `ModuleNotFoundError: No module named 'flask'`  
**Oplossing:** Installeer dependencies: `pip3 install -r requirements.txt`

**Probleem:** Port 5001 is al in gebruik  
**Oplossing:** Wijzig de poort in `app.py` regel 107

## Verschil met Node.js

In Python:
- ✅ `python3 app.py` = Start de app
- ❌ Geen `npm run dev` nodig
- ❌ Geen `package.json` nodig

## Andere opties

### Test alleen de standalone analyzer (geen web server)
```bash
python3 music_analyzer_standalone.py track.mp3
```

### Test de eenvoudige app
```bash
python3 app_simple.py
```
