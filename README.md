# Jarvis

A voice-activated AI assistant powered by Claude. Speak your question, Jarvis listens, thinks, and talks back — just like the Iron Man movies.

---

## How It Works

```
You speak → Whisper transcribes locally → Claude API thinks → macOS say reads the response aloud
```

- **Speech-to-text** — OpenAI Whisper runs entirely on your machine. No audio is sent anywhere.
- **AI brain** — Anthropic Claude (claude-sonnet-4-6) handles the conversation via API.
- **Text-to-speech** — macOS built-in `say` command with the Daniel (British) voice.
- **Conversation memory** — Jarvis remembers the full conversation so you can follow up naturally.

---

## Requirements

- macOS (uses the built-in `say` command for speech)
- Python 3.11 or newer (Homebrew recommended — Anaconda has known pip issues)
- An [Anthropic API key](https://console.anthropic.com)
- Homebrew

---

## Installation

### 1. Install system dependencies

```bash
brew install ffmpeg portaudio
```

### 2. Create a virtual environment

```bash
/opt/homebrew/bin/python3.13 -m venv ~/Projects/jarvis/venv
source ~/Projects/jarvis/venv/bin/activate
```

> **Important:** Use Homebrew Python, not Anaconda. Anaconda's pip has a version parsing bug that breaks installation.

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

The first run will download the Whisper `base` model (~140 MB). This only happens once.

### 4. Set your API key

```bash
export ANTHROPIC_API_KEY=your-key-here
```

To make this permanent, add it to your `~/.zshrc`:
```bash
echo 'export ANTHROPIC_API_KEY=your-key-here' >> ~/.zshrc
source ~/.zshrc
```

---

## Running Jarvis

```bash
source ~/Projects/jarvis/venv/bin/activate
python3 jarvis.py
```

Jarvis will say **"Jarvis online. How can I help you?"** when ready.

---

## Usage

| Action | What to do |
|---|---|
| Ask a question | Press **Enter**, speak, press **Enter** again to stop |
| Follow up | Just press Enter again — conversation history is maintained |
| Exit | Type `quit` and press Enter |
| Force quit | Press **Ctrl+C** |

---

## Configuration

All options are at the top of `jarvis.py`:

| Setting | Default | Description |
|---|---|---|
| `MODEL` | `claude-sonnet-4-6` | Claude model to use |
| `WHISPER_MODEL` | `base` | Whisper model size — `tiny` is faster, `medium`/`large` are more accurate |
| `SAMPLE_RATE` | `16000` | Audio sample rate in Hz |

### Changing the voice

Jarvis uses the **Daniel** (British English) voice by default. To use a different voice, edit the `speak()` function in `jarvis.py`:

```python
def speak(text: str):
    subprocess.run(["say", "-v", "Daniel", "-r", "175", text])
```

Replace `Daniel` with any voice from:
```bash
say -v '?'
```

Good male English options: `Daniel` (British), `Reed (English (US))`, `Rocko (English (US))`, `Fred`

---

## Troubleshooting

**PyAudio install fails**
```bash
brew install portaudio
pip install pyaudio
```
If still failing, make sure you are using Homebrew Python, not Anaconda.

**"ANTHROPIC_API_KEY not set" error**
```bash
export ANTHROPIC_API_KEY=your-key-here
```

**Credit balance error from Anthropic**
Top up your API credits at [console.anthropic.com](https://console.anthropic.com) → Plans & Billing.

**Nothing heard after recording**
Make sure your Mac microphone is enabled for Terminal in System Settings → Privacy & Security → Microphone.

---

## Dependencies

| Package | Purpose |
|---|---|
| `anthropic` | Claude API client |
| `openai-whisper` | Local speech-to-text |
| `pyaudio` | Microphone input |
| macOS `say` | Text-to-speech (built-in, no install needed) |

---

## License

Personal use.
