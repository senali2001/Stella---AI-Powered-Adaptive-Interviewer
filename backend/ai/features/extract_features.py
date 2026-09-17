"""
Feature extraction for SER.
Primary feature (fed to CNN-LSTM): 128-bin log-mel spectrogram.
"""
import json
import numpy as np
import librosa

SR = 16000
N_MELS = 128
N_FFT = 1024
HOP_LENGTH = 256


def extract_logmel(y, sr=SR):
    mel = librosa.feature.melspectrogram(
        y=y, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH, n_mels=N_MELS
    )
    log_mel = librosa.power_to_db(mel, ref=np.max)
    log_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-9)
    return log_mel.astype(np.float32)


def build_feature_dataset(manifest_split, label_key="interview_state"):
    X, y_labels = [], []
    for entry in manifest_split:
        audio, sr = librosa.load(entry["audio_path"], sr=SR, mono=True)
        X.append(extract_logmel(audio, sr))
        y_labels.append(entry[label_key])
    return np.stack(X), y_labels


if __name__ == "__main__":
    with open("data/processed/manifest.json") as f:
        manifest = json.load(f)

    for split in ["train", "val", "test"]:
        X, y = build_feature_dataset(manifest[split])
        np.save(f"data/processed/X_{split}.npy", X)
        print(f"{split}: features shape {X.shape}")

    print("Feature extraction done.")