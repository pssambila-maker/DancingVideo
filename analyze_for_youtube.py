"""
Enhanced audio analysis for YouTube content generation.
Analyzes MP3 and generates professional YouTube metadata.
"""

import sys
import os
from pathlib import Path
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import librosa
import numpy as np
from datetime import timedelta

# Load environment
from dotenv import load_dotenv
load_dotenv()


def format_timestamp(seconds):
    """Convert seconds to MM:SS format."""
    td = timedelta(seconds=int(seconds))
    minutes = td.seconds // 60
    secs = td.seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def detect_genre_mood(y, sr, tempo, energy_curve):
    """Detect genre and mood from audio features."""

    # Extract features
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    avg_spectral = np.mean(spectral_centroid)

    chroma = librosa.feature.chroma_stft(y=y, sr=sr)

    # Calculate variance (dynamics)
    energy_variance = np.var(energy_curve)
    avg_energy = np.mean(energy_curve)

    # Genre detection heuristics
    genre = "Unknown"
    mood = "Neutral"

    # BPM-based genre hints
    if 60 <= tempo <= 90:
        if avg_energy > 0.6:
            genre = "Hip-Hop/Trap"
            mood = "Confident"
        else:
            genre = "R&B/Soul"
            mood = "Chill"
    elif 90 <= tempo <= 120:
        if avg_spectral > 2000:
            genre = "Pop/Dance"
            mood = "Upbeat"
        else:
            genre = "Rock/Alternative"
            mood = "Energetic"
    elif 120 <= tempo <= 140:
        if avg_energy > 0.7:
            genre = "Dance/EDM"
            mood = "Euphoric"
        else:
            genre = "Pop"
            mood = "Uplifting"
    elif tempo > 140:
        genre = "EDM/House"
        mood = "High Energy"

    # Refine mood based on energy variance
    if energy_variance < 0.02:
        mood = "Steady"
    elif energy_variance > 0.1:
        mood = "Dynamic"

    return genre, mood


