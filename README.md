# Dancing Video Generator

AI-powered music-to-dance video generation app. Upload music and get synchronized dance videos!

## 🎯 Project Status: Testing Phase

Currently testing video generation capabilities before building the full app.

## 📋 What's Been Done

- ✅ Video generation API testing (Gemini/VEO)
- ✅ Test scripts for audio analysis
- ✅ Test scripts for choreography generation (Claude)
- ⏸️ Evaluating best approach (AI video vs templates)

## 🧪 Test Scripts

1. **test_gemini_video.py** - Tests Google's Gemini/VEO video generation
2. **test_veo_video.py** - Specifically tests VEO models
3. **test_audio_analysis.py** - Analyzes MP3 files for beat/section detection
4. **test_claude_choreography.py** - Tests Claude's choreography prompt generation

## 🚀 Quick Start (Testing)

### Setup
```bash
# Install dependencies
pip install -r requirements_test.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your keys
```

### Run Tests
```bash
# Test video generation
python test_gemini_video.py

# Test audio analysis (requires MP3 file)
python test_audio_analysis.py

# Test choreography generation
python test_claude_choreography.py
```

## 📖 Documentation

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Complete testing instructions
- [TEST_RESULTS.md](TEST_RESULTS.md) - Findings and recommendations
- [Detailed Implementation Plan Music-.txt](Detailed%20Implementation%20Plan%20Music-.txt) - Original full plan

## 🔑 Required API Keys

- **GEMINI_API_KEY** - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **ANTHROPIC_API_KEY** - Get from [Anthropic Console](https://console.anthropic.com/)

## 🎬 Planned Features

- Music analysis (BPM, sections, energy detection)
- AI choreography planning with Claude
- Video generation (evaluating options)
- Automatic video assembly with FFmpeg
- Web interface for uploads

## 📊 Current Findings

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed analysis of video generation options.

**TL;DR**: VEO video generation exists but requires complex setup. Evaluating alternatives.

## 🛠️ Tech Stack (Planned)

- **Backend**: Python + FastAPI
- **Audio Analysis**: librosa
- **Choreography**: Claude API (Anthropic)
- **Video Generation**: TBD (testing options)
- **Video Assembly**: FFmpeg
- **Frontend**: React or simple HTML

## 📝 License

TBD

## 👤 Author

Built with Claude Code
