
from flask import Flask, render_template, request, jsonify, url_for
import os
from pathlib import Path
from werkzeug.utils import secure_filename
import json
from music_analyzer_pro import analyze_track_pro
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'm4a', 'flac'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/analysis_images', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Geen bestand geüpload'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Geen bestand geselecteerd'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            result = analyze_track_pro(filepath, visualize=False, export=False)
            
            import librosa
            y, sr = librosa.load(filepath, sr=44100)
            energy = np.array(result['energy'])
            peak_times = np.array(result['peaks'])
            img_path = create_visualization_pro(
                y, sr, energy, peak_times, filename, 
                result['bpm'], result['key'], result.get('mode', 'major'),
                result.get('camelot', ''), result.get('phrases', {})
            )
            
            result['visualization'] = url_for('static', filename=f'analysis_images/{Path(img_path).name}')
            result['filename'] = filename
            
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'Fout bij analyseren: {str(e)}'}), 500
    
    return jsonify({'error': 'Ongeldig bestandsformaat'}), 400


def create_visualization_pro(y, sr, energy, peak_times, filename, bpm, key, mode='major', camelot='', phrases=None):
    x_energy = np.linspace(0, len(y)/sr, len(energy))
    time_axis = np.linspace(0, len(y)/sr, len(y))
    
    # Maak 3 subplots: Waveform, Combined, Energy
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.5, 2, 1], hspace=0.3)
    
    # Plot 1: Duidelijke Waveform
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(time_axis, y, color='#4A90E2', linewidth=0.8, alpha=0.9)
    ax1.fill_between(time_axis, y, 0, alpha=0.3, color='#4A90E2')
    ax1.set_ylabel('Amplitude', fontsize=12, fontweight='bold')
    ax1.set_title('Waveform', fontsize=13, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(0, len(y)/sr)
    ax1.axhline(y=0, color='black', linewidth=0.5, alpha=0.3)
    
    # Plot 2: Combined view met waveform, energy en peaks
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(time_axis, y, alpha=0.4, color='#4A90E2', linewidth=0.6, label='Waveform')
    ax2.plot(x_energy, energy, color='#E24A4A', linewidth=2, label='Energy', zorder=3)
    ax2.scatter(peak_times, [np.max(energy)*0.6]*len(peak_times), color='#50C878', s=50, zorder=5, label='Peaks', alpha=0.8, marker='v')
    
    if phrases:
        colors = {'intro': '#FFD700', 'verse': '#87CEEB', 'chorus': '#FF6B6B', 'outro': '#9370DB'}
        for phrase_type, segments in phrases.items():
            for start, end in segments:
                ax2.axvspan(start, end, alpha=0.15, color=colors.get(phrase_type, 'gray'))
    
    title = f'{Path(filename).stem} | BPM: {bpm} | Key: {key} {mode}'
    if camelot:
        title += f' | Camelot: {camelot}'
    ax2.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Amplitude / Energy', fontsize=12)
    ax2.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Energy detail
    ax3 = fig.add_subplot(gs[2])
    ax3.fill_between(x_energy, energy, alpha=0.6, color='#E24A4A')
    ax3.plot(x_energy, energy, color='#E24A4A', linewidth=2)
    ax3.set_xlabel('Time (s)', fontsize=12)
    ax3.set_ylabel('Energy', fontsize=12, fontweight='bold')
    ax3.set_title('Energy Detail', fontsize=13, fontweight='bold', pad=10)
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    img_filename = f"{Path(filename).stem}_pro_analysis.png"
    img_path = os.path.join('static/analysis_images', img_filename)
    plt.savefig(img_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return img_path


if __name__ == '__main__':
    port = 5001
    print("\n" + "="*50)
    print("🎵 Music Analyzer Web Interface")
    print("="*50)
    print(f"Open je browser en ga naar: http://localhost:{port}")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=port)

