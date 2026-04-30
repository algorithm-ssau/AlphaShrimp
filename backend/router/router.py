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
_model_scores = None


def _load():
    global _embedder, _clf, _model_scores

    if _clf is not None:
        return

    with open(CLF_PATH, "rb") as f:
        data = pickle.load(f)
    _clf = data["classifier"]
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
    categories = _clf.classes_

    prob_dict = {cat: round(float(p), 4) for cat, p in zip(categories, probs)}
    top_category = categories[np.argmax(probs)]

    return {
        "category": top_category,
        "probabilities": prob_dict,
    }


def route(query: str) -> dict:
    """
    score = sum(P(category_i) * benchmark_score_i)

    returns:
        {
            "best_model": "claude-opus-4.7",
            "best_score": 0.912,
            "category": "code",
            "probabilities": {"code": 0.85, ...},
            "all_scores": {"claude-opus-4.7": 0.912, ...}
        }
    """
    _load()
    classification = classify(query)
    probs = classification["probabilities"]

    all_scores = {}
    for model_id, model_info in _model_scores.items():
        benchmarks = model_info["scores"]
        score = sum(
            probs.get(cat, 0) * benchmarks.get(cat, 0)
            for cat in probs
        )
        all_scores[model_id] = round(score, 4)

    best_model = max(all_scores, key=all_scores.get)

    return {
        "best_model": best_model,
        "best_model_name": _model_scores[best_model]["display_name"],
        "best_score": all_scores[best_model],
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
