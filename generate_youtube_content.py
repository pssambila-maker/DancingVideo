"""
Generate professional YouTube title, description, and thumbnail text
based on audio analysis using Claude AI.
"""

import sys
import os
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

import anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


def generate_youtube_metadata(analysis_path, output_dir):
    """Generate YouTube title, description, and thumbnail suggestions."""

    if not ANTHROPIC_API_KEY:
        print("❌ ERROR: ANTHROPIC_API_KEY not set")
        return

    # Load analysis
    with open(analysis_path, 'r') as f:
        analysis = json.load(f)

    print("\n🎬 Generating YouTube Content with Claude AI")
    print("=" * 60)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Prepare context
    genre = analysis['audio_features']['genre']
    mood = analysis['audio_features']['mood']
    duration = analysis['metadata']['duration_formatted']
    bpm = analysis['audio_features']['bpm']

    # Build section breakdown
    section_breakdown = "\n".join([
        f"- {s['timestamp']} {s['label']} ({s['duration']:.1f}s, Energy: {s['energy']:.0%})"
        for s in analysis['sections']
    ])

    prompt = f"""You are a professional YouTube content creator and music marketer. Create compelling YouTube metadata for this music track.

TRACK ANALYSIS:
- Genre: {genre}
- Mood: {mood}
- Duration: {duration}
- BPM: {bpm}
- Structure:
{section_breakdown}

Generate the following (output as JSON):

1. **YouTube Title** (50-70 characters, clickable, SEO-friendly)
   - Include genre/mood keywords
   - Make it catchy and professional
   - Examples: "Uplifting Pop Dance Mix 2024 🎵 | 117 BPM Workout Music"

2. **YouTube Description** (comprehensive):
   - Opening hook (2-3 sentences about the track)
   - Timestamps for key sections
   - Hashtags (10-15 relevant tags)
   - Call to action (like, subscribe, comment)
   - Professional footer

3. **Thumbnail Text Suggestions** (3-5 words max for thumbnail overlay):
   - Short, bold, eye-catching
   - Examples: "POP VIBES", "117 BPM", "DANCE MIX"

Output ONLY valid JSON in this format:
{{
  "title": "...",
  "description": "...",
  "thumbnail_suggestions": ["TEXT 1", "TEXT 2", "TEXT 3"]
}}"""

    print("Requesting YouTube content from Claude...", flush=True)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        metadata = json.loads(content.strip())

        print("✓ Content generated!\n")

        # Save individual files
        output_path = Path(output_dir)

        # Title
        title_file = output_path / "youtube_title.txt"
        with open(title_file, 'w', encoding='utf-8') as f:
            f.write(metadata['title'])
        print(f"💾 Title saved: {title_file}")

        # Description
        desc_file = output_path / "youtube_description.txt"
        with open(desc_file, 'w', encoding='utf-8') as f:
            f.write(metadata['description'])
        print(f"💾 Description saved: {desc_file}")

        # Thumbnail suggestions
        thumb_file = output_path / "thumbnail_suggestions.txt"
        with open(thumb_file, 'w', encoding='utf-8') as f:
            f.write("THUMBNAIL TEXT SUGGESTIONS:\n\n")
            for i, suggestion in enumerate(metadata['thumbnail_suggestions'], 1):
                f.write(f"{i}. {suggestion}\n")
        print(f"💾 Thumbnail suggestions saved: {thumb_file}")

        # Complete metadata JSON
        complete_file = output_path / "youtube_metadata.json"
        with open(complete_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"💾 Complete metadata saved: {complete_file}")

        return metadata

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def display_youtube_content(metadata):
    """Display generated YouTube content."""

    print("\n" + "=" * 60)
    print("📺 YOUTUBE CONTENT")
    print("=" * 60)

    print(f"\n📌 TITLE:")
    print(f"   {metadata['title']}")
    print(f"   (Length: {len(metadata['title'])} characters)")

    print(f"\n📝 DESCRIPTION:")
    print("   " + "-" * 56)
    for line in metadata['description'].split('\n'):
        print(f"   {line}")
    print("   " + "-" * 56)

    print(f"\n🎨 THUMBNAIL TEXT OPTIONS:")
    for i, suggestion in enumerate(metadata['thumbnail_suggestions'], 1):
        print(f"   {i}. \"{suggestion}\"")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    analysis_file = "output/audio_analysis.json"
    output_dir = "output"

    if not Path(analysis_file).exists():
        print(f"❌ Error: {analysis_file} not found")
        print("Please run analyze_for_youtube.py first")
        exit(1)

    # Generate YouTube content
    metadata = generate_youtube_metadata(analysis_file, output_dir)

    if metadata:
        # Display
        display_youtube_content(metadata)

        print("\n✅ YouTube content generation complete!")
        print(f"📁 All files saved to: {output_dir}/")
