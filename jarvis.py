"""
Jarvis — Voice interface for Claude
Press Enter to start recording, speak, press Enter again to stop.
"""

import os
import sys
import tempfile
import threading
import queue
import wave
import anthropic
import pyaudio
import whisper
import pyttsx3

# ── Config ────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL             = "claude-sonnet-4-6"
SAMPLE_RATE       = 16000
CHANNELS          = 1
CHUNK             = 1024
WHISPER_MODEL     = "base"  # tiny, base, small, medium, large

SYSTEM_PROMPT = """You are Jarvis, a helpful and concise voice assistant.
Keep responses short and conversational — you are being read aloud, so avoid
bullet points, markdown, or long lists. Speak naturally."""

# ── Setup ─────────────────────────────────────────────────────────────────────

if not ANTHROPIC_API_KEY:
    print("Error: ANTHROPIC_API_KEY environment variable not set.")
    print("Run: export ANTHROPIC_API_KEY=your-key-here")
    sys.exit(1)

print("Loading Whisper model... (first run downloads it)")
stt_model = whisper.load_model(WHISPER_MODEL)
print("Whisper ready.")

tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 175)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
conversation_history = []

# ── Functions ─────────────────────────────────────────────────────────────────

def record_audio() -> str:
    """Record audio until user presses Enter, return path to wav file."""
    audio_queue = queue.Queue()
    stop_event  = threading.Event()

    def capture():
        pa     = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        frames = []
        count  = 0
        while not stop_event.is_set():
            frames.append(stream.read(CHUNK, exception_on_overflow=False))
            count += 1
            if count % 20 == 0:
                print("  🔴 still recording...", flush=True)
        stream.stop_stream()
        stream.close()
        pa.terminate()
        audio_queue.put(frames)

    thread = threading.Thread(target=capture, daemon=True)
    thread.start()
    print("  🎤  Recording started! Speak now, then press Enter to stop.")
    input()
    stop_event.set()
    thread.join()

    frames = audio_queue.get()
    print(f"  Captured {len(frames)} audio chunks.")
    tmp    = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    with wave.open(tmp.name, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # paInt16 = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(frames))
    return tmp.name


def transcribe(wav_path: str) -> str:
    result = stt_model.transcribe(wav_path, fp16=False)
    os.unlink(wav_path)
    return result["text"].strip()


def ask_claude(text: str) -> str:
    conversation_history.append({"role": "user", "content": text})
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=conversation_history,
    )
    reply = response.content[0].text
    conversation_history.append({"role": "assistant", "content": reply})
    return reply


def speak(text: str):
    tts_engine.say(text)
    tts_engine.runAndWait()


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    print("\n=== Jarvis is ready ===")
    print("Press Enter to start recording. Type 'quit' to exit.\n")
    speak("Jarvis online. How can I help you?")

    while True:
        try:
            cmd = input("Press Enter to speak (or type 'quit'): ").strip().lower()
            if cmd == "quit":
                speak("Goodbye.")
                break

            wav_path = record_audio()

            print("  Transcribing...")
            user_text = transcribe(wav_path)
            if not user_text:
                print("  (nothing heard, try again)\n")
                continue
            print(f"  You: {user_text}")

            print("  Thinking...")
            reply = ask_claude(user_text)
            print(f"  Jarvis: {reply}\n")

            speak(reply)

        except KeyboardInterrupt:
            speak("Goodbye.")
            break


if __name__ == "__main__":
    main()
