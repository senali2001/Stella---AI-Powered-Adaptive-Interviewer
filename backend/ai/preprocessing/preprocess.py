"""
Preprocessing pipeline for Speech Emotion Recognition datasets (RAVDESS + CREMA-D).

Steps: load -> resample to 16kHz -> mono -> trim silence -> fixed-length
segmentation -> label encoding -> speaker-independent train/val/test split.

Run: python preprocess.py --ravdess_dir <path> --cremad_dir <path> --out_dir data/processed
"""
import argparse
import os
import glob
import json
import numpy as np
import librosa
import soundfile as sf
from sklearn.model_selection import GroupShuffleSplit

TARGET_SR = 16000
CLIP_SECONDS = 3.0
CLIP_SAMPLES = int(TARGET_SR * CLIP_SECONDS)

RAVDESS_EMOTION_MAP = {
    "01": "neutral", "02": "calm", "03": "happy", "04": "sad",
    "05": "angry", "06": "fearful", "07": "disgust", "08": "surprise",
}

INTERVIEW_STATE_MAP = {
    "neutral": "calm", "calm": "calm",
    "happy": "confident", "surprise": "uncertain",
    "sad": "nervous", "fearful": "nervous",
    "angry": "stressed", "disgust": "stressed",
}


def load_and_clean(path):
    y, sr = librosa.load(path, sr=TARGET_SR, mono=True)
    y, _ = librosa.effects.trim(y, top_db=25)
    if len(y) < CLIP_SAMPLES:
        y = np.pad(y, (0, CLIP_SAMPLES - len(y)))
    else:
        y = y[:CLIP_SAMPLES]
    peak = np.max(np.abs(y)) + 1e-9
    y = y / peak
    return y


def parse_ravdess(ravdess_dir):
    rows = []
    for path in glob.glob(os.path.join(ravdess_dir, "**", "*.wav"), recursive=True):
        fname = os.path.basename(path)
        parts = fname.split("-")
        if len(parts) < 7:
            continue
        emo_code = parts[2]
        actor_id = int(parts[6].split(".")[0])
        emotion = RAVDESS_EMOTION_MAP.get(emo_code)
        if emotion is None:
            continue
        rows.append({
            "path": path,
            "speaker_id": f"ravdess_{actor_id}",
            "emotion": emotion,
            "interview_state": INTERVIEW_STATE_MAP[emotion],
        })
    return rows


def parse_cremad(cremad_dir):
    code_map = {"NEU": "neutral", "HAP": "happy", "SAD": "sad",
                "ANG": "angry", "FEA": "fearful", "DIS": "disgust"}
    rows = []
    for path in glob.glob(os.path.join(cremad_dir, "*.wav")):
        fname = os.path.basename(path)
        parts = fname.split("_")
        if len(parts) < 3:
            continue
        actor_id, emo_code = parts[0], parts[2]
        emotion = code_map.get(emo_code)
        if emotion is None:
            continue
        rows.append({
            "path": path,
            "speaker_id": f"cremad_{actor_id}",
            "emotion": emotion,
            "interview_state": INTERVIEW_STATE_MAP[emotion],
        })
    return rows


def speaker_independent_split(rows, test_size=0.15, val_size=0.15, seed=42):
    speakers = np.array([r["speaker_id"] for r in rows])
    idx = np.arange(len(rows))

    gss1 = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    trainval_idx, test_idx = next(gss1.split(idx, groups=speakers))

    trainval_speakers = speakers[trainval_idx]
    gss2 = GroupShuffleSplit(n_splits=1, test_size=val_size / (1 - test_size), random_state=seed)
    train_idx_rel, val_idx_rel = next(gss2.split(trainval_idx, groups=trainval_speakers))
    train_idx = trainval_idx[train_idx_rel]
    val_idx = trainval_idx[val_idx_rel]

    return [rows[i] for i in train_idx], [rows[i] for i in val_idx], [rows[i] for i in test_idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ravdess_dir", required=True)
    ap.add_argument("--cremad_dir", required=True)
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(args.out_dir, split), exist_ok=True)

    rows = parse_ravdess(args.ravdess_dir) + parse_cremad(args.cremad_dir)
    print(f"Total samples found: {len(rows)}")

    train_rows, val_rows, test_rows = speaker_independent_split(rows)
    print(f"Train: {len(train_rows)}  Val: {len(val_rows)}  Test: {len(test_rows)}")

    manifest = {"train": [], "val": [], "test": []}
    for split_name, split_rows in [("train", train_rows), ("val", val_rows), ("test", test_rows)]:
        for i, r in enumerate(split_rows):
            y = load_and_clean(r["path"])
            out_path = os.path.join(args.out_dir, split_name, f"{split_name}_{i}.wav")
            sf.write(out_path, y, TARGET_SR)
            manifest[split_name].append({
                "audio_path": out_path,
                "speaker_id": r["speaker_id"],
                "emotion": r["emotion"],
                "interview_state": r["interview_state"],
            })

    with open(os.path.join(args.out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("Done. Manifest written to manifest.json")


if __name__ == "__main__":
    main()