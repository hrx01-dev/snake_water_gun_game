import sys
import threading
import subprocess

_have_pyttsx3 = False
_use_powershell_tts = False

try:
    import pyttsx3
    _have_pyttsx3 = True
except Exception:
    _have_pyttsx3 = False
    if sys.platform.startswith("win"):
        _use_powershell_tts = True

def speak(text: str, voice_enabled: bool = True):
    if not voice_enabled:
        return
        
    def _speak():
        # Try pyttsx3 first
        if _have_pyttsx3:
            try:
                import pyttsx3 as _py
                engine = _py.init()
                engine.say(text)
                engine.runAndWait()
                return
            except Exception:
                pass
                
        # Fallback to PowerShell TTS
        if _use_powershell_tts and sys.platform.startswith("win"):
            try:
                t = text.replace('"', '\\"')
                cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{t}")'
                subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    threading.Thread(target=_speak, daemon=True).start()