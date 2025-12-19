# Video Generation Testing - Proof of Concept

## Purpose
Test if Gemini 2.0 Flash (or alternatives) can generate dance videos suitable for our music-to-dance app.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements_test.txt
```

### 2. Get API Keys

**Gemini API Key:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Get API Key" or "Create API Key"
4. Copy your key

**Anthropic API Key (for later):**
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up/login
3. Navigate to API Keys
4. Create a new key

### 3. Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API keys
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

### 4. Run Test
```bash
python test_gemini_video.py
```

## What This Tests

The script will:
1. ✅ List available Gemini models
2. ✅ Check which models support video generation
3. ✅ Attempt to generate 3 test dance video clips with different prompts:
   - Simple hip-hop dance (4 sec)
   - Low energy body waves (5 sec)
   - High energy jumping (4 sec)
4. ✅ Report results and capabilities

## Expected Outcomes

### Scenario A: Video Generation Works ✨
- You'll get video files in `test_output/` folder
- We can proceed with building the full automated pipeline
- **Action**: Build the complete app!

### Scenario B: Video Gen Limited/Beta 🔒
- Gemini API might not support video yet (API-wise)
- May work in Google AI Studio UI but not programmatically
- **Action**:
  - Check if you can access video gen through AI Studio manually
  - Or test alternative APIs (Runway, Replicate, etc.)

### Scenario C: Video Gen Not Available ❌
- Feature not accessible yet
- **Action**: Pivot to template-based approach or wait for API access

## Alternative Video Generation Options

If Gemini doesn't work, we can test:

### 1. Replicate (Stable Video Diffusion)
```python
# Install: pip install replicate
import replicate

output = replicate.run(
    "stability-ai/stable-video-diffusion",
    input={"image": "character.jpg", "motion_bucket_id": 127}
)
```

### 2. Runway Gen-2/Gen-3
- Check [Runway API](https://runwayml.com/) for access
- High quality but may be expensive

### 3. Pika Labs
- Check for API access at [pika.art](https://pika.art)

### 4. Local Generation (Advanced)
- ComfyUI + AnimateDiff
- Requires GPU (NVIDIA with 12GB+ VRAM)

## Next Steps Based on Results

**If video generation works:**
→ Run `test_audio_analysis.py` (we'll create this next)
→ Build full automated pipeline

**If video generation doesn't work:**
→ Decide between:
  - Template-based approach (pre-recorded dance clips)
  - Wait for better API access
  - Use alternative video generation service

## Questions?

After running the test, we'll know:
- ✅ Can we generate dance videos programmatically?
- ✅ What's the quality like?
- ✅ How long does each clip take?
- ✅ What are the limitations (duration, style, etc.)?

This will inform our final architecture decision!
