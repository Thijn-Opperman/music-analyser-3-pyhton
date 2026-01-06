"""
Music Analyzer - Vereenvoudigde versie
Retourneert alleen: songnaam, BPM, key en duur
"""

import librosa
import numpy as np
from pathlib import Path

# Keys voor key detectie
KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Krumhansl-Schmuckler profiles voor majeur en minor
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def detect_bpm_improved(y, sr):
    """
    Verbeterde BPM detectie met multi-tempo analyse
    """
    # Methode 1: Standaard beat tracking
    tempo1, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units='time')
    tempo1 = float(tempo1[0] if isinstance(tempo1, np.ndarray) else tempo1)
    
    # Methode 2: Tempogram analyse
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
    combined_tempo = (tempo1 * 0.3 + tempo2 * 0.5 + tempo3 * 0.2)
    
    # Rond af naar dichtstbijzijnde integer
    final_tempo = round(combined_tempo)
    
    return final_tempo


def detect_key_krumhansl_schmuckler(y, sr):
    """
    Key detectie met Krumhansl-Schmuckler algoritme
    Detecteert zowel chroma als majeur/minor mode
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
    
    key = KEYS[key_index]
    
    # Retourneer key + mode (bijv. "C major" of "A minor")
    return f"{key} {mode}"


def analyze_track_simple(filename, sample_rate=44100):
    """
    Vereenvoudigde analyse - retourneert alleen essentiële data
    
    Args:
        filename: Pad naar audio bestand
        sample_rate: Sample rate (default: 44100)
    
    Returns:
        Dictionary met: songnaam, bpm, key, duration
    """
    # Audio inladen
    y, sr = librosa.load(filename, sr=sample_rate)
    
    # BPM detecteren
    bpm = detect_bpm_improved(y, sr)
    
    # Key detecteren
    key = detect_key_krumhansl_schmuckler(y, sr)
    
    # Duur berekenen
    duration_seconds = len(y) / sr
    
    # Songnaam (zonder extensie)
    song_name = Path(filename).stem
    
    return {
        "songnaam": song_name,
        "bpm": bpm,
        "key": key,
        "duration": duration_seconds
    }

