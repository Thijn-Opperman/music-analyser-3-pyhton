"""
Music Analyzer - Analyseer audio tracks voor BPM, key, energie en peaks
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path


# Keys voor key detectie
KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def load_audio(filename, sample_rate=44100):
    """
    Laad audio bestand in
    
    Args:
        filename: Pad naar audio bestand (mp3/wav)
        sample_rate: Sample rate in Hz (default: 44100)
    
    Returns:
        y: Audio time series
        sr: Sample rate
    """
    print(f"Laden van track: {filename}")
    y, sr = librosa.load(filename, sr=sample_rate)
    print(f"Track geladen: {filename}, Sample Rate: {sr}, Lengte: {len(y)/sr:.2f} sec")
    return y, sr


def detect_bpm(y, sr):
    """
    Detecteer BPM (Beats Per Minute)
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        tempo: BPM waarde
        beat_frames: Frames waar beats voorkomen
    """
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    # Zorg dat tempo een scalar is (niet een array)
    tempo = float(tempo[0] if isinstance(tempo, np.ndarray) else tempo)
    print(f"BPM: {tempo:.2f}")
    return tempo, beat_frames


def detect_key(y, sr):
    """
    Detecteer de key (toonsoort) van het nummer
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        key: Toonsoort (bijv. 'C', 'D#', etc.)
        key_index: Index van de key in KEYS array
    """
    # Chromagram voor tonaliteit
    chromagram = librosa.feature.chroma_stft(y=y, sr=sr)
    
    # Dominante toon berekenen
    key_index = np.argmax(chromagram.mean(axis=1))
    key = KEYS[key_index]
    
    print(f"Key: {key}")
    return key, key_index


def calculate_energy(y, sr):
    """
    Bereken energie (RMS) van het nummer
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        energy: Genormaliseerde energie array (0-1)
        rms: Ruwe RMS waarden
    """
    # RMS = Root Mean Square (energie)
    rms = librosa.feature.rms(y=y)[0]
    
    # Normaliseer energie naar 0-1
    if rms.max() - rms.min() > 0:
        energy = (rms - rms.min()) / (rms.max() - rms.min())
    else:
        energy = rms
    
    print(f"Eerste 10 energy samples: {energy[:10]}")
    return energy, rms


def detect_peaks(energy, y, sr, threshold=0.6):
    """
    Detecteer peaks in de energie curve
    
    Args:
        energy: Energie array
        y: Audio time series
        sr: Sample rate
        threshold: Drempelwaarde voor peaks (default: 0.6)
    
    Returns:
        peaks: Array met frame indices waar peaks voorkomen
        peak_times: Array met tijden in seconden waar peaks voorkomen
    """
    # Drempel instellen
    peaks = np.where(energy > threshold)[0]
    
    # Zet frame-indexen om naar seconden
    peak_times = peaks * (len(y)/len(energy)) / sr
    
    print(f"Peaks op seconden: {peak_times[:10]}...")  # Toon eerste 10
    return peaks, peak_times


def visualize_track(y, sr, energy, peak_times, filename="track", bpm=None, key=None):
    """
    Visualiseer waveform, energie en peaks
    
    Args:
        y: Audio time series
        sr: Sample rate
        energy: Energie array
        peak_times: Tijden waar peaks voorkomen
        filename: Bestandsnaam voor opslag
        bpm: BPM waarde (optioneel)
        key: Key waarde (optioneel)
    """
    # X-as voor energie
    x_energy = np.linspace(0, len(y)/sr, len(energy))
    
    plt.figure(figsize=(12, 4))
    plt.plot(np.linspace(0, len(y)/sr, len(y)), y, alpha=0.5, label='Waveform')
    plt.plot(x_energy, energy, color='red', label='Energy')
    plt.scatter(peak_times, [0.5]*len(peak_times), color='green', label='Peaks', s=10)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude / Energy')
    plt.legend()
    
    # Titel met BPM en Key
    title = f'Track Analyse: {filename}'
    if bpm is not None and key is not None:
        title += f' | BPM: {bpm:.1f} | Key: {key}'
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Sla visualisatie op
    output_file = f"{filename}_analysis.png"
    plt.savefig(output_file, dpi=150)
    print(f"Visualisatie opgeslagen als: {output_file}")
    plt.show()


def export_to_json(data, output_file="track_analysis.json"):
    """
    Exporteer analyse data naar JSON
    
    Args:
        data: Dictionary met analyse data
        output_file: Output bestandsnaam
    """
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Analyse geëxporteerd naar {output_file}")


def analyze_track(filename, sample_rate=44100, energy_threshold=0.6, visualize=True, export=True):
    """
    Volledige analyse van een enkele track
    
    Args:
        filename: Pad naar audio bestand
        sample_rate: Sample rate (default: 44100)
        energy_threshold: Drempel voor peak detectie (default: 0.6)
        visualize: Of visualisatie moet worden getoond (default: True)
        export: Of data moet worden geëxporteerd (default: True)
    
    Returns:
        Dictionary met alle analyse resultaten
    """
    print("\n" + "="*50)
    print(f"Analyseren van: {filename}")
    print("="*50)
    
    # Stap 2: Audio inladen
    y, sr = load_audio(filename, sample_rate)
    
    # Stap 3: BPM detecteren
    tempo, beat_frames = detect_bpm(y, sr)
    
    # Stap 4: Key detectie
    key, key_index = detect_key(y, sr)
    
    # Stap 5: Energie berekenen
    energy, rms = calculate_energy(y, sr)
    
    # Stap 6: Peaks detecteren
    peaks, peak_times = detect_peaks(energy, y, sr, energy_threshold)
    
    # Stap 7: Visualisatie
    if visualize:
        track_name = Path(filename).stem
        visualize_track(y, sr, energy, peak_times, track_name, bpm=tempo, key=key)
    
    # Stap 8: Exporteren naar JSON
    data = {
        "title": Path(filename).name,
        "filename": filename,
        "bpm": float(tempo),
        "key": key,
        "key_index": int(key_index),
        "energy": energy.tolist(),
        "peaks": peak_times.tolist(),
        "duration_seconds": float(len(y)/sr),
        "sample_rate": int(sr)
    }
    
    if export:
        output_file = f"{Path(filename).stem}_analysis.json"
        export_to_json(data, output_file)
    
    # Samenvatting weergeven
    print("\n" + "="*50)
    print("📊 ANALYSE SAMENVATTING")
    print("="*50)
    print(f"📁 Bestand:     {Path(filename).name}")
    print(f"🎵 BPM:         {tempo:.2f}")
    print(f"🎹 Key:         {key}")
    print(f"⏱️  Duur:        {len(y)/sr:.2f} seconden ({len(y)/sr/60:.2f} minuten)")
    print(f"📈 Peaks:       {len(peak_times)} gevonden")
    if export:
        print(f"💾 JSON:        {Path(filename).stem}_analysis.json")
    if visualize:
        print(f"🖼️  Visualisatie: {Path(filename).stem}_analysis.png")
    print("="*50)
    print("✅ Analyse voltooid!")
    print("="*50 + "\n")
    
    return data


def batch_analyze(folder="tracks", sample_rate=44100, energy_threshold=0.6, output_file="all_tracks.json"):
    """
    Batch-analyse van meerdere tracks in een folder
    
    Args:
        folder: Pad naar folder met audio bestanden
        sample_rate: Sample rate (default: 44100)
        energy_threshold: Drempel voor peak detectie (default: 0.6)
        output_file: Output JSON bestandsnaam
    
    Returns:
        List met analyse resultaten
    """
    print("\n" + "="*50)
    print(f"Batch-analyse van folder: {folder}")
    print("="*50)
    
    results = []
    folder_path = Path(folder)
    
    if not folder_path.exists():
        print(f"Folder '{folder}' bestaat niet!")
        return results
    
    # Zoek alle audio bestanden
    audio_files = []
    for ext in [".mp3", ".wav", ".m4a", ".flac"]:
        audio_files.extend(folder_path.glob(f"*{ext}"))
    
    if not audio_files:
        print(f"Geen audio bestanden gevonden in '{folder}'")
        return results
    
    print(f"Gevonden {len(audio_files)} audio bestand(en)")
    
    # Analyseer elk bestand
    for i, file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Verwerken van: {file.name}")
        try:
            y, sr = load_audio(str(file), sample_rate)
            tempo, beat_frames = detect_bpm(y, sr)
            chromagram = librosa.feature.chroma_stft(y=y, sr=sr)
            key_index = np.argmax(chromagram.mean(axis=1))
            key = KEYS[key_index]
            rms = librosa.feature.rms(y=y)[0]
            energy = (rms - rms.min()) / (rms.max() - rms.min()) if rms.max() - rms.min() > 0 else rms
            peaks = np.where(energy > energy_threshold)[0]
            peak_times = peaks * (len(y)/len(energy)) / sr
            
            results.append({
                "title": file.name,
                "filename": str(file),
                "bpm": float(tempo),
                "key": key,
                "key_index": int(key_index),
                "energy": energy.tolist(),
                "peaks": peak_times.tolist(),
                "duration_seconds": float(len(y)/sr),
                "sample_rate": int(sr)
            })
            
            print(f"✓ {file.name} geanalyseerd")
        except Exception as e:
            print(f"✗ Fout bij analyseren van {file.name}: {e}")
            continue
    
    # Exporteer alle resultaten
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print("\n" + "="*50)
    print(f"Batch-analyse voltooid. {len(results)} tracks geanalyseerd.")
    print(f"Resultaten opgeslagen in: {output_file}")
    print("="*50 + "\n")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Command line argument handling
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch" or sys.argv[1] == "-b":
            # Batch analyse
            folder = sys.argv[2] if len(sys.argv) > 2 else "tracks"
            batch_analyze(folder)
        else:
            # Analyseer één track
            filename = sys.argv[1]
            analyze_track(filename)
    else:
        print("Music Analyzer")
        print("="*50)
        print("\nGebruik:")
        print("  python music_analyzer.py <audio_file>  - Analyseer één track")
        print("  python music_analyzer.py --batch [folder]  - Batch analyse")
        print("\nVoorbeeld:")
        print("  python music_analyzer.py track1.mp3")
        print("  python music_analyzer.py --batch tracks/")
        print("\nOf gebruik de functies direct in Python:")
        print("  from music_analyzer import analyze_track, batch_analyze")
        print("  analyze_track('track1.mp3')")
        print("  batch_analyze('tracks/')")

