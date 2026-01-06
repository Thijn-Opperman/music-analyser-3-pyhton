# Music Analyzer - Vereenvoudigde Versie

Deze applicatie analyseert muziekbestanden en retourneert alleen de essentiële informatie:
- **Songnaam** (zonder extensie)
- **BPM** (Beats Per Minute)
- **Key** (Toonsoort, bijv. "C major" of "A minor")
- **Duur** (in seconden)

## Project Structuur

```
project/
├── api/
│   ├── index.py          # Vercel serverless function
│   └── vercel.json       # Configuratie voor api route
├── templates/
│   └── index.html        # Frontend UI
├── music_analyzer_simple.py  # Vereenvoudigde analyzer
├── requirements.txt      # Python dependencies
├── vercel.json          # Hoofd Vercel configuratie
└── runtime.txt          # Python runtime versie (indien nodig)
```

## Dependencies

- `librosa==0.10.1` - Audio analyse
- `numpy==1.24.3` - Numerieke berekeningen
- `scipy==1.11.4` - Wetenschappelijke berekeningen
- `werkzeug==3.0.1` - HTTP utilities

## Setup voor Vercel

1. **Installeer Vercel CLI** (optioneel):
   ```bash
   npm i -g vercel
   ```

2. **Deploy naar Vercel**:
   ```bash
   vercel
   ```

3. **Of push naar GitHub en koppel aan Vercel**:
   - Ga naar vercel.com
   - Import je repository
   - Vercel detecteert automatisch de configuratie

## API Endpoints

### GET `/`
Serveert de web interface (HTML)

### POST `/upload`
Upload en analyseert een audio bestand

**Request:**
- Content-Type: `multipart/form-data`
- Form field: `file` (audio bestand: mp3, wav, m4a, flac)

**Response:**
```json
{
  "songnaam": "My Track",
  "bpm": 128,
  "key": "C major",
  "duration": 245.5
}
```

## Lokaal Testen

Voor lokaal testen kun je een simpele Flask app gebruiken:

```python
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from music_analyzer_simple import analyze_track_simple

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Geen bestand'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Geen bestand geselecteerd'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        result = analyze_track_simple(filepath)
        os.remove(filepath)  # Cleanup
        return jsonify(result)
    except Exception as e:
        os.remove(filepath)  # Cleanup
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Functies

### `analyze_track_simple(filename, sample_rate=44100)`

Analyseert een audio bestand en retourneert alleen de essentiële data.

**Parameters:**
- `filename` (str): Pad naar audio bestand
- `sample_rate` (int, optioneel): Sample rate (default: 44100)

**Returns:**
```python
{
    "songnaam": str,    # Bestandsnaam zonder extensie
    "bpm": int,         # BPM waarde
    "key": str,         # Key + mode (bijv. "C major")
    "duration": float   # Duur in seconden
}
```

## Opmerkingen

- De applicatie gebruikt `/tmp` directory in Vercel voor tijdelijke bestandsopslag
- Audio bestanden worden direct na analyse verwijderd
- Geen visualisaties of extra data wordt opgeslagen
- Maximale functie duur: 60 seconden (configureerbaar in vercel.json)