def analyze_audio_comprehensive(audio_path, output_dir):
    """Complete audio analysis with YouTube metadata generation."""

    print(f"\n🎵 Analyzing: {Path(audio_path).name}")
    print("=" * 60)

    # Load audio
    print("Loading audio...", end=" ", flush=True)
    y, sr = librosa.load(audio_path, sr=22050)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"✓ ({duration:.1f}s / {duration/60:.1f}min)")

    # Tempo and beats
    print("Detecting tempo and beats...", end=" ", flush=True)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beats = librosa.frames_to_time(beat_frames, sr=sr)
    tempo = float(tempo) if hasattr(tempo, '__iter__') else tempo
    print(f"✓ ({tempo:.1f} BPM)")

    # Energy analysis
    print("Analyzing energy levels...", end=" ", flush=True)
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    rms_normalized = rms / rms.max() if rms.max() > 0 else rms

    # Resample energy curve to 2Hz (2 samples per second)
    num_samples = int(duration * 2)
    indices = np.linspace(0, len(rms_normalized) - 1, num_samples).astype(int)
    energy_curve = rms_normalized[indices]
    print("✓")

    # Detect genre and mood
    print("Detecting genre and mood...", end=" ", flush=True)
    genre, mood = detect_genre_mood(y, sr, tempo, energy_curve)
    print(f"✓ ({genre}, {mood})")

    # Section detection
    print("Detecting song sections...", end=" ", flush=True)
    try:
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        bounds = librosa.segment.agglomerative(chroma, k=min(8, int(duration / 20)))
        bound_times = librosa.frames_to_time(bounds, sr=sr)
        print(f"✓ ({len(bound_times)-1} sections)")
    except Exception as e:
        print(f"⚠️ Using fallback")
        num_sections = max(4, int(duration / 25))
        bound_times = np.linspace(0, duration, num_sections + 1)

    # Label sections intelligently
    sections = []
    section_names = []

    for i in range(len(bound_times) - 1):
        start = bound_times[i]
        end = bound_times[i + 1]

        # Calculate section energy
        start_idx = int(start * 2)
        end_idx = int(end * 2)
        section_slice = energy_curve[start_idx:end_idx]
        section_energy = float(np.mean(section_slice)) if len(section_slice) > 0 else 0.5

        # Determine section type
        position_ratio = start / duration

        if i == 0:
            label = "Intro"
        elif i == len(bound_times) - 2:
            label = "Outro"
        elif position_ratio < 0.2:
            label = "Intro" if section_energy < 0.5 else "Build-Up"
        elif position_ratio > 0.8:
            label = "Outro" if section_energy < 0.5 else "Final Chorus"
        elif section_energy > 0.7:
            label = "Chorus" if "Chorus" not in section_names else "Drop"
        elif section_energy < 0.4:
            label = "Verse" if section_energy > 0.25 else "Break"
        elif 0.5 <= section_energy <= 0.7:
            label = "Bridge" if position_ratio > 0.6 else "Pre-Chorus"
        else:
            label = "Verse"

        section_names.append(label)

        sections.append({
            "id": i,
            "label": label,
            "start": round(float(start), 2),
            "end": round(float(end), 2),
            "duration": round(float(end - start), 2),
            "energy": round(section_energy, 3),
            "timestamp": format_timestamp(start)
        })

    # Create comprehensive analysis
    analysis = {
        "metadata": {
            "filename": Path(audio_path).name,
            "duration_seconds": round(duration, 2),
            "duration_formatted": format_timestamp(duration),
            "file_size_mb": round(Path(audio_path).stat().st_size / (1024*1024), 2)
        },
        "audio_features": {
            "bpm": round(float(tempo), 1),
            "genre": genre,
            "mood": mood,
            "total_beats": len(beats),
            "avg_energy": round(float(np.mean(energy_curve)), 3),
            "energy_variance": round(float(np.var(energy_curve)), 3)
        },
        "sections": sections,
        "youtube_metadata": {
            "genre": genre,
            "mood": mood,
            "key_moments": []
        }
    }

    # Identify key moments (high energy peaks)
    for i, section in enumerate(sections):
        if section['energy'] > 0.75:
            analysis['youtube_metadata']['key_moments'].append({
                "time": section['timestamp'],
                "label": section['label'],
                "description": f"High energy {section['label'].lower()}"
            })

    # Save analysis
    output_path = Path(output_dir) / "audio_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\n💾 Analysis saved to: {output_path}")

    return analysis


def print_analysis_summary(analysis):
    """Print beautiful analysis summary."""

    print("\n" + "=" * 60)
    print("📊 AUDIO ANALYSIS SUMMARY")
    print("=" * 60)

    meta = analysis['metadata']
    features = analysis['audio_features']

    print(f"\n🎵 File Info:")
    print(f"   Duration: {meta['duration_formatted']} ({meta['duration_seconds']}s)")
    print(f"   Size: {meta['file_size_mb']} MB")

    print(f"\n🎼 Audio Features:")
    print(f"   BPM: {features['bpm']}")
    print(f"   Genre: {features['genre']}")
    print(f"   Mood: {features['mood']}")
    print(f"   Average Energy: {features['avg_energy']:.1%}")

    print(f"\n🎬 Song Structure ({len(analysis['sections'])} sections):")
    print(f"   {'Timestamp':<10} {'Section':<15} {'Duration':<10} {'Energy'}")
    print(f"   {'-'*10} {'-'*15} {'-'*10} {'-'*8}")

    for section in analysis['sections']:
        energy_bar = "█" * int(section['energy'] * 10)
        print(f"   {section['timestamp']:<10} {section['label']:<15} {section['duration']:.1f}s{'':<6} {energy_bar}")

    if analysis['youtube_metadata']['key_moments']:
        print(f"\n⭐ Key Moments:")
        for moment in analysis['youtube_metadata']['key_moments']:
            print(f"   {moment['time']} - {moment['description']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    audio_file = "test_audio.mp3"
    output_dir = "output"

    if not Path(audio_file).exists():
        print(f"❌ Error: {audio_file} not found")
        print("Please ensure the MP3 file is in the current directory")
        exit(1)

    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)

    # Analyze
    analysis = analyze_audio_comprehensive(audio_file, output_dir)

    # Print summary
    print_analysis_summary(analysis)

    print("\n✅ Analysis complete!")
    print(f"📁 Results saved to: {output_dir}/")
