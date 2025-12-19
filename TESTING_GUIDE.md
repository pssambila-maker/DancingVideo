# Testing Guide - Music to Dance Video POC

This guide walks you through testing each component before building the full system.

## 🎯 Goal
Verify that our core technologies (Gemini video gen, audio analysis, Claude choreography) work well enough to build the complete app.

---

## 📋 Step-by-Step Testing

### Step 0: Setup ⚙️

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements_test.txt
   ```

2. **Get API Keys:**
   - **Gemini**: https://aistudio.google.com/app/apikey
   - **Anthropic/Claude**: https://console.anthropic.com/

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

---

### Step 1: Test Gemini Video Generation 🎬

**Purpose:** Verify Gemini can generate dance videos programmatically

```bash
python test_gemini_video.py
```

**What to look for:**
- ✅ Can we access Gemini API?
- ✅ Does it support video generation?
- ✅ What models are available?

**Expected outcome:**
- **Best case:** Video files are generated in `test_output/`
- **Likely case:** Text response indicating video gen not available via API yet
- **Action:** If video gen doesn't work, we'll test alternatives (Runway, Replicate, etc.)

**Decision point:**
- ✅ Video works → Proceed to Step 2
- ❌ Video doesn't work → Test alternative services or pivot to template-based approach

---

### Step 2: Test Audio Analysis 🎵

**Purpose:** See how many clips we'll need for a typical song

**Prepare a test file:**
1. Get any MP3 file (your favorite song, 2-4 minutes long)
2. Place it in this directory
3. Name it `test_audio.mp3`

```bash
python test_audio_analysis.py
```

**What you'll see:**
- Song duration, BPM, beats
- Detected sections (intro, verse, chorus, etc.)
- **How many video clips needed** (this is key!)
- Estimated time and cost to generate all clips

**Example output:**
```
Duration: 210 seconds (3.5 minutes)
BPM: 128
Total clips needed: 24

Estimated Generation Time: 12-48 minutes
Estimated Cost: $2.40-$24.00 (depending on service)
```

**Decision point:**
- If clips needed is reasonable (15-30) → Good!
- If too many clips (50+) → We may need to adjust clip duration

---

### Step 3: Test Claude Choreography 🎭

**Purpose:** See what kind of video prompts Claude generates

```bash
python test_claude_choreography.py
```

**What you'll see:**
- Claude generates specific video prompts for each song section
- Prompts include exact movements, camera angles, intensity
- JSON output saved to `test_output/choreography_prompts.json`

**Example prompt:**
```
"A dancer in urban streetwear doing quick footwork with arms
swinging side to side, energetic hip-hop moves, studio lighting,
full body shot"
```

**Evaluation:**
- ✅ Are prompts specific enough?
- ✅ Do they match the energy levels?
- ✅ Would these work for video generation?

**Decision point:**
- Good prompts → Ready to test actual video generation
- Vague prompts → Adjust system prompt and retry

---

## 🧪 Integration Test (Optional)

Once Steps 1-3 work individually, test the full flow:

1. Run audio analysis on a test song
2. Feed results to Claude for choreography
3. Take 1-2 prompts and manually test video generation
4. Evaluate the final video quality

**If this works well → Build the full automated pipeline!**

---

## 📊 Decision Matrix

After testing, use this to decide next steps:

| Scenario | Video Gen | Audio | Claude | Action |
|----------|-----------|-------|--------|--------|
| ✅ All work | Works | ✅ | ✅ | **Build full app!** |
| ⚠️ Video limited | Limited/Beta | ✅ | ✅ | Test alternatives or wait for API access |
| ⚠️ Video expensive | Works but $$$$ | ✅ | ✅ | Consider template-based approach |
| ❌ Video unavailable | Not available | ✅ | ✅ | Pivot to template-based or wait |

---

## 🔄 Alternative Approaches

### If Gemini video doesn't work:

#### Option A: Test Replicate (Stable Video Diffusion)
```bash
pip install replicate
```

Create `test_replicate_video.py`:
```python
import replicate

output = replicate.run(
    "stability-ai/stable-video-diffusion:...",
    input={"image": "dancer.jpg", "motion_bucket_id": 127}
)
```

#### Option B: Template-Based (No AI Video Gen)
- Build a library of 20-30 pre-recorded dance clips
- Claude matches clips to music sections
- FFmpeg assembles them
- **Pros:** Fast, reliable, cheap
- **Cons:** Less "AI magic", limited variety

#### Option C: Manual Hybrid
- Generate analysis + choreography automatically
- Export prompts for manual video generation
- User generates videos in Gemini/Runway UI
- Import to DaVinci for assembly

---

## ✅ Success Criteria

You're ready to build the full app if:
1. ✅ You can generate at least 1 dance video clip programmatically
2. ✅ Audio analysis detects sections and energy correctly
3. ✅ Claude generates specific, usable video prompts
4. ✅ The quality of generated videos meets your expectations
5. ✅ The cost/time per video is acceptable

---

## 📞 Next Steps

After testing, report back:

1. **What worked?**
2. **What didn't work?**
3. **What's the video quality like?**
4. **How long did each clip take?**
5. **What's your estimated cost per complete video?**

Based on your answers, we'll either:
- ✅ Build the full automated pipeline
- 🔄 Adjust the approach
- 🔀 Pivot to a different architecture

---

## 💡 Pro Tips

- **Start small:** Test with a 30-second audio clip first
- **Check quality:** Generate 2-3 test videos before committing
- **Monitor costs:** Some APIs charge per generation
- **Be patient:** Video generation can take 30-120 seconds per clip

Good luck with testing! 🚀
