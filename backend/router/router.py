"""
Модуль маршрутизации запросов.

Загружает обученный классификатор и бенчмарк-скоры моделей. Для входного запроса:
1) Классифицирует категорию (code/math/translation/creative/general)
2) Считает взвешенный Score для каждой модели
3) Возвращает лучшую модель
"""

import json
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

ROUTER_DIR = os.path.dirname(os.path.abspath(__file__))
CLF_PATH = os.path.join(ROUTER_DIR, "router_data.pkl")
SCORES_PATH = os.path.join(ROUTER_DIR, "model_scores.json")

_embedder = None
_clf = None
_label_encoder = None
_model_scores = None


def _load():
    global _embedder, _clf, _label_encoder, _model_scores

    if _clf is not None:
        return

    with open(CLF_PATH, "rb") as f:
        data = pickle.load(f)
    _clf = data["classifier"]
    _label_encoder = data["label_encoder"]
    _embedder = SentenceTransformer(data["model_name"])

    with open(SCORES_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    _model_scores = config["models"]


def classify(query: str) -> dict:
    """
    returns:
        {
            "category": "code",
            "probabilities": {"code": 0.85, "math": 0.05, ...}
        }
    """
    _load()
    embedding = _embedder.encode([query])
    probs = _clf.predict_proba(embedding)[0]
    category_names = _label_encoder.inverse_transform(_clf.classes_)

    prob_dict = {cat: round(float(p), 4) for cat, p in zip(category_names, probs)}
    top_category = category_names[np.argmax(probs)]

    return {
        "category": top_category,
        "probabilities": prob_dict,
    }


ROUTING_MODES = {
    "quality":  {"quality_w": 1.0, "cost_w": 0.0},
    "balanced": {"quality_w": 0.6, "cost_w": 0.4},
    "economy":  {"quality_w": 0.3, "cost_w": 0.7},
}


def _compute_efficiency():
    """Нормализованная эффективность: дешёвые модели → ближе к 1.0."""
    costs = {mid: info["cost"] for mid, info in _model_scores.items()}
    max_cost = max(costs.values())
    return {mid: round(1 - cost / max_cost, 4) for mid, cost in costs.items()}


def route(query: str, mode: str = "quality") -> dict:
    """
    mode: "quality" | "balanced" | "economy"

    quality_score = sum(P(category_i) * benchmark_score_i)
    cost_efficiency = 1 - (cost / max_cost)
    final_score = quality_w * quality_score + cost_w * cost_efficiency
    """
    _load()
    weights = ROUTING_MODES.get(mode, ROUTING_MODES["quality"])
    classification = classify(query)
    probs = classification["probabilities"]
    efficiency = _compute_efficiency()

    all_scores = {}
    for model_id, model_info in _model_scores.items():
        benchmarks = model_info["scores"]
        quality = sum(
            probs.get(cat, 0) * benchmarks.get(cat, 0)
            for cat in probs
        )
        final = (
            weights["quality_w"] * quality
            + weights["cost_w"] * efficiency[model_id]
        )
        all_scores[model_id] = round(final, 4)

    best_model = max(all_scores, key=all_scores.get)

    return {
        "best_model": best_model,
        "best_model_name": _model_scores[best_model]["display_name"],
        "best_score": all_scores[best_model],
        "mode": mode,
        "category": classification["category"],
        "probabilities": probs,
        "all_scores": all_scores,
    }


def get_available_models() -> list:
    _load()
    return [
        {"id": mid, "name": info["display_name"], "provider": info["provider"]}
        for mid, info in _model_scores.items()
    ]
