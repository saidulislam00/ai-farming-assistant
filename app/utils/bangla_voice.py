from gtts import gTTS
import io

def tts_to_mp3_bytes(text: str, lang: str = "bn") -> bytes:
    fp = io.BytesIO()
    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(fp)
    return fp.getvalue()
