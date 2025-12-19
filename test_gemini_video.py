"""
Test script for Gemini 2.0 Flash video generation capabilities.
This will help us determine if Gemini can generate dance videos suitable for our app.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

try:
    from google import genai
    NEW_API = True
except ImportError:
    import google.generativeai as genai
    NEW_API = False

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Set your API key
OUTPUT_DIR = Path("test_output")
OUTPUT_DIR.mkdir(exist_ok=True)


def test_gemini_video_generation():
    """Test Gemini's video generation with dance-related prompts."""

    if not GEMINI_API_KEY:
        print("ERROR: Please set GEMINI_API_KEY environment variable")
        print("   Get your key from: https://aistudio.google.com/app/apikey")
        return

    # Configure Gemini
    if NEW_API:
        client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        genai.configure(api_key=GEMINI_API_KEY)

    print("🎬 Testing Gemini 2.0 Flash Video Generation\n")
    print("=" * 60)

    # Test prompts - varying complexity
    test_prompts = [
        {
            "name": "simple_dance",
            "prompt": "A person dancing hip-hop style with energetic movements, full body shot, 4 seconds",
            "duration": 4
        },
        {
            "name": "low_energy_sway",
            "prompt": "A dancer doing slow body waves and gentle swaying, smooth movements, medium shot, 5 seconds",
            "duration": 5
        },
        {
            "name": "high_energy_jump",
            "prompt": "A dancer jumping and doing dynamic hip-hop moves with high energy, full body, 4 seconds",
            "duration": 4
        }
    ]

    results = []

    for i, test in enumerate(test_prompts, 1):
        print(f"\nTest {i}/{len(test_prompts)}: {test['name']}")
        print(f"   Prompt: {test['prompt']}")
        print("   Status: Generating...", end="", flush=True)

        try:
            # Check which models support video generation
            # Note: As of now, Gemini video generation might be:
            # - In beta/limited access
            # - Using imagen-3 or veo models
            # - Available through different API endpoints

            if NEW_API:
                # Try new API
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=test['prompt']
                )
            else:
                # Try old API
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                response = model.generate_content(
                    test['prompt'],
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 100,
                    }
                )

            print(" WARNING: TEXT RESPONSE (Video gen may not be available)")
            response_text = response.text if hasattr(response, 'text') else str(response)
            print(f"   Response: {response_text[:100]}...")

            results.append({
                "test": test['name'],
                "status": "text_only",
                "note": "Video generation not available in current API"
            })

        except Exception as e:
            print(f" ERROR")
            print(f"   {str(e)}")
            results.append({
                "test": test['name'],
                "status": "failed",
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY\n")

    for result in results:
        print(f"- {result['test']}: {result['status']}")
        if 'error' in result:
            print(f"  Error: {result['error']}")
        if 'note' in result:
            print(f"  Note: {result['note']}")

    print("\n" + "=" * 60)
    print("IMPORTANT FINDINGS:\n")
    print("Gemini video generation is currently:")
    print("1. In limited preview/beta access")
    print("2. Might require waitlist approval")
    print("3. May be available through Google AI Studio UI but not API yet")
    print("\nALTERNATIVE VIDEO GENERATION OPTIONS TO TEST:")
    print("   - Runway Gen-2/Gen-3 API")
    print("   - Replicate (stability-ai/stable-video-diffusion)")
    print("   - Pika Labs (if API available)")
    print("   - Luma Dream Machine API")
    print("\nNEXT STEPS:")
    print("   1. Check Google AI Studio for video generation access")
    print("   2. Consider alternative video APIs")
    print("   3. Or pivot to template-based approach with real dance clips")


def check_available_models():
    """List available Gemini models and their capabilities."""

    if not GEMINI_API_KEY:
        print("ERROR: Set GEMINI_API_KEY first")
        return

    print("\nAvailable Gemini Models:\n")

    try:
        if NEW_API:
            client = genai.Client(api_key=GEMINI_API_KEY)
            models = client.models.list()
        else:
            genai.configure(api_key=GEMINI_API_KEY)
            models = genai.list_models()

        for model in models:
            model_name = model.name if hasattr(model, 'name') else str(model)
            print(f"- {model_name}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"  Supported methods: {model.supported_generation_methods}")
            if hasattr(model, 'input_token_limit'):
                print(f"  Input token limit: {model.input_token_limit}")
            print()
    except Exception as e:
        print(f"ERROR listing models: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("GEMINI VIDEO GENERATION TEST")
    print("=" * 60)

    # First check available models
    check_available_models()

    # Then try video generation
    test_gemini_video_generation()

    print("\n" + "=" * 60)
    print("Test script complete!")
    print("=" * 60)
