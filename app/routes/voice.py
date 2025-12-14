from fastapi import APIRouter, UploadFile, File, HTTPException
import speech_recognition as sr
import tempfile

router = APIRouter()

@router.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    """
    Accepts audio file (wav recommended).
    Returns recognized Bangla text.
    """
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio uploaded")

    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp.flush()

        with sr.AudioFile(tmp.name) as source:
            audio_data = recognizer.record(source)

        try:
            # bn-BD Bangla
            text = recognizer.recognize_google(audio_data, language="bn-BD")
            return {"text_bn": text}
        except sr.UnknownValueError:
            return {"text_bn": "", "error": "Could not understand audio"}
        except sr.RequestError as e:
            raise HTTPException(status_code=502, detail=f"STT request failed: {e}")
