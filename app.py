"""
Flask Web Application voor Music Analyzer
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, url_for
import os
from pathlib import Path
from werkzeug.utils import secure_filename
import json
from music_analyzer_pro import analyze_track_pro
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)

# Gebruik /tmp op Vercel (serverless), anders 'uploads'
UPLOAD_BASE = '/tmp' if os.environ.get('VERCEL') else os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(UPLOAD_BASE, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'm4a', 'flac'}

# Maak uploads folder aan
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Voor static images, gebruik /tmp op Vercel
STATIC_IMAGES_BASE = '/tmp' if os.environ.get('VERCEL') else os.path.dirname(os.path.abspath(__file__))
static_images_dir = os.path.join(STATIC_IMAGES_BASE, 'static', 'analysis_images')
os.makedirs(static_images_dir, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Hoofdpagina met upload formulier"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload en start analyse"""
    if 'file' not in request.files:
        return jsonify({'error': 'Geen bestand geüpload'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Geen bestand geselecteerd'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Start PRO analyse
        try:
            result = analyze_track_pro(
                filepath, 
                visualize=False,  # We maken onze eigen visualisatie
                export=False
            )
            
            # Maak visualisatie
            import librosa
            y, sr = librosa.load(filepath, sr=44100)
            energy = np.array(result['energy'])
            peak_times = np.array(result['peaks'])
            
            # Genereer visualisatie met nieuwe data
            img_path = create_visualization_pro(
                y, sr, energy, peak_times, filename, 
                result['bpm'], result['key'], result.get('mode', 'major'),
                result.get('camelot', ''), result.get('phrases', {})
            )
            
            # Genereer URL voor visualisatie
            if os.environ.get('VERCEL'):
                # Op Vercel: gebruik een speciale route om images te serveren
                result['visualization'] = url_for('serve_image', filename=Path(img_path).name)
            else:
                # Lokaal: gebruik static folder
                result['visualization'] = url_for('static', filename=f'analysis_images/{Path(img_path).name}')
            result['filename'] = filename
            
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'Fout bij analyseren: {str(e)}'}), 500
    
    return jsonify({'error': 'Ongeldig bestandsformaat'}), 400


def create_visualization_pro(y, sr, energy, peak_times, filename, bpm, key, mode='major', camelot='', phrases=None):
    """Maak verbeterde visualisatie met alle PRO features"""
    x_energy = np.linspace(0, len(y)/sr, len(energy))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[2, 1])
    
    # Bovenste plot: Waveform en energie
    ax1.plot(np.linspace(0, len(y)/sr, len(y)), y, alpha=0.3, color='#4A90E2', linewidth=0.5, label='Waveform')
    ax1.plot(x_energy, energy, color='#E24A4A', linewidth=1.5, label='Energy')
    ax1.scatter(peak_times, [0.5]*len(peak_times), color='#50C878', s=30, zorder=5, label='Peaks', alpha=0.7)
    
    # Markeer phrases als beschikbaar
    if phrases:
        colors = {'intro': '#FFD700', 'verse': '#87CEEB', 'chorus': '#FF6B6B', 'outro': '#9370DB'}
        for phrase_type, segments in phrases.items():
            for start, end in segments:
                ax1.axvspan(start, end, alpha=0.2, color=colors.get(phrase_type, 'gray'))
    
    title = f'{Path(filename).stem} | BPM: {bpm} | Key: {key} {mode}'
    if camelot:
        title += f' | Camelot: {camelot}'
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Amplitude / Energy', fontsize=12)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Onderste plot: Energie detail
    ax2.fill_between(x_energy, energy, alpha=0.5, color='#E24A4A')
    ax2.plot(x_energy, energy, color='#E24A4A', linewidth=1.5)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Energy', fontsize=12)
    ax2.set_title('Energy Detail', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Sla op
    img_filename = f"{Path(filename).stem}_pro_analysis.png"
    STATIC_IMAGES_BASE = '/tmp' if os.environ.get('VERCEL') else os.path.dirname(os.path.abspath(__file__))
    static_images_dir = os.path.join(STATIC_IMAGES_BASE, 'static', 'analysis_images')
    os.makedirs(static_images_dir, exist_ok=True)
    img_path = os.path.join(static_images_dir, img_filename)
    plt.savefig(img_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return img_path


@app.route('/image/<filename>')
def serve_image(filename):
    """Serve images from /tmp op Vercel"""
    if os.environ.get('VERCEL'):
        STATIC_IMAGES_BASE = '/tmp'
        img_path = os.path.join(STATIC_IMAGES_BASE, 'static', 'analysis_images', filename)
        if os.path.exists(img_path):
            return send_file(img_path, mimetype='image/png')
        return jsonify({'error': 'Image not found'}), 404
    else:
        # Lokaal: gebruik normale static route
        return send_from_directory('static/analysis_images', filename)


@app.route('/results')
def results():
    """Resultaten pagina"""
    return render_template('results.html')


@app.route('/api/tracks', methods=['GET'])
def get_tracks():
    """Haal alle geanalyseerde tracks op"""
    results = []
    uploads_dir = Path(app.config['UPLOAD_FOLDER'])
    
    # Zoek alle JSON bestanden (als we die opslaan)
    json_files = list(Path('.').glob('*_analysis.json'))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                # Voeg visualisatie pad toe als het bestaat
                img_name = f"{Path(json_file).stem.replace('_analysis', '')}_analysis.png"
                img_path = Path('static/analysis_images') / img_name
                if img_path.exists():
                    data['visualization'] = url_for('static', filename=f'analysis_images/{img_name}')
                results.append(data)
        except:
            continue
    
    return jsonify(results)


if __name__ == '__main__':
    port = 5001  # Gebruik 5001 omdat 5000 vaak door AirPlay wordt gebruikt op macOS
    print("\n" + "="*50)
    print("🎵 Music Analyzer Web Interface")
    print("="*50)
    print(f"Open je browser en ga naar: http://localhost:{port}")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=port)

