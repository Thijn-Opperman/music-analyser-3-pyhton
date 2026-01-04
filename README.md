# Music Analyzer 3

Een Python tool om audio tracks te analyseren voor BPM, key, energie en peaks.

## ✅ Wat is al gedaan (automatisch)

- ✅ Python versie gecontroleerd (3.9.6)
- ✅ Alle dependencies geïnstalleerd (librosa, numpy, scipy, matplotlib, pydub, flask)
- ✅ Code geschreven en klaar voor gebruik
- ✅ **Web UI gebouwd** - Moderne interface om tracks te uploaden en analyseren!

## 🚀 Snelstart: Web Interface (Aanbevolen!)

**Start de web server:**
```bash
python3 app.py
```

**Open je browser:**
```
http://localhost:5000
```

**Gebruik:**
1. Sleep een audio bestand naar de upload zone (of klik om te selecteren)
2. Klik op "Analyseer Track"
3. Bekijk direct de resultaten: BPM, Key, Duur, Peaks en visualisatie!

De web interface heeft:
- ✨ Moderne, gebruiksvriendelijke UI
- 📁 Drag & drop bestand upload
- 📊 Live resultaten met visualisatie
- 🎨 Mooie statistieken cards

## 📋 Command Line Gebruik (Alternatief)

### Stap 1: Audio bestanden toevoegen

Je hebt twee opties:

**Optie A: Analyseer één track**
- Plaats je audio bestand (mp3, wav, m4a, flac) in de project folder
- Bijvoorbeeld: `track1.mp3` in `/Users/thijnopperman/Documents/GitHub/music-analyser-3-pyhton/`

**Optie B: Batch analyse van meerdere tracks**
- Maak een folder aan genaamd `tracks/` in de project folder
- Plaats alle audio bestanden in deze folder

### Stap 2: Run de analyzer

**Voor één track:**
```bash
python3 music_analyzer.py track1.mp3
```

**Voor batch analyse:**
```bash
python3 music_analyzer.py --batch tracks/
```

### Stap 3: Bekijk de resultaten

Na de analyse krijg je:
- **Visualisatie**: Een PNG bestand met waveform, energie en peaks (bijv. `track1_analysis.png`)
- **JSON data**: Een JSON bestand met alle analyse data (bijv. `track1_analysis.json` of `all_tracks.json`)

## 📁 Project structuur

```
music-analyser-3-pyhton/
├── app.py                # Flask web applicatie (START DIT!)
├── music_analyzer.py     # Hoofdscript (analyse functies)
├── requirements.txt      # Dependencies (al geïnstalleerd)
├── example_usage.py      # Voorbeelden
├── README.md            # Deze file
├── templates/           # HTML templates
│   └── index.html      # Web interface
├── static/             # Static files
│   └── analysis_images/ # Opgeslagen visualisaties
└── uploads/            # Geüploade bestanden
```

## 🎵 Ondersteunde formaten

- MP3
- WAV
- M4A
- FLAC

## 📊 Wat wordt geanalyseerd?

- **BPM**: Beats per minute
- **Key**: Toonsoort (C, C#, D, etc.)
- **Energy**: Energie curve (0-1)
- **Peaks**: Tijden waar energie pieken voorkomen

## 💻 Alternatief: Gebruik in Python code

```python
from music_analyzer import analyze_track, batch_analyze

# Analyseer één track
result = analyze_track("track1.mp3")

# Batch analyse
results = batch_analyze("tracks/")
```

## ⚙️ Aanpassingen

Je kunt parameters aanpassen in de functie calls:

```python
# Met aangepaste drempel voor peaks
analyze_track("track1.mp3", energy_threshold=0.7)

# Zonder visualisatie
analyze_track("track1.mp3", visualize=False)

# Zonder export
analyze_track("track1.mp3", export=False)
```

## 🐛 Troubleshooting

**Probleem**: "FileNotFoundError" of "No such file or directory"
- **Oplossing**: Controleer of het audio bestand in de juiste folder staat

**Probleem**: "No module named 'librosa'"
- **Oplossing**: Run `pip3 install -r requirements.txt` opnieuw

**Probleem**: Audio laadt niet
- **Oplossing**: Controleer of het bestand een ondersteund formaat heeft (mp3, wav, m4a, flac)

