"""
Load the trained CNN-LSTM checkpoint and predict interview-relevant
affective state + confidence from a raw audio file.
"""
import numpy as np
import torch
import librosa

from ai.training.train_ser import CNNLSTM  # reuse the same architecture class

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SR = 16000
N_MELS = 128
N_FFT = 1024
HOP_LENGTH = 256
CLIP_SECONDS = 3.0

_model = None
_classes = None


def _load_model():
    global _model, _classes
    if _model is None:
        ckpt = torch.load("ai/models/ser_cnn_lstm.pt", map_location=DEVICE)
        _classes = ckpt["label_classes"]
        _model = CNNLSTM(n_classes=len(_classes)).to(DEVICE)
        _model.load_state_dict(ckpt["model_state"])
        _model.eval()
    return _model, _classes


def _extract_logmel(y, sr=SR):
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH, n_mels=N_MELS)
    log_mel = librosa.power_to_db(mel, ref=np.max)
    log_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-9)
    return log_mel.astype(np.float32)


def predict_emotion(audio_path: str) -> dict:
    model, classes = _load_model()

    y, sr = librosa.load(audio_path, sr=SR, mono=True)
    clip_samples = int(SR * CLIP_SECONDS)
    if len(y) < clip_samples:
        y = np.pad(y, (0, clip_samples - len(y)))
    else:
        y = y[:clip_samples]

    spec = _extract_logmel(y, sr)
    xb = torch.tensor(spec).unsqueeze(0).unsqueeze(0).to(DEVICE)  # (1, 1, mels, time)

    with torch.no_grad():
        logits = model(xb)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    pred_idx = int(np.argmax(probs))
    return {
        "interview_state": classes[pred_idx],
        "confidence": round(float(probs[pred_idx]), 3),
    }