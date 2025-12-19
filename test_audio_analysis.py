"""
Test script for audio analysis to determine how many video clips are needed.
This simulates the first step of our pipeline.
"""

import librosa
import numpy as np
from pathlib import Path
import json


def analyze_audio_for_clips(audio_path, target_clip_duration=(4, 8)):
    """
    Analyze an MP3 file and determine how many video clips we'll need.

    Args:
        audio_path: Path to MP3/audio file
        target_clip_duration: Tuple of (min, max) seconds per clip

    Returns:
        Dictionary with analysis results and clip requirements
    """

    print(f"\n🎵 Analyzing: {Path(audio_path).name}")
    print("=" * 60)

    # Load audio
    print("Loading audio file...", end=" ", flush=True)
    y, sr = librosa.load(audio_path, sr=22050)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"✓ ({duration:.1f} seconds)")

    # Extract tempo (BPM)
    print("Detecting BPM...", end=" ", flush=True)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beats = librosa.frames_to_time(beat_frames, sr=sr)
    print(f"✓ ({tempo:.1f} BPM, {len(beats)} beats)")

    # Calculate energy (RMS)
    print("Analyzing energy levels...", end=" ", flush=True)
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    # Normalize
    rms_normalized = rms / rms.max() if rms.max() > 0 else rms
    print("✓")

    # Detect sections using structural analysis
    print("Detecting song sections...", end=" ", flush=True)
    try:
        # Use chroma features for structure
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        # Segment into ~6-10 sections
        bounds = librosa.segment.agglomerative(chroma, k=8)
        bound_times = librosa.frames_to_time(bounds, sr=sr)
        print(f"✓ ({len(bound_times)-1} sections)")
    except Exception as e:
        print(f"⚠️  Using fallback sectioning")
        # Fallback: divide into 30-second sections
        num_sections = max(4, int(duration / 30))
        bound_times = np.linspace(0, duration, num_sections + 1)

    # Assign labels and energy to sections
    sections = []
    section_labels = ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"]

    for i in range(len(bound_times) - 1):
        start = bound_times[i]
        end = bound_times[i + 1]

        # Calculate average energy for this section
        start_idx = int(start * sr / 512)
        end_idx = int(end * sr / 512)
        section_energy = float(np.mean(rms_normalized[start_idx:end_idx]))

        # Assign label
        if i == 0:
            label = "intro"
        elif i == len(bound_times) - 2:
            label = "outro"
        elif section_energy > 0.7:
            label = "chorus"
        elif section_energy < 0.4:
            label = "verse"
        else:
            label = section_labels[i % len(section_labels)]

        sections.append({
            "id": i,
            "label": label,
            "start": round(float(start), 2),
            "end": round(float(end), 2),
            "duration": round(float(end - start), 2),
            "energy": round(section_energy, 2)
        })

    # Calculate how many clips we need
    print("\nCalculating clip requirements...", end=" ", flush=True)

    total_clips = 0
    clips_breakdown = []

    for section in sections:
        section_duration = section['duration']
        # Use average clip duration
        avg_clip_duration = sum(target_clip_duration) / 2
        num_clips = max(1, int(section_duration / avg_clip_duration))
        total_clips += num_clips

        clips_breakdown.append({
            "section": section['label'],
            "time_range": f"{section['start']}-{section['end']}s",
            "clips_needed": num_clips,
            "energy": section['energy']
        })

    print(f"✓ ({total_clips} clips needed)")

    # Create result summary
    result = {
        "audio_file": str(audio_path),
        "duration_seconds": round(duration, 2),
        "bpm": round(float(tempo), 1),
        "total_beats": len(beats),
        "sections": sections,
        "clip_requirements": {
            "total_clips_needed": total_clips,
            "target_clip_duration": f"{target_clip_duration[0]}-{target_clip_duration[1]}s",
            "breakdown_by_section": clips_breakdown
        }
    }

    return result


def print_analysis_summary(result):
    """Pretty print the analysis results."""

    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)

    print(f"\n🎵 Audio Info:")
    print(f"   Duration: {result['duration_seconds']} seconds ({result['duration_seconds']/60:.1f} minutes)")
    print(f"   BPM: {result['bpm']}")
    print(f"   Total Beats: {result['total_beats']}")

    print(f"\n📹 Video Clip Requirements:")
    print(f"   Total clips needed: {result['clip_requirements']['total_clips_needed']}")
    print(f"   Target clip length: {result['clip_requirements']['target_clip_duration']}")

    print(f"\n🎬 Section Breakdown:")
    print(f"   {'Section':<12} {'Time Range':<15} {'Energy':<8} {'Clips'}")
    print(f"   {'-'*12} {'-'*15} {'-'*8} {'-'*5}")

    for clip_info in result['clip_requirements']['breakdown_by_section']:
        section = clip_info['section']
        time_range = clip_info['time_range']
        energy = clip_info['energy']
        clips = clip_info['clips_needed']

        # Energy indicator
        energy_bar = "█" * int(energy * 10)

        print(f"   {section:<12} {time_range:<15} {energy_bar:<8} {clips} clips")

    print("\n" + "=" * 60)
    print("💡 INTERPRETATION:")
    print("=" * 60)

    total_clips = result['clip_requirements']['total_clips_needed']

    print(f"\nFor this {result['duration_seconds']/60:.1f}-minute song, you'll need to generate:")
    print(f"   • {total_clips} separate video clips")
    print(f"   • Each clip: {result['clip_requirements']['target_clip_duration']}")

    print(f"\n⏱️  Estimated Generation Time:")
    print(f"   • At ~30-60 sec per clip: {total_clips * 0.5:.0f}-{total_clips:.0f} minutes")
    print(f"   • At ~2-3 min per clip: {total_clips * 2:.0f}-{total_clips * 3:.0f} minutes")

    print(f"\n💰 Estimated Cost (varies by service):")
    print(f"   • If $0.10/clip: ${total_clips * 0.10:.2f}")
    print(f"   • If $0.50/clip: ${total_clips * 0.50:.2f}")
    print(f"   • If $1.00/clip: ${total_clips * 1.00:.2f}")

    print("\n" + "=" * 60)


def save_analysis(result, output_path="test_output/analysis.json"):
    """Save analysis to JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n💾 Analysis saved to: {output_file}")


if __name__ == "__main__":
    print("=" * 60)
    print("AUDIO ANALYSIS TEST - CLIP REQUIREMENTS")
    print("=" * 60)

    # Look for test audio file
    test_files = [
        "test_audio.mp3",
        "sample.mp3",
        "test.mp3",
    ]

    audio_file = None
    for filename in test_files:
        if Path(filename).exists():
            audio_file = filename
            break

    if not audio_file:
        print("\n⚠️  No test audio file found!")
        print("\nPlease provide a test MP3 file:")
        print("   1. Place an MP3 file in this directory")
        print("   2. Name it 'test_audio.mp3' or 'sample.mp3'")
        print("   3. Or provide the path below:\n")

        audio_file = input("Enter path to MP3 file (or press Enter to skip): ").strip()

        if not audio_file or not Path(audio_file).exists():
            print("\n✅ Test skipped. No audio file provided.")
            print("\nWhen you have an MP3 file, run:")
            print("   python test_audio_analysis.py")
            exit(0)

    try:
        # Analyze the audio
        result = analyze_audio_for_clips(audio_file)

        # Print summary
        print_analysis_summary(result)

        # Save results
        save_analysis(result)

        print("\n✅ Test complete!")
        print("\nNext step: Use these clip requirements to test video generation")

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
