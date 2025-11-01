import sys
import threading
import subprocess
import queue
import traceback
import time

# Single consumer queue + worker thread to serialize all speech requests.
_speech_queue = queue.Queue()
_speech_thread = None


def _speech_worker():
    print('[voice] worker: started')
    while True:
        item = _speech_queue.get()
        if item is None:
            break
        text = item
        try:
            print('[voice] worker: processing:', repr(text))
            # Use PowerShell speech synthesis directly on Windows
            if sys.platform.startswith("win"):
                try:
                    t = text.replace('"', '\\"')
                    cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{t}")'
                    subprocess.run([
                        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print('[voice] worker: done (PowerShell)')
                    continue
                except Exception as e:
                    print('[voice] worker: PowerShell speech failed:', str(e))
            
            # Fall back to pyttsx3 if PowerShell fails or not on Windows
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                print('[voice] worker: done (pyttsx3)')
            except Exception as e:
                print('[voice] worker: pyttsx3 failed:', str(e))
            # Fallback to PowerShell TTS on Windows
            if sys.platform.startswith("win"):
                try:
                    t = text.replace('"', '\\"')
                    cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{t}")'
                    subprocess.run([
                        "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    # swallow fallback errors
                    pass
        finally:
            try:
                _speech_queue.task_done()
            except Exception:
                pass


def _ensure_thread():
    global _speech_thread
    if _speech_thread is None or not _speech_thread.is_alive():
        _speech_thread = threading.Thread(target=_speech_worker, daemon=True)
        _speech_thread.start()


print('[voice] module loaded')


def speak(text: str, voice_enabled: bool = True):
    """Queue a text to be spoken. Returns immediately."""
    if not voice_enabled:
        return
    _ensure_thread()
    try:
        _speech_queue.put(text)
    except Exception:
        print("[voice] failed to enqueue text")


def wait_until_done(timeout: float | None = None):
    """Block until the speech queue is empty and the worker thread has finished processing current items.
    If timeout is provided, wait at most that many seconds.
    """
    start = time.time()
    # Wait for queue empty
    while True:
        try:
            empty = _speech_queue.empty()
        except Exception:
            empty = True
        if empty:
            break
        if timeout is not None and (time.time() - start) >= timeout:
            return False
        time.sleep(0.05)
    # Give the worker a short moment to finish
    if _speech_thread is not None and _speech_thread.is_alive():
        # Wait a short period for the thread to settle
        waited = 0.0
        while _speech_thread.is_alive():
            if timeout is not None and (time.time() - start) >= timeout:
                return False
            time.sleep(0.05)
            waited += 0.05
    return True


def speak_sync(text: str, voice_enabled: bool = True):
    """Speak text synchronously in the current thread. Returns when finished.
    This bypasses the background worker and is useful for short blocking calls where
    the caller wants to ensure speech completes before continuing (for example,
    before quitting the application window).
    """
    if not voice_enabled:
        return
    try:
        # Prefer PowerShell on Windows for reliable System.Speech synthesis
        if sys.platform.startswith("win"):
            t = text.replace('"', '\\"')
            cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{t}")'
            subprocess.run([
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
    except Exception:
        pass
    # Fall back to pyttsx3 (may block until finished)
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        # If all else fails, silently return
        return