"""
Test VEO (Google's video generation model) for dance video creation.
VEO 3 is Google's latest video generation model.
"""

import sys
import os
from pathlib import Path
import time

# Fix Windows console encoding
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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OUTPUT_DIR = Path("test_output")
OUTPUT_DIR.mkdir(exist_ok=True)


def test_veo_video_generation():
    """Test VEO 3 video generation with a dance prompt."""

    if not GEMINI_API_KEY:
        print("ERROR: Please set GEMINI_API_KEY environment variable")
        return

    print("=" * 60)
    print("VEO 3 VIDEO GENERATION TEST")
    print("=" * 60)

    # Configure client
    if NEW_API:
        client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        genai.configure(api_key=GEMINI_API_KEY)

    # Test prompt - simple dance movement
    test_prompt = "A person dancing hip-hop style with energetic arm movements and footwork, full body shot, urban setting, 4 seconds"

    print(f"\nPrompt: {test_prompt}\n")
    print("Attempting to generate video with VEO 3.1...")

    try:
        if NEW_API:
            # Use new API
            print("\nUsing new google.genai API...")

            # Try VEO 3.1 (latest)
            model_name = "veo-3.1-fast-generate-preview"
            print(f"Model: {model_name}")

            # VEO uses predict/predictLongRunning methods
            response = client.models.generate_content(
                model=model_name,
                contents=test_prompt
            )

            print("\nResponse:", response)

        else:
            # Use old API
            print("\nUsing old google.generativeai API...")

            model = genai.GenerativeModel("veo-3.1-fast-generate-preview")
            response = model.generate_content(test_prompt)

            print("\nResponse:", response)

        # Check if we got a video
        if hasattr(response, 'video'):
            print("\nSUCCESS! Video generated!")
            # Save video
            video_path = OUTPUT_DIR / "test_dance_veo.mp4"
            with open(video_path, 'wb') as f:
                f.write(response.video)
            print(f"Saved to: {video_path}")
        else:
            print("\nVideo not found in response. Response type:", type(response))
            if hasattr(response, 'text'):
                print("Text response:", response.text[:200])

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

        print("\n" + "=" * 60)
        print("EXPLANATION:")
        print("=" * 60)
        print("VEO video generation might require:")
        print("1. Special API access (waitlist/approval)")
        print("2. Different API endpoint (not via generateContent)")
        print("3. Google Cloud Project setup")
        print("4. Vertex AI API instead of AI Studio API")

        print("\nALTERNATIVE OPTIONS:")
        print("1. Use Runway Gen-3 API (more accessible)")
        print("2. Use Replicate for video generation")
        print("3. Use template-based approach with real dance clips")
        print("4. Check Google AI Studio UI to see if VEO is available there")


def check_veo_access():
    """Check if we have access to VEO models."""

    if not GEMINI_API_KEY:
        print("ERROR: Set GEMINI_API_KEY first")
        return

    print("\nChecking VEO Model Access...\n")

    try:
        if NEW_API:
            client = genai.Client(api_key=GEMINI_API_KEY)
            models = client.models.list()
        else:
            genai.configure(api_key=GEMINI_API_KEY)
            models = genai.list_models()

        veo_models = []
        for model in models:
            model_name = model.name if hasattr(model, 'name') else str(model)
            if 'veo' in model_name.lower():
                veo_models.append({
                    'name': model_name,
                    'methods': model.supported_generation_methods if hasattr(model, 'supported_generation_methods') else 'unknown'
                })

        if veo_models:
            print(f"Found {len(veo_models)} VEO models:\n")
            for veo in veo_models:
                print(f"- {veo['name']}")
                print(f"  Methods: {veo['methods']}\n")
        else:
            print("No VEO models found in your account.")
            print("You may need special access or different API setup.")

    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    check_veo_access()
    test_veo_video_generation()

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
