"""
Train the CNN-LSTM Speech Emotion Recognition model.
Run: python train_ser.py
"""
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class SERDataset(Dataset):
    def __init__(self, X, y_encoded, augment=False):
        self.X = X
        self.y = y_encoded
        self.augment = augment

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        spec = self.X[idx].copy()
        if self.augment:
            spec = self._augment(spec)
        return torch.tensor(spec).unsqueeze(0), torch.tensor(self.y[idx])

    def _augment(self, spec):
        if np.random.rand() < 0.5:
            t = spec.shape[1]
            mask_len = np.random.randint(1, max(2, t // 10))
            start = np.random.randint(0, max(1, t - mask_len))
            spec[:, start:start + mask_len] = 0.0
        if np.random.rand() < 0.5:
            f = spec.shape[0]
            mask_len = np.random.randint(1, max(2, f // 10))
            start = np.random.randint(0, max(1, f - mask_len))
            spec[start:start + mask_len, :] = 0.0
        return spec


class CNNLSTM(nn.Module):
    def __init__(self, n_classes, n_mels=128):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
        )
        reduced_mels = n_mels // 8
        self.lstm = nn.LSTM(input_size=64 * reduced_mels, hidden_size=128,
                             num_layers=2, batch_first=True, bidirectional=True, dropout=0.3)
        self.classifier = nn.Sequential(
            nn.Linear(256, 64), nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, n_classes)
        )

    def forward(self, x):
        b = x.size(0)
        feat = self.conv(x)
        feat = feat.permute(0, 3, 1, 2).reshape(b, feat.size(3), -1)
        out, _ = self.lstm(feat)
        out = out.mean(dim=1)
        return self.classifier(out)


def train():
    X_train = np.load("data/processed/X_train.npy")
    X_val = np.load("data/processed/X_val.npy")
    with open("data/processed/manifest.json") as f:
        manifest = json.load(f)
    y_train_raw = [e["interview_state"] for e in manifest["train"]]
    y_val_raw = [e["interview_state"] for e in manifest["val"]]

    le = LabelEncoder()
    y_train = le.fit_transform(y_train_raw)
    y_val = le.transform(y_val_raw)
    n_classes = len(le.classes_)

    class_weights = compute_class_weight("balanced", classes=np.unique(y_train), y=y_train)
    class_weights = torch.tensor(class_weights, dtype=torch.float32).to(DEVICE)

    train_ds = SERDataset(X_train, y_train, augment=True)
    val_ds = SERDataset(X_val, y_val, augment=False)
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32)

    model = CNNLSTM(n_classes=n_classes).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", patience=3, factor=0.5)

    best_f1, patience, patience_ctr = 0.0, 7, 0

    for epoch in range(50):
        model.train()
        for xb, yb in train_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()

        model.eval()
        preds, trues = [], []
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(DEVICE)
                out = model(xb).argmax(dim=1).cpu().numpy()
                preds.extend(out)
                trues.extend(yb.numpy())
        val_f1 = f1_score(trues, preds, average="macro")
        scheduler.step(val_f1)
        print(f"Epoch {epoch+1}: val macro-F1 = {val_f1:.4f}")

        if val_f1 > best_f1:
            best_f1 = val_f1
            patience_ctr = 0
            torch.save({"model_state": model.state_dict(),
                        "label_classes": le.classes_.tolist()},
                       "ai/models/ser_cnn_lstm.pt")
        else:
            patience_ctr += 1
            if patience_ctr >= patience:
                print("Early stopping.")
                break

    print(f"Best val macro-F1: {best_f1:.4f}. Checkpoint saved to ai/models/ser_cnn_lstm.pt")


if __name__ == "__main__":
    train()