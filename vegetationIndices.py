"""
vegetation_indices.py
---------------------
Computes NDVI, EVI, SAVI, and NDWI from multispectral band arrays.
These are standard remote sensing indices used for crop health assessment.
"""

import numpy as np


def safe_divide(a, b, fill=0.0):
    """Avoid division by zero."""
    return np.where(b == 0, fill, a / b)


def compute_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """
    Normalized Difference Vegetation Index
    NDVI = (NIR - RED) / (NIR + RED)
    Range: [-1, 1]. Healthy vegetation > 0.3
    """
    return safe_divide(nir - red, nir + red)


def compute_evi(nir: np.ndarray, red: np.ndarray, blue: np.ndarray,
                G=2.5, C1=6, C2=7.5, L=1) -> np.ndarray:
    """
    Enhanced Vegetation Index — reduces atmospheric & soil noise.
    EVI = G * (NIR - RED) / (NIR + C1*RED - C2*BLUE + L)
    """
    denom = nir + C1 * red - C2 * blue + L
    return G * safe_divide(nir - red, denom)


def compute_savi(nir: np.ndarray, red: np.ndarray, L=0.5) -> np.ndarray:
    """
    Soil Adjusted Vegetation Index — reduces soil brightness effect.
    SAVI = ((NIR - RED) / (NIR + RED + L)) * (1 + L)
    """
    return safe_divide((nir - red) * (1 + L), nir + red + L)


def compute_ndwi(nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
    """
    Normalized Difference Water Index — detects water stress.
    NDWI = (NIR - SWIR) / (NIR + SWIR)
    """
    return safe_divide(nir - swir, nir + swir)


def classify_crop_health(ndvi: np.ndarray) -> np.ndarray:
    """
    Classify pixels into health categories based on NDVI thresholds.
    Returns array with labels: 0=barren, 1=sparse, 2=moderate, 3=healthy, 4=dense
    """
    classes = np.zeros_like(ndvi, dtype=np.uint8)
    classes[ndvi > 0.1] = 1   # sparse vegetation
    classes[ndvi > 0.2] = 2   # moderate
    classes[ndvi > 0.4] = 3   # healthy
    classes[ndvi > 0.6] = 4   # dense/lush
    return classes


def generate_synthetic_bands(height=128, width=128, seed=42) -> dict:
    """Generate fake multispectral bands for testing."""
    rng = np.random.default_rng(seed)
    return {
        "blue":  rng.uniform(0.02, 0.15, (height, width)),
        "red":   rng.uniform(0.05, 0.30, (height, width)),
        "nir":   rng.uniform(0.20, 0.80, (height, width)),
        "swir":  rng.uniform(0.10, 0.40, (height, width)),
    }


if __name__ == "__main__":
    bands = generate_synthetic_bands()
    ndvi = compute_ndvi(bands["nir"], bands["red"])
    evi  = compute_evi(bands["nir"], bands["red"], bands["blue"])
    savi = compute_savi(bands["nir"], bands["red"])
    ndwi = compute_ndwi(bands["nir"], bands["swir"])
    health = classify_crop_health(ndvi)

    print("=== Vegetation Indices (mean values) ===")
    print(f"  NDVI : {ndvi.mean():.4f}  (std={ndvi.std():.4f})")
    print(f"  EVI  : {evi.mean():.4f}  (std={evi.std():.4f})")
    print(f"  SAVI : {savi.mean():.4f}  (std={savi.std():.4f})")
    print(f"  NDWI : {ndwi.mean():.4f}  (std={ndwi.std():.4f})")
    print(f"\nHealth class distribution:")
    for cls, label in enumerate(["Barren","Sparse","Moderate","Healthy","Dense"]):
        pct = (health == cls).mean() * 100
        print(f"  {label:10s}: {pct:.1f}%")