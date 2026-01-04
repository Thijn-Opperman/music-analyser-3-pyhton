"""
Music Analyzer Pro - Verbeterde versie met Rekordbox-achtige functionaliteit
- Verbeterde BPM detectie
- Krumhansl-Schmuckler key detection (majeur/minor)
- Camelot wheel notation
- Betere peak detectie
- Phrase detection (intro/verse/chorus)
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path
from scipy.signal import find_peaks


# Keys voor key detectie
KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Krumhansl-Schmuckler profiles voor majeur en minor
# Deze zijn gebaseerd op psychologisch onderzoek naar tooncentrum perceptie
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# Camelot Wheel mapping (zoals Rekordbox gebruikt)
# Format: (key, mode) -> (camelot_number, camelot_letter)
CAMELOT_WHEEL = {
    ('C', 'major'): (8, 'B'), ('C#', 'major'): (3, 'B'), ('D', 'major'): (10, 'B'),
    ('D#', 'major'): (5, 'B'), ('E', 'major'): (12, 'B'), ('F', 'major'): (7, 'B'),
    ('F#', 'major'): (2, 'B'), ('G', 'major'): (9, 'B'), ('G#', 'major'): (4, 'B'),
    ('A', 'major'): (11, 'B'), ('A#', 'major'): (6, 'B'), ('B', 'major'): (1, 'B'),
    ('C', 'minor'): (5, 'A'), ('C#', 'minor'): (12, 'A'), ('D', 'minor'): (7, 'A'),
    ('D#', 'minor'): (2, 'A'), ('E', 'minor'): (9, 'A'), ('F', 'minor'): (4, 'A'),
    ('F#', 'minor'): (11, 'A'), ('G', 'minor'): (6, 'A'), ('G#', 'minor'): (1, 'A'),
    ('A', 'minor'): (8, 'A'), ('A#', 'minor'): (3, 'A'), ('B', 'minor'): (10, 'A'),
}


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


def detect_bpm_improved(y, sr):
    """
    Verbeterde BPM detectie met multi-tempo analyse (zoals Rekordbox)
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        tempo: BPM waarde (meest waarschijnlijke)
        tempo_confidence: Betrouwbaarheid (0-1)
        beat_frames: Frames waar beats voorkomen
    """
    # Methode 1: Standaard beat tracking
    tempo1, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units='time')
    tempo1 = float(tempo1[0] if isinstance(tempo1, np.ndarray) else tempo1)
    
    # Methode 2: Tempogram analyse (meer robuust)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo2 = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, aggregate=np.median)
    tempo2 = float(tempo2[0] if isinstance(tempo2, np.ndarray) else tempo2)
    
    # Methode 3: Multi-tempo detectie
    tempos = librosa.beat.tempo(y=y, sr=sr, aggregate=None)
    if isinstance(tempos, np.ndarray) and len(tempos) > 0:
        tempo3 = float(np.median(tempos))
    else:
        tempo3 = tempo1
    
    # Combineer resultaten (gewogen gemiddelde)
    # Geef meer gewicht aan tempogram (meest betrouwbaar)
    combined_tempo = (tempo1 * 0.3 + tempo2 * 0.5 + tempo3 * 0.2)
    
    # Bereken confidence op basis van consistentie
    tempos_list = [tempo1, tempo2, tempo3]
    std_dev = np.std(tempos_list)
    mean_tempo = np.mean(tempos_list)
    confidence = max(0, 1 - (std_dev / mean_tempo))  # Lagere std = hogere confidence
    
    # Rond af naar dichtstbijzijnde integer
    final_tempo = round(combined_tempo)
    
    print(f"BPM: {final_tempo:.0f} (confidence: {confidence:.2f})")
    print(f"  - Beat track: {tempo1:.1f} BPM")
    print(f"  - Tempogram: {tempo2:.1f} BPM")
    print(f"  - Multi-tempo: {tempo3:.1f} BPM")
    
    return final_tempo, confidence, beat_frames


def detect_key_krumhansl_schmuckler(y, sr):
    """
    Verbeterde key detectie met Krumhansl-Schmuckler algoritme
    Detecteert zowel chroma als majeur/minor mode
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        key: Toonsoort (bijv. 'C', 'D#', etc.)
        mode: 'major' of 'minor'
        key_index: Index van de key in KEYS array
        confidence: Betrouwbaarheid (0-1)
        camelot: Camelot notation (bijv. '8B', '5A')
    """
    # Chromagram voor tonaliteit
    chromagram = librosa.feature.chroma_stft(y=y, sr=sr)
    
    # Gemiddelde chroma vector
    chroma_mean = np.mean(chromagram, axis=1)
    
    # Normaliseer chroma vector
    chroma_norm = chroma_mean / (np.sum(chroma_mean) + 1e-6)
    
    # Test alle 24 mogelijkheden (12 keys × 2 modes)
    correlations = []
    
    for key_idx in range(12):
        # Rotate profiles voor elke key
        major_rotated = np.roll(MAJOR_PROFILE, key_idx)
        minor_rotated = np.roll(MINOR_PROFILE, key_idx)
        
        # Bereken correlatie
        major_corr = np.corrcoef(chroma_norm, major_rotated)[0, 1]
        minor_corr = np.corrcoef(chroma_norm, minor_rotated)[0, 1]
        
        correlations.append((key_idx, 'major', major_corr))
        correlations.append((key_idx, 'minor', minor_corr))
    
    # Vind beste match
    best_match = max(correlations, key=lambda x: x[2])
    key_index, mode, correlation = best_match
    
    # Normaliseer confidence (correlatie kan negatief zijn)
    confidence = max(0, min(1, (correlation + 1) / 2))
    
    key = KEYS[key_index]
    
    # Converteer naar Camelot notation
    camelot = get_camelot_notation(key, mode)
    
    print(f"Key: {key} {mode} (confidence: {confidence:.2f})")
    print(f"Camelot: {camelot}")
    
    return key, mode, key_index, confidence, camelot


def get_camelot_notation(key, mode):
    """
    Converteer key en mode naar Camelot wheel notation
    
    Args:
        key: Toonsoort (bijv. 'C', 'D#')
        mode: 'major' of 'minor'
    
    Returns:
        Camelot notation string (bijv. '8B', '5A')
    """
    camelot = CAMELOT_WHEEL.get((key, mode))
    if camelot:
        return f"{camelot[0]}{camelot[1]}"
    return "?"


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
    
    return energy, rms


def detect_peaks_improved(energy, y, sr, prominence=0.1):
    """
    Verbeterde peak detectie met scipy.signal.find_peaks
    
    Args:
        energy: Energie array
        y: Audio time series
        sr: Sample rate
        prominence: Minimum prominence voor peaks (default: 0.1)
    
    Returns:
        peaks: Array met frame indices waar peaks voorkomen
        peak_times: Array met tijden in seconden waar peaks voorkomen
        peak_heights: Hoogtes van de peaks
    """
    # Gebruik scipy's find_peaks met prominence
    peaks, properties = find_peaks(
        energy, 
        prominence=prominence,
        distance=len(energy) // 100  # Minimaal 1% van track tussen peaks
    )
    
    # Zet frame-indexen om naar seconden
    peak_times = peaks * (len(y)/len(energy)) / sr
    peak_heights = energy[peaks]
    
    print(f"Peaks gevonden: {len(peaks)} (met prominence={prominence})")
    
    return peaks, peak_times, peak_heights


def detect_phrases(y, sr, energy, beat_frames):
    """
    Detecteer muzikale frases (intro, verse, chorus, outro)
    Gebaseerd op energie patronen en beat structure
    
    Args:
        y: Audio time series
        sr: Sample rate
        energy: Energie array
        beat_frames: Beat frames
    
    Returns:
        phrases: Dictionary met gedetecteerde frases
    """
    duration = len(y) / sr
    
    # Segment track in delen op basis van energie
    # Gebruik sliding window om energie gemiddelden te berekenen
    window_size = int(len(energy) / 20)  # 5% van track
    energy_smooth = []
    
    for i in range(len(energy) - window_size):
        energy_smooth.append(np.mean(energy[i:i+window_size]))
    
    energy_smooth = np.array(energy_smooth)
    
    # Vind energie veranderingen (mogelijke phrase boundaries)
    energy_diff = np.diff(energy_smooth)
    threshold = np.std(energy_diff) * 1.5
    
    # Detecteer significante veranderingen
    changes = np.where(np.abs(energy_diff) > threshold)[0]
    
    # Converteer naar seconden
    change_times = changes * (len(y)/len(energy)) / sr
    
    # Classificeer frases op basis van positie en energie
    phrases = {
        'intro': [],
        'verse': [],
        'chorus': [],
        'outro': []
    }
    
    if len(change_times) > 0:
        # Eerste deel = waarschijnlijk intro
        if change_times[0] > 10:
            phrases['intro'].append((0, change_times[0]))
        
        # Laatste deel = waarschijnlijk outro
        if duration - change_times[-1] > 10:
            phrases['outro'].append((change_times[-1], duration))
        
        # Midden delen: hoge energie = chorus, lage = verse
        for i in range(len(change_times) - 1):
            start = change_times[i]
            end = change_times[i + 1]
            mid_time = (start + end) / 2
            
            # Bepaal energie niveau in dit segment
            mid_idx = int(mid_time * len(energy) / duration)
            if mid_idx < len(energy):
                seg_energy = np.mean(energy[max(0, mid_idx-50):min(len(energy), mid_idx+50)])
                
                if seg_energy > 0.6:
                    phrases['chorus'].append((start, end))
                else:
                    phrases['verse'].append((start, end))
    
    print(f"Phrases gedetecteerd:")
    for phrase_type, segments in phrases.items():
        if segments:
            print(f"  {phrase_type}: {len(segments)} segment(en)")
    
    return phrases


def analyze_track_pro(filename, sample_rate=44100, visualize=True, export=True):
    """
    Verbeterde volledige analyse van een enkele track (Rekordbox-achtig)
    
    Args:
        filename: Pad naar audio bestand
        sample_rate: Sample rate (default: 44100)
        visualize: Of visualisatie moet worden getoond (default: True)
        export: Of data moet worden geëxporteerd (default: True)
    
    Returns:
        Dictionary met alle analyse resultaten
    """
    print("\n" + "="*50)
    print(f"🎵 PRO ANALYSE: {Path(filename).name}")
    print("="*50)
    
    # Audio inladen
    y, sr = load_audio(filename, sample_rate)
    
    # Verbeterde BPM detectie
    tempo, tempo_confidence, beat_frames = detect_bpm_improved(y, sr)
    
    # Verbeterde Key detectie (met majeur/minor)
    key, mode, key_index, key_confidence, camelot = detect_key_krumhansl_schmuckler(y, sr)
    
    # Energie berekenen
    energy, rms = calculate_energy(y, sr)
    
    # Verbeterde Peak detectie
    peaks, peak_times, peak_heights = detect_peaks_improved(energy, y, sr)
    
    # Phrase detectie
    phrases = detect_phrases(y, sr, energy, beat_frames)
    
    # Visualisatie
    if visualize:
        track_name = Path(filename).stem
        visualize_track_pro(y, sr, energy, peak_times, track_name, tempo, key, mode, camelot, phrases)
    
    # Data structuur
    data = {
        "title": Path(filename).name,
        "filename": filename,
        "bpm": int(tempo),
        "bpm_confidence": float(tempo_confidence),
        "key": key,
        "mode": mode,
        "key_index": int(key_index),
        "key_confidence": float(key_confidence),
        "camelot": camelot,
        "energy": energy.tolist(),
        "peaks": peak_times.tolist(),
        "peak_heights": peak_heights.tolist(),
        "phrases": phrases,
        "duration_seconds": float(len(y)/sr),
        "sample_rate": int(sr)
    }
    
    if export:
        output_file = f"{Path(filename).stem}_pro_analysis.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"💾 Geëxporteerd naar: {output_file}")
    
    # Samenvatting
    print("\n" + "="*50)
    print("📊 PRO ANALYSE SAMENVATTING")
    print("="*50)
    print(f"📁 Bestand:     {Path(filename).name}")
    print(f"🎵 BPM:         {tempo} ({tempo_confidence*100:.0f}% confidence)")
    print(f"🎹 Key:         {key} {mode} ({key_confidence*100:.0f}% confidence)")
    print(f"🎯 Camelot:     {camelot}")
    print(f"⏱️  Duur:        {len(y)/sr:.2f} sec ({len(y)/sr/60:.2f} min)")
    print(f"📈 Peaks:       {len(peak_times)} gevonden")
    print(f"🎼 Phrases:     {sum(len(v) for v in phrases.values())} segmenten")
    print("="*50)
    print("✅ PRO Analyse voltooid!")
    print("="*50 + "\n")
    
    return data


def visualize_track_pro(y, sr, energy, peak_times, filename, bpm, key, mode, camelot, phrases):
    """
    Verbeterde visualisatie met alle informatie
    """
    x_energy = np.linspace(0, len(y)/sr, len(energy))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[2, 1])
    
    # Bovenste plot: Waveform en energie
    ax1.plot(np.linspace(0, len(y)/sr, len(y)), y, alpha=0.3, color='#4A90E2', linewidth=0.5, label='Waveform')
    ax1.plot(x_energy, energy, color='#E24A4A', linewidth=1.5, label='Energy')
    ax1.scatter(peak_times, [0.5]*len(peak_times), color='#50C878', s=30, zorder=5, label='Peaks', alpha=0.7)
    
    # Markeer phrases
    colors = {'intro': '#FFD700', 'verse': '#87CEEB', 'chorus': '#FF6B6B', 'outro': '#9370DB'}
    for phrase_type, segments in phrases.items():
        for start, end in segments:
            ax1.axvspan(start, end, alpha=0.2, color=colors.get(phrase_type, 'gray'), label=phrase_type.title())
    
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Amplitude / Energy', fontsize=12)
    ax1.set_title(f'{filename} | BPM: {bpm} | Key: {key} {mode} | Camelot: {camelot}', 
                  fontsize=14, fontweight='bold')
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
    
    output_file = f"{filename}_pro_analysis.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"🖼️  Visualisatie opgeslagen: {output_file}")
    plt.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        analyze_track_pro(filename)
    else:
        print("Music Analyzer Pro")
        print("="*50)
        print("\nGebruik:")
        print("  python music_analyzer_pro.py <audio_file>")
        print("\nVoorbeeld:")
        print("  python music_analyzer_pro.py track1.mp3")

