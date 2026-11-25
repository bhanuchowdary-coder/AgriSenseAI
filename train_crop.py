
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "datasets" / "Crop_recommendation.csv"
MODEL_PATH = BASE_DIR / "models" / "crop_model.npz"

FEATURES = [
    "N", "P", "K",
    "temperature", "humidity",
    "ph", "rainfall"
]

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        "Place Crop_recommendation.csv in the datasets folder."
    )

df = pd.read_csv(DATASET_PATH)

df = df.dropna(subset=FEATURES + ["label"])
df = df.drop_duplicates()

X = df[FEATURES].to_numpy(dtype=float)
y = df["label"].to_numpy(dtype=str)

print("Dataset loaded successfully")
print("Dataset shape:", df.shape)

# Split dataset into training and testing sets
rng = np.random.default_rng(42)
indices = rng.permutation(len(X))

split = int(len(X) * 0.8)

train_idx = indices[:split]
test_idx = indices[split:]

X_train = X[train_idx]
X_test = X[test_idx]

y_train = y[train_idx]
y_test = y[test_idx]

# Normalize features using training data
mean = X_train.mean(axis=0)
std = X_train.std(axis=0)

std[std == 0] = 1

X_train_scaled = (X_train - mean) / std
X_test_scaled = (X_test - mean) / std

# K-Nearest Neighbors
K = 5

def predict(sample):
    distances = np.sqrt(
        np.sum((X_train_scaled - sample) ** 2, axis=1)
    )

    nearest = np.argsort(distances)[:K]

    labels, counts = np.unique(
        y_train[nearest],
        return_counts=True
    )

    return labels[np.argmax(counts)]

print("Evaluating KNN model...")

predictions = np.array([
    predict(sample) for sample in X_test_scaled
])

accuracy = np.mean(predictions == y_test)

print(f"Test accuracy: {accuracy * 100:.2f}%")

# Save model data
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

np.savez_compressed(
    MODEL_PATH,
    X_train=X_train_scaled,
    y_train=y_train,
    mean=mean,
    std=std,
    k=K,
    features=np.array(FEATURES)
)

print("Model saved successfully")
print(MODEL_PATH)

