"""
Speech-to-text using faster-whisper.
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from faster_whisper import WhisperModel

_model = None


def get_model(size="small"):
    global _model
    if _model is None:
        _model = WhisperModel(size, device="cpu", compute_type="int8")
    return _model


def transcribe(audio_path, size="small"):
    model = get_model(size)
    segments, info = model.transcribe(audio_path, language="en", word_timestamps=True)

    words = []
    full_text = []
    for seg in segments:
        full_text.append(seg.text.strip())
        if seg.words:
            for w in seg.words:
                words.append({"word": w.word, "start": w.start, "end": w.end})

    transcript = " ".join(full_text).strip()
    duration = info.duration
    speaking_rate = (len(words) / duration * 60) if duration > 0 else 0.0

    return {
        "transcript": transcript,
        "words": words,
        "duration_sec": duration,
        "speaking_rate_wpm": speaking_rate,
        "language": info.language,
    }