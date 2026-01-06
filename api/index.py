"""
Vercel serverless function voor Music Analyzer
"""
import os
import sys
import json
import base64
import tempfile
from pathlib import Path
from io import BytesIO

# Voeg parent directory toe aan Python path voor imports
# Dit is nodig omdat api/index.py in een subdirectory staat
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from werkzeug.utils import secure_filename
from music_analyzer_pro import analyze_track_pro
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import librosa

# Laad HTML template
def load_template():
    template_path = Path(__file__).parent.parent / 'templates' / 'index.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def allowed_file(filename):
    allowed_extensions = {'mp3', 'wav', 'm4a', 'flac'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_visualization_pro_base64(y, sr, energy, peak_times, filename, bpm, key, mode='major', camelot='', phrases=None):
    """Maak visualisatie en retourneer als base64 string"""
    x_energy = np.linspace(0, len(y)/sr, len(energy))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[2, 1])
    
    # Bovenste plot
    ax1.plot(np.linspace(0, len(y)/sr, len(y)), y, alpha=0.3, color='#4A90E2', linewidth=0.5, label='Waveform')
    ax1.plot(x_energy, energy, color='#E24A4A', linewidth=1.5, label='Energy')
    ax1.scatter(peak_times, [0.5]*len(peak_times), color='#50C878', s=30, zorder=5, label='Peaks', alpha=0.7)
    
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
    
    # Onderste plot
    ax2.fill_between(x_energy, energy, alpha=0.5, color='#E24A4A')
    ax2.plot(x_energy, energy, color='#E24A4A', linewidth=1.5)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Energy', fontsize=12)
    ax2.set_title('Energy Detail', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Sla op in memory buffer
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Converteer naar base64
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    
    return f"data:image/png;base64,{img_base64}"

def parse_multipart(body, content_type):
    """Parse multipart form data - verbeterde versie"""
    # Parse boundary
    if 'boundary=' not in content_type:
        return {}
    
    boundary = content_type.split('boundary=')[1].strip()
    if boundary.startswith('"') and boundary.endswith('"'):
        boundary = boundary[1:-1]
    
    files = {}
    
    # Split by boundary
    parts = body.split(f'--{boundary}')
    
    for part in parts:
        part = part.strip()
        if not part or part == '--':
            continue
        
        # Find header/content separator
        header_end = -1
        for sep in [b'\r\n\r\n', b'\n\n', '\r\n\r\n', '\n\n']:
            if isinstance(part, bytes):
                if sep.encode() in part:
                    header_end = part.find(sep.encode())
                    break
            else:
                if sep in part:
                    header_end = part.find(sep)
                    break
        
        if header_end == -1:
            continue
        
        # Split headers and content
        if isinstance(part, bytes):
            headers_bytes = part[:header_end]
            content = part[header_end + len(sep):]
            headers_str = headers_bytes.decode('utf-8', errors='ignore')
        else:
            headers_str = part[:header_end]
            content = part[header_end + len(sep):]
        
        # Parse headers
        headers = {}
        for line in headers_str.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        # Check if it's a file
        if 'content-disposition' in headers:
            disp = headers['content-disposition']
            if 'filename=' in disp:
                # Extract filename
                try:
                    # Handle quoted filenames
                    if 'filename="' in disp:
                        filename = disp.split('filename="')[1].split('"')[0]
                    elif "filename='" in disp:
                        filename = disp.split("filename='")[1].split("'")[0]
                    else:
                        filename = disp.split('filename=')[1].split(';')[0].strip()
                    
                    # Extract field name
                    if 'name="' in disp:
                        name = disp.split('name="')[1].split('"')[0]
                    elif "name='" in disp:
                        name = disp.split("name='")[1].split("'")[0]
                    else:
                        name = disp.split('name=')[1].split(';')[0].strip()
                    
                    # Clean up content (remove trailing boundary markers)
                    if isinstance(content, bytes):
                        # Remove trailing \r\n-- if present
                        while content.endswith(b'\r\n--') or content.endswith(b'\n--'):
                            if content.endswith(b'\r\n--'):
                                content = content[:-4]
                            elif content.endswith(b'\n--'):
                                content = content[:-3]
                    else:
                        while content.endswith('\r\n--') or content.endswith('\n--'):
                            if content.endswith('\r\n--'):
                                content = content[:-4]
                            elif content.endswith('\n--'):
                                content = content[:-3]
                    
                    files[name] = {
                        'filename': filename,
                        'content': content
                    }
                except Exception as e:
                    continue
    
    return files

# Vercel entry point
def handler(req):
    """Vercel serverless function handler"""
    # Vercel geeft request als dictionary met specifieke velden
    # Handle both Vercel format and direct dict access
    if isinstance(req, dict):
        method = req.get('method', req.get('httpMethod', 'GET'))
        path = req.get('path', req.get('pathInfo', '/'))
        headers_req = req.get('headers', {})
        body = req.get('body', '')
        
        # Als body base64 encoded is, decode het
        if req.get('isBase64Encoded', False) and body:
            import base64
            body = base64.b64decode(body).decode('utf-8', errors='ignore')
    else:
        # Fallback voor andere formats
        method = 'GET'
        path = '/'
        headers_req = {}
        body = ''
    
    # CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle OPTIONS voor CORS
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': ''
        }
    
    # Serve index page
    if method == 'GET' and path == '/':
        html_content = load_template()
        return {
            'statusCode': 200,
            'headers': {
                **cors_headers,
                'Content-Type': 'text/html; charset=utf-8'
            },
            'body': html_content
        }
    
    # Handle file upload
    if method == 'POST' and path == '/upload':
        try:
            content_type = headers_req.get('content-type', headers_req.get('Content-Type', ''))
            
            if 'multipart/form-data' not in content_type:
                return {
                    'statusCode': 400,
                    'headers': {
                        **cors_headers,
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'error': 'Geen bestand geüpload'})
                }
            
            # Parse multipart data
            files = parse_multipart(body, content_type)
            
            if 'file' not in files:
                return {
                    'statusCode': 400,
                    'headers': {
                        **cors_headers,
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'error': 'Geen bestand gevonden in upload'})
                }
            
            file_data = files['file']
            filename = secure_filename(file_data['filename'])
            file_content = file_data['content']
            
            if not allowed_file(filename):
                return {
                    'statusCode': 400,
                    'headers': {
                        **cors_headers,
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'error': 'Ongeldig bestandsformaat'})
                }
            
            # Sla tijdelijk op in /tmp (beschikbaar in Vercel serverless)
            tmp_dir = '/tmp'
            os.makedirs(tmp_dir, exist_ok=True)
            
            # Genereer unieke filename om conflicten te voorkomen
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(tmp_dir, unique_filename)
            
            with open(filepath, 'wb') as f:
                # Schrijf content als bytes
                if isinstance(file_content, str):
                    # Als string, encode naar bytes (latin-1 behoudt alle bytes)
                    file_content = file_content.encode('latin-1')
                elif isinstance(file_content, bytes):
                    pass  # Al bytes
                else:
                    file_content = bytes(file_content)
                f.write(file_content)
            
            try:
                # Analyseer track
                result = analyze_track_pro(filepath, visualize=False, export=False)
                
                # Laad audio voor visualisatie
                y, sr = librosa.load(filepath, sr=44100)
                energy = np.array(result['energy'])
                peak_times = np.array(result['peaks'])
                
                # Maak visualisatie als base64
                img_base64 = create_visualization_pro_base64(
                    y, sr, energy, peak_times, filename,
                    result['bpm'], result['key'], result.get('mode', 'major'),
                    result.get('camelot', ''), result.get('phrases', {})
                )
                
                result['visualization'] = img_base64
                result['filename'] = filename
                
                # Cleanup temp file
                try:
                    os.remove(filepath)
                except:
                    pass
                
                return {
                    'statusCode': 200,
                    'headers': {
                        **cors_headers,
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps(result)
                }
                
            except Exception as e:
                # Cleanup bij error
                try:
                    os.remove(filepath)
                except:
                    pass
                return {
                    'statusCode': 500,
                    'headers': {
                        **cors_headers,
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'error': f'Fout bij analyseren: {str(e)}'})
                }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    **cors_headers,
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': f'Fout bij verwerken: {str(e)}'})
            }
    
    return {
        'statusCode': 404,
        'headers': {
            **cors_headers,
            'Content-Type': 'application/json'
        },
        'body': json.dumps({'error': 'Route niet gevonden'})
    }

# Vercel verwacht dat de handler functie direct beschikbaar is
# Export de handler als default
__all__ = ['handler']

