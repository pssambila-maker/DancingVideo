"""
Test Claude's ability to generate choreography prompts for video generation.
This will help us see what kind of prompts Claude creates.
"""

import anthropic
import os
import json
from pathlib import Path


def generate_sample_choreography(audio_analysis=None):
    """
    Test Claude's choreography generation with sample data.

    Args:
        audio_analysis: Optional dict from audio analysis, or use mock data
    """

    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not api_key:
        print("❌ ERROR: Please set ANTHROPIC_API_KEY environment variable")
        print("   Get your key from: https://console.anthropic.com/")
        return None

    client = anthropic.Anthropic(api_key=api_key)

    print("\n🎭 Testing Claude Choreography Generation")
    print("=" * 60)

    # Use provided analysis or create mock data
    if not audio_analysis:
        print("📝 Using mock audio analysis data...")
        audio_analysis = {
            "duration_seconds": 180,
            "bpm": 128,
            "sections": [
                {"label": "intro", "start": 0, "end": 15, "energy": 0.3},
                {"label": "verse", "start": 15, "end": 45, "energy": 0.5},
                {"label": "chorus", "start": 45, "end": 75, "energy": 0.9},
                {"label": "verse", "start": 75, "end": 105, "energy": 0.5},
                {"label": "chorus", "start": 105, "end": 135, "energy": 0.9},
                {"label": "bridge", "start": 135, "end": 155, "energy": 0.6},
                {"label": "chorus", "start": 155, "end": 180, "energy": 0.95},
            ]
        }
    else:
        print("📊 Using provided audio analysis data...")

    # Create the prompt
    system_prompt = """You are an expert dance choreographer and music video director.
Your job is to create detailed video generation prompts for an AI video generator (like Gemini).

Given audio analysis data (BPM, sections, energy levels) and a dance style, output a JSON array of video prompts.

Rules:
1. Each clip should be 4-7 seconds long
2. Match movement intensity to the section's energy level (0-1 scale)
3. Prompts should be specific and visual for AI video generation
4. Include camera framing suggestions (full body, medium shot, close-up)
5. Describe specific movements, not just general "dancing"
6. Consider smooth conceptual flow between segments

Output ONLY a JSON array with this structure:
[
  {
    "segment_id": 0,
    "start": 0.0,
    "end": 5.0,
    "section": "intro",
    "video_prompt": "A dancer in urban streetwear standing still, then slowly starting to move with subtle head nods and shoulder bounces to the beat, soft lighting, full body shot",
    "intensity": 2,
    "camera": "full_body",
    "movement_type": "subtle_groove"
  }
]

Make the prompts work for text-to-video AI models."""

    style = "hip-hop"
    user_prompt = f"""Create video generation prompts for this song:

AUDIO ANALYSIS:
{json.dumps(audio_analysis, indent=2)}

DANCE STYLE: {style}
TARGET: Create prompts for AI video generation (like Gemini, Runway, etc.)

Generate specific, visual prompts that an AI can understand. Focus on:
- Exact body movements (e.g., "arms swinging side to side", "quick footwork", "slow body roll")
- Visual setting and lighting
- Energy matching the music sections
- Camera angles

Output ONLY the JSON array, no other text."""

    print(f"\n🎵 Song Duration: {audio_analysis['duration_seconds']}s")
    print(f"🎵 BPM: {audio_analysis['bpm']}")
    print(f"🎵 Style: {style}")
    print(f"🎵 Sections: {len(audio_analysis['sections'])}")

    print("\n💭 Generating choreography prompts with Claude...", flush=True)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.7,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        # Extract response
        content = response.content[0].text

        # Clean up if needed
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        # Parse JSON
        choreography = json.loads(content.strip())

        print(" ✓ Success!\n")

        # Display results
        print("=" * 60)
        print("🎬 GENERATED VIDEO PROMPTS")
        print("=" * 60)

        for i, segment in enumerate(choreography, 1):
            print(f"\n📹 Segment {i}/{len(choreography)}")
            print(f"   Time: {segment['start']}s - {segment['end']}s ({segment['end']-segment['start']:.1f}s)")
            print(f"   Section: {segment['section']}")
            print(f"   Intensity: {segment['intensity']}/5")
            print(f"   Camera: {segment['camera']}")
            print(f"   Prompt: {segment['video_prompt'][:100]}...")
            if len(segment['video_prompt']) > 100:
                print(f"          {segment['video_prompt'][100:]}")

        print("\n" + "=" * 60)
        print(f"📊 SUMMARY")
        print("=" * 60)
        print(f"   Total segments: {len(choreography)}")
        print(f"   Total duration: {choreography[-1]['end']}s")
        print(f"   Average clip length: {sum(s['end']-s['start'] for s in choreography)/len(choreography):.1f}s")

        # Count by intensity
        intensity_counts = {}
        for seg in choreography:
            intensity = seg['intensity']
            intensity_counts[intensity] = intensity_counts.get(intensity, 0) + 1

        print(f"\n   Intensity distribution:")
        for intensity in sorted(intensity_counts.keys()):
            count = intensity_counts[intensity]
            bar = "█" * count
            print(f"      {intensity}/5: {bar} ({count} clips)")

        # Save to file
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "choreography_prompts.json"

        with open(output_file, 'w') as f:
            json.dump(choreography, f, indent=2)

        print(f"\n💾 Prompts saved to: {output_file}")

        print("\n" + "=" * 60)
        print("💡 NEXT STEPS:")
        print("=" * 60)
        print("1. Review the prompts - are they specific enough for video gen?")
        print("2. Try feeding 1-2 prompts to Gemini/Runway to see quality")
        print("3. Adjust the choreography prompt if needed")
        print("4. If results look good, build the full pipeline!")

        return choreography

    except json.JSONDecodeError as e:
        print(f" ❌ Failed to parse response as JSON")
        print(f"\nRaw response:\n{content}")
        return None

    except Exception as e:
        print(f" ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("CLAUDE CHOREOGRAPHY TEST")
    print("=" * 60)

    # Check if we have audio analysis results
    analysis_file = Path("test_output/analysis.json")

    audio_analysis = None
    if analysis_file.exists():
        print(f"\n✓ Found audio analysis from previous test")
        with open(analysis_file, 'r') as f:
            data = json.load(f)
            audio_analysis = {
                "duration_seconds": data['duration_seconds'],
                "bpm": data['bpm'],
                "sections": data['sections']
            }

    # Generate choreography
    result = generate_sample_choreography(audio_analysis)

    if result:
        print("\n✅ Test complete!")
    else:
        print("\n❌ Test failed - check error messages above")
