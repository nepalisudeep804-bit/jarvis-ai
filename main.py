"""JARVIS AI - Termux terminal app.

Chalane ke liye:  python main.py
"""
import getpass
import logging

from jarvis.assistant import Assistant
from jarvis.config import HOME_DIR, Settings
from jarvis.gemini_service import AIStatus, GeminiService
from jarvis.live_info import LiveInfo
from jarvis.memory import Memory
from jarvis.voice import Voice, VoiceUnavailable

HELP = """
Commands:
  v                  Bolkar command dein (voice)
  /test              Gemini connection check karein
  /status            AI status aur key ka masked view
  /setkey            Gemini API key save karein (hidden input)
  /clearkey          API key hatayein (confirmation ke saath)
  /settings          Saari settings dekhein
  /set <key> <val>   Setting badlein, jaise: /set affection_level 3
  /resetsettings     Settings default par (confirmation ke saath)
  /memory on|off|clear
  /history           Recent chat dekhein
  /history clear     Chat history saaf karein
  /speak on|off      Jawab bolkar sunana on/off
  /stop              Bolna abhi rokein
  /help              Ye menu
  /exit              Band karein
Kuch bhi likhiye: jaise 'torch on karo', 'mausam kaisa hai', 'Arijit Singh ka romantic gaana chalao'.
"""


def setup_logging():
    HOME_DIR.mkdir(parents=True, exist_ok=True)
    # API key kabhi log nahi hoti; sirf events aur errors.
    logging.basicConfig(filename=HOME_DIR / "jarvis.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")


def confirm(prompt):
    return input(f"{prompt} (yes/no): ").strip().lower() == "yes"


def main():
    setup_logging()
    settings = Settings()
    memory = Memory(HOME_DIR / "memory.json", enabled=settings.get("memory_enabled"))
    gemini = GeminiService(settings)
    assistant = Assistant(settings, memory, gemini, LiveInfo())
    voice = Voice(language=settings.get("tts_language"), rate=settings.get("speech_rate"))
    speak_on = True
    name = settings.get("nickname")

    print(f"{name} ready hai. '/help' se commands dekhein. Bolne ke liye 'v' likhein.")
    while True:
        try:
            raw = input("Aap > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            voice.stop()
            break
        if not raw:
            continue

        if raw.startswith("/"):
            parts = raw.split(maxsplit=2)
            cmd = parts[0].lower()
            if cmd == "/exit":
                print("Bye!")
                break
            elif cmd == "/help":
                print(HELP)
            elif cmd == "/status":
                print(f"AI: {gemini.status.value} | key: {settings.masked_key()} | model: {settings.get('gemini_model')}")
                if gemini.last_error:
                    print(f"Last error: {gemini.last_error}")
            elif cmd == "/test":
                ok, msg = gemini.test_connection()
                print(("✅ " if ok else "❌ ") + msg)
            elif cmd == "/setkey":
                try:
                    settings.set_api_key(getpass.getpass("Gemini API key (hidden): "))
                    print("Key save ho gayi. '/test' se check karein.")
                except ValueError as e:
                    print(e)
            elif cmd == "/clearkey":
                if confirm("API key hata dein?"):
                    settings.clear_api_key()
                    gemini.status = AIStatus.DISCONNECTED
                    print("API key hata di gayi.")
            elif cmd == "/settings":
                for k, v in settings.data.items():
                    print(f"{k} = {v}")
                print(f"api_key = {settings.masked_key()}")
            elif cmd == "/set":
                if len(parts) < 3:
                    print("Usage: /set <key> <value>. Keys dekhne ke liye /settings")
                else:
                    try:
                        value = settings.set(parts[1], parts[2])
                        memory.enabled = settings.get("memory_enabled")
                        voice.language = settings.get("tts_language")
                        voice.rate = settings.get("speech_rate")
                        print(f"{parts[1]} = {value}")
                    except (KeyError, ValueError) as e:
                        print(f"Galat: {e}")
            elif cmd == "/resetsettings":
                if confirm("Saari settings default par reset karein?"):
                    settings.reset()
                    memory.enabled = settings.get("memory_enabled")
                    print("Settings reset ho gayi.")
            elif cmd == "/memory":
                arg = parts[1].lower() if len(parts) > 1 else ""
                if arg in ("on", "off"):
                    settings.set("memory_enabled", arg == "on")
                    memory.enabled = arg == "on"
                    print(f"Memory {arg}.")
                elif arg == "clear":
                    if confirm("Saari memory (chat, preferences, tasks) delete karein?"):
                        memory.clear_all()
                        print("Memory saaf ho gayi.")
                else:
                    print(f"Memory: {'on' if memory.enabled else 'off'}")
            elif cmd == "/history":
                if len(parts) > 1 and parts[1].lower() == "clear":
                    memory.clear_history()
                    print("History saaf ho gayi.")
                else:
                    for m in memory.recent(10):
                        print(f"{m['role']}: {m['text']}")
            elif cmd == "/speak":
                speak_on = not (len(parts) > 1 and parts[1].lower() == "off")
                print(f"Bolkar jawab: {'on' if speak_on else 'off'}")
            elif cmd == "/stop":
                voice.stop()
                print("Bolna rok diya.")
            else:
                print("Aisa command nahi hai. '/help' dekhein.")
            continue

        heard_by_voice = False
        if raw.lower() == "v":
            try:
                heard = voice.listen()
            except VoiceUnavailable as e:
                print(e)
                continue
            if not heard:
                print("Kuch sunai nahi diya.")
                continue
            print(f"Aap (voice) > {heard}")
            raw = heard
            heard_by_voice = True

        reply = assistant.handle(raw)
        print(f"{name} > {reply}")
        if speak_on:
            try:
                voice.speak(reply)
            except KeyboardInterrupt:
                voice.stop()
                print("(bolna rok diya)")
        logging.info("turn handled (voice=%s)", heard_by_voice)


if __name__ == "__main__":
    main()
