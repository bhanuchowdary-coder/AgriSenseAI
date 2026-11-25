"""
visualization.py
----------------
Plotting utilities: vegetation index maps, sensor time series,
risk heatmaps, and confusion matrices.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (safe for servers)
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
import os

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --------------------------------------------------------------------------- #
#  Colormap helpers                                                             #
# --------------------------------------------------------------------------- #

NDVI_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "ndvi", ["#8B4513", "#F5DEB3", "#90EE90", "#228B22", "#006400"]
)

RISK_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "risk", ["#00CC44", "#FFFF00", "#FF8800", "#CC0000"]
)


# --------------------------------------------------------------------------- #
#  Vegetation index plots                                                       #
# --------------------------------------------------------------------------- #

def plot_vegetation_indices(ndvi, evi, savi, save_path=None):
    """Side-by-side maps of NDVI, EVI, SAVI."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("#1a1a2e")

    data_cmaps = [(ndvi, "NDVI", NDVI_CMAP), (evi, "EVI", "YlGn"), (savi, "SAVI", "BrBG")]
    for ax, (data, title, cmap) in zip(axes, data_cmaps):
        im = ax.imshow(data, cmap=cmap, vmin=-1, vmax=1)
        plt.colorbar(im, ax=ax, shrink=0.8, label="Index value")
        ax.set_title(title, color="white", fontsize=14, fontweight="bold")
        ax.set_facecolor("#0f0f23")
        ax.tick_params(colors="gray")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")

    fig.suptitle("Vegetation Health Indices", color="white", fontsize=16, y=1.02)
    plt.tight_layout()
    path = save_path or f"{OUTPUT_DIR}/vegetation_indices.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved: {path}")
    return path


def plot_crop_health_map(health_classes, save_path=None):
    """
    Colored map of crop health classes.
    0=barren, 1=sparse, 2=moderate, 3=healthy, 4=dense
    """
    colors = ["#8B4513", "#DEB887", "#9ACD32", "#32CD32", "#006400"]
    labels = ["Barren", "Sparse", "Moderate", "Healthy", "Dense"]
    cmap = mcolors.ListedColormap(colors)

    fig, ax = plt.subplots(figsize=(8, 7))
    fig.patch.set_facecolor("#1a1a2e")
    im = ax.imshow(health_classes, cmap=cmap, vmin=0, vmax=4)
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2, 3, 4])
    cbar.ax.set_yticklabels(labels, color="white")
    ax.set_title("Crop Health Map", color="white", fontsize=15, fontweight="bold")
    ax.set_facecolor("#0f0f23")
    plt.tight_layout()
    path = save_path or f"{OUTPUT_DIR}/crop_health_map.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    return path


# --------------------------------------------------------------------------- #
#  Sensor time series                                                           #
# --------------------------------------------------------------------------- #

def plot_sensor_timeseries(df, save_path=None):
    """4-panel sensor time series with drought/pest risk overlay."""
    cols = ["soil_moisture", "temperature", "humidity", "leaf_wetness"]
    colors = ["#00BFFF", "#FF6347", "#90EE90", "#DDA0DD"]
    units = ["%", "°C", "%", "/10"]
    labels = ["Soil Moisture", "Temperature", "Humidity", "Leaf Wetness"]

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor("#1a1a2e")
    gs = GridSpec(4, 1, hspace=0.4)

    for i, (col, color, unit, label) in enumerate(zip(cols, colors, units, labels)):
        ax = fig.add_subplot(gs[i])
        ax.set_facecolor("#0f0f23")
        if col in df.columns:
            ax.plot(df.index, df[col], color=color, lw=1.5, alpha=0.9)
            ax.fill_between(df.index, df[col], alpha=0.2, color=color)
        ax.set_ylabel(f"{label} ({unit})", color="white", fontsize=9)
        ax.tick_params(colors="gray", labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#333")
        if i < len(cols) - 1:
            ax.set_xticks([])

    fig.suptitle("IoT Sensor Readings Over Time", color="white", fontsize=14, y=1.01)
    path = save_path or f"{OUTPUT_DIR}/sensor_timeseries.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    return path


# --------------------------------------------------------------------------- #
#  Risk heatmap                                                                 #
# --------------------------------------------------------------------------- #

def plot_risk_heatmap(risk_grid, title="Pest Outbreak Risk", save_path=None):
    """2D risk map with color coding low→high."""
    fig, ax = plt.subplots(figsize=(8, 7))
    fig.patch.set_facecolor("#1a1a2e")
    im = ax.imshow(risk_grid, cmap=RISK_CMAP, vmin=0, vmax=1)
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Risk Level", color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")
    ax.set_title(title, color="white", fontsize=14, fontweight="bold")
    ax.set_facecolor("#0f0f23")
    for spine in ax.spines.values():
        spine.set_edgecolor("#333")
    ax.tick_params(colors="gray")
    plt.tight_layout()
    path = save_path or f"{OUTPUT_DIR}/risk_heatmap.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    return path


# --------------------------------------------------------------------------- #
#  Confusion matrix                                                             #
# --------------------------------------------------------------------------- #

def plot_confusion_matrix(cm, class_names, title="Confusion Matrix", save_path=None):
    """Styled confusion matrix heatmap."""
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#0f0f23")

    im = ax.imshow(cm, cmap="Blues")
    plt.colorbar(im, ax=ax)

    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right", color="white", fontsize=9)
    ax.set_yticklabels(class_names, color="white", fontsize=9)
    ax.tick_params(colors="gray")

    for i in range(len(class_names)):
        for j in range(len(class_names)):
            val = cm[i, j]
            color = "white" if val < cm.max() / 2 else "black"
            ax.text(j, i, str(val), ha="center", va="center", color=color, fontsize=9)

    ax.set_xlabel("Predicted", color="white")
    ax.set_ylabel("Actual", color="white")
    ax.set_title(title, color="white", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = save_path or f"{OUTPUT_DIR}/confusion_matrix.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    return path


# --------------------------------------------------------------------------- #
#  Demo                                                                         #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "..")
    from models.vegetation_indices import (
        generate_synthetic_bands, compute_ndvi, compute_evi, compute_savi
    )
    from data.preprocessing import generate_synthetic_sensor_df

    print("Generating vegetation index plots...")
    bands = generate_synthetic_bands(128, 128)
    ndvi = compute_ndvi(bands["nir"], bands["red"])
    evi  = compute_evi(bands["nir"], bands["red"], bands["blue"])
    savi = compute_savi(bands["nir"], bands["red"])
    plot_vegetation_indices(ndvi, evi, savi)

    print("Generating sensor time series plot...")
    df = generate_synthetic_sensor_df(n_days=30, readings_per_day=24)
    df = df.set_index("timestamp")
    plot_sensor_timeseries(df)

    print("Generating risk heatmap...")
    risk = np.random.beta(2, 5, (64, 64))
    plot_risk_heatmap(risk, title="Pest Outbreak Risk Map")

    print("\n✅ All visualizations saved to outputs/")