# =============================================================
# ml/predict_cluster.py
# Edu-Platform — Cluster / Learning Style Prediction
#
# Priority:
#   1. Ensemble classifier (93.3% accuracy) — BEST
#   2. KMeans fallback (92.0% accuracy)
#   3. Rule-based fallback (if no models found)
#
# Usage:
#   from ml.predict_cluster import predict_learning_style
#   style, confidence = predict_learning_style({'logical':80,'verbal':45,...})
# =============================================================

import pickle
import os
import numpy as np
from typing import Optional

FEATURES    = ['logical', 'verbal', 'numerical', 'memory', 'attention']
MODELS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')


# =============================================================
# Load Models (once at import time)
# =============================================================

def _load(filename):
    path = os.path.join(MODELS_PATH, filename)
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

# Load all — None agar file nahi mili
_CLASSIFIER    = _load('classifier.pkl')
_SCALER        = _load('scaler.pkl')
_LABEL_ENCODER = _load('label_encoder.pkl')
_KMEANS        = _load('kmeans_model.pkl')
_CLUSTER_MAP   = _load('cluster_map.pkl')

# Status print
_mode = "ensemble" if (_CLASSIFIER and _SCALER and _LABEL_ENCODER) else \
        "kmeans"   if (_KMEANS and _SCALER and _CLUSTER_MAP)        else \
        "rule_based"
print(f"[predict_cluster] Mode: {_mode}")


# =============================================================
# Default cluster map (fallback)
# =============================================================

_DEFAULT_CLUSTER_MAP = {
    0: 'visual_learner',
    1: 'conceptual_thinker',
    2: 'practice_based',
    3: 'step_by_step',
}

_RULE_BASED_MAP = {
    'logical':   'conceptual_thinker',
    'verbal':    'visual_learner',
    'numerical': 'practice_based',
    'memory':    'step_by_step',
    'attention': 'practice_based',
}


# =============================================================
# Main Prediction Function
# =============================================================

def predict_learning_style(scores: dict) -> tuple[str, float]:
    """
    Student ke aptitude scores se learning style predict karo.

    Args:
        scores: dict with keys: logical, verbal, numerical, memory, attention
                Values: 0-100 (float or int)

    Returns:
        tuple: (learning_style: str, confidence: float 0-1)

    Example:
        style, conf = predict_learning_style({
            'logical': 80, 'verbal': 45, 'numerical': 75,
            'memory': 55, 'attention': 82
        })
        # -> ('practice_based', 0.94)
    """

    # Validate input
    missing = [f for f in FEATURES if f not in scores]
    if missing:
        raise ValueError(f"Missing features: {missing}. Required: {FEATURES}")

    features_arr = [[float(scores[f]) for f in FEATURES]]

    # ── Method 1: Ensemble Classifier (Best accuracy ~93.3%) ────
    if _CLASSIFIER and _SCALER and _LABEL_ENCODER:
        try:
            X_scaled    = _SCALER.transform(features_arr)
            pred_idx    = _CLASSIFIER.predict(X_scaled)[0]
            style       = _LABEL_ENCODER.classes_[pred_idx]
            proba       = _CLASSIFIER.predict_proba(X_scaled)[0]
            confidence  = float(proba[pred_idx])
            return style, confidence
        except Exception as e:
            print(f"[predict_cluster] Ensemble failed: {e} — falling back to KMeans")

    # ── Method 2: KMeans Fallback (92.0% accuracy) ──────────────
    if _KMEANS and _SCALER and _CLUSTER_MAP:
        try:
            X_scaled   = _SCALER.transform(features_arr)
            cluster_id = int(_KMEANS.predict(X_scaled)[0])
            style      = _CLUSTER_MAP.get(cluster_id, 'visual_learner')
            return style, 0.85   # KMeans has no probability — fixed confidence
        except Exception as e:
            print(f"[predict_cluster] KMeans failed: {e} — falling back to rules")

    # ── Method 3: Rule-Based Fallback ───────────────────────────
    dominant = max({f: scores[f] for f in FEATURES}, key=lambda k: scores[k])
    style    = _RULE_BASED_MAP.get(dominant, 'visual_learner')
    return style, 0.70


def predict_cluster_id(scores: dict) -> tuple[int, str]:
    """
    Cluster ID aur style dono return karo.
    Backward compatibility ke liye.

    Returns:
        (cluster_id: int, style: str)
    """
    style, _ = predict_learning_style(scores)
    style_to_cluster = {
        'visual_learner':     0,
        'conceptual_thinker': 1,
        'practice_based':     2,
        'step_by_step':       3,
    }
    cluster_id = style_to_cluster.get(style, 0)
    return cluster_id, style


def get_model_info() -> dict:
    """Current model ki info return karo."""
    import json
    info_path = os.path.join(MODELS_PATH, 'model_info.json')
    try:
        with open(info_path) as f:
            return json.load(f)
    except Exception:
        return {'mode': _mode, 'note': 'model_info.json nahi mila'}


# =============================================================
# Quick Test
# =============================================================

if __name__ == '__main__':
    print("="*50)
    print("predict_cluster.py — Quick Test")
    print("="*50)
    print(f"Model mode: {_mode}")

    test_cases = [
        ({'logical':80,'verbal':45,'numerical':75,'memory':55,'attention':82}, 'practice_based'),
        ({'logical':55,'verbal':85,'numerical':40,'memory':80,'attention':70}, 'visual_learner'),
        ({'logical':88,'verbal':65,'numerical':72,'memory':50,'attention':60}, 'conceptual_thinker'),
        ({'logical':60,'verbal':62,'numerical':58,'memory':88,'attention':75}, 'step_by_step'),
    ]

    for scores, expected in test_cases:
        style, conf = predict_learning_style(scores)
        match = "✅" if style == expected else "❌"
        print(f"{match} Expected: {expected:25s} | Got: {style:25s} | Confidence: {conf:.2f}")