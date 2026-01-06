"""
Lokale Flask app voor het testen van de vereenvoudigde Music Analyzer
"""
from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from music_analyzer_simple import analyze_track_simple

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'm4a', 'flac'}

# Maak uploads directory aan
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


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
            # Analyseer track (vereenvoudigd - alleen songnaam, BPM, key, duur)
            result = analyze_track_simple(filepath)
            
            # Verwijder bestand na analyse
            os.remove(filepath)
            
            return jsonify(result)
        except Exception as e:
            # Verwijder bestand bij error
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'error': f'Fout bij analyseren: {str(e)}'}), 500
    
    return jsonify({'error': 'Ongeldig bestandsformaat'}), 400


if __name__ == '__main__':
    port = 5001
    print("\n" + "="*50)
    print("🎵 Music Analyzer - Vereenvoudigde Versie")
    print("="*50)
    print(f"Open je browser en ga naar: http://localhost:{port}")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=port)

