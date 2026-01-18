# 🎵 Music Analyzer

Een professionele muziekanalyse tool die audio tracks analyseert en BPM, Key, Energy, Peaks en Waveform visualisaties genereert.

## ✨ Features

- 🎯 **BPM Detectie** - Multi-tempo analyse met ~90-95% nauwkeurigheid
- 🎹 **Key Detectie** - Krumhansl-Schmuckler algoritme (majeur/minor) met ~80-90% nauwkeurigheid
- 🎵 **Camelot Wheel** - Rekordbox-achtige notatie voor DJ mixing
- 📊 **Waveform Visualisatie** - Duidelijke waveform, energy en peaks
- 🎼 **Phrase Detectie** - Automatische detectie van intro, verse, chorus, outro
- 📈 **Energy Analyse** - RMS energie berekening en peak detectie

## 🚀 Quick Start

### Web Interface (Aanbevolen)

```bash
# Installeer dependencies
pip install -r requirements.txt

# Start de applicatie
python app.py

# Open in browser: http://localhost:5001
```

### Standalone Versie

Voor gebruik in andere projecten:

```bash
pip install -r requirements_standalone.txt
```

```python
from music_analyzer_standalone import analyze_audio

result = analyze_audio('track.mp3')
print(f"BPM: {result['bpm']}")
print(f"Key: {result['key_full']}")
```

Zie [README_STANDALONE.md](README_STANDALONE.md) voor meer details.

### Command Line

```bash
# Analyseer één track
python music_analyzer_pro.py track.mp3

# Standalone versie
python music_analyzer_standalone.py track.mp3
```

## 📁 Project Structuur

```
music-analyser-3-pyhton/
├── app.py                      # Flask web applicatie (hoofdapp)
├── music_analyzer_pro.py       # Pro analyzer met alle features
├── music_analyzer_standalone.py # Standalone versie voor import
├── templates/
│   └── index.html              # Web interface
├── static/
│   └── analysis_images/        # Gegenereerde visualisaties
├── uploads/                     # Tijdelijke uploads
├── requirements.txt            # Dependencies voor web app
├── requirements_standalone.txt # Dependencies voor standalone
├── README.md                   # Dit bestand
├── README_STANDALONE.md        # Standalone documentatie
├── START.md                    # Start instructies
└── ACCURACY.md                 # Nauwkeurigheid documentatie
```

## 📊 Nauwkeurigheid

- **BPM**: ~90-95% (vergelijkbaar met Rekordbox/Serato)
- **Key**: ~80-90% (vergelijkbaar met Mixed In Key)
- **Duur/Bitrate/Waveform**: 100% (direct uit audio/metadata)

Zie [ACCURACY.md](ACCURACY.md) voor gedetailleerde informatie.

## 🛠️ Dependencies

### Web App
- `librosa` - Audio analyse
- `numpy`, `scipy` - Numerieke berekeningen
- `Flask` - Web framework
- `matplotlib` - Visualisaties

### Standalone
- `librosa` - Audio analyse
- `numpy` - Numerieke berekeningen
- `mutagen` - Metadata extractie

## 📝 Gebruik

### Web Interface

1. Start de applicatie: `python app.py`
2. Open `http://localhost:5001` in je browser
3. Upload een audio bestand (MP3, WAV, M4A, FLAC)
4. Bekijk de analyse resultaten en waveform visualisatie

### Python API

```python
from music_analyzer_pro import analyze_track_pro

# Volledige analyse met visualisatie
result = analyze_track_pro('track.mp3', visualize=True, export=True)

print(f"BPM: {result['bpm']}")
print(f"Key: {result['key']} {result['mode']}")
print(f"Camelot: {result['camelot']}")
```

## 🎯 Ondersteunde Formaten

- MP3
- WAV
- M4A
- FLAC

## 📚 Documentatie

- [START.md](START.md) - Start instructies
- [README_STANDALONE.md](README_STANDALONE.md) - Standalone versie documentatie
- [ACCURACY.md](ACCURACY.md) - Nauwkeurigheid en testresultaten

## 🔧 Development

```bash
# Development server starten
python app.py

# Of gebruik het script
./run_dev.sh
```

## 📄 Licentie

Open source - vrij te gebruiken en aan te passen.

## 🙏 Credits

- Gebruikt `librosa` voor audio analyse
- Krumhansl-Schmuckler algoritme voor key detectie
- Geïnspireerd door Rekordbox en Mixed In Key
