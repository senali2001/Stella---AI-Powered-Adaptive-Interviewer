import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")

segments, info = model.transcribe("test.mp4", language="en")

print("Detected language:", info.language)
for segment in segments:
    print(segment.text)
