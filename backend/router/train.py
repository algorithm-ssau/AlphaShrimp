"""
Гибридный маршрутизатор: эмбеддинги + логистическая регрессия.
"""

import csv
import pickle
import numpy as np
from collections import Counter
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

MODEL_NAME = "cointegrated/rubert-tiny2"
TRAIN_PATH = "router_examples.csv"
VALID_PATH = "router_validation.csv"
OUTPUT_PATH = "router_data_clf.pkl"


def load_csv(path: str) -> list[tuple[str, str]]:
    examples = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            q = row["query"].strip()
            c = row["category"].strip()
            if q and c:
                examples.append((q, c))
    return examples


def main():
    print(f"Загрузка модели {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    # обучающая выборка
    train_examples = load_csv(TRAIN_PATH)
    train_queries = [q for q, _ in train_examples]
    train_labels = [c for _, c in train_examples]
    print(f"Обучающая выборка: {len(train_examples)} примеров")

    print("Кодирование обучающей выборки...")
    X_train = model.encode(train_queries, show_progress_bar=True, convert_to_numpy=True)

    # валидационная выборка
    val_examples = load_csv(VALID_PATH)
    val_queries = [q for q, _ in val_examples]
    val_labels = [c for _, c in val_examples]
    print(f"Валидационная выборка: {len(val_examples)} примеров")

    print("Кодирование валидационной выборки...")
    X_val = model.encode(val_queries, show_progress_bar=True, convert_to_numpy=True)

    # обучение классификатора
    le = LabelEncoder()
    y_train = le.fit_transform(train_labels)
    y_val = le.transform(val_labels)

    ###
    print("\nПодбор гиперпараметра C:")
    best_acc = 0
    best_c = 1.0
    for c_val in [0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]:
        clf = LogisticRegression(C=c_val, max_iter=1000, random_state=42)
        clf.fit(X_train, y_train)
        acc_train = clf.score(X_train, y_train)
        acc_val = clf.score(X_val, y_val)
        marker = ""
        if acc_val > best_acc:
            best_acc = acc_val
            best_c = c_val
            marker = " ← лучший"
        print(f"  C={c_val:<6} train={acc_train:.1%}  val={acc_val:.1%}{marker}")

    print(f"\nФинальная модель (C={best_c})")
    clf = LogisticRegression(C=best_c, max_iter=1000, random_state=42)
    clf.fit(X_train, y_train)

    # self-test
    y_pred_train = clf.predict(X_train)
    acc_train = np.mean(y_pred_train == y_train)
    print(f"\nSelf-test: {int(acc_train * len(train_examples))}/{len(train_examples)} = {acc_train:.1%}")

    # валидация
    y_pred_val = clf.predict(X_val)
    acc_val = np.mean(y_pred_val == y_val)
    print(f"Валидация: {int(acc_val * len(val_examples))}/{len(val_examples)} = {acc_val:.1%}")

    ###
    print(f"\nОтчёт по категориям:")
    print(classification_report(
        y_val, y_pred_val,
        target_names=le.classes_,
        digits=2,
    ))

    errors = []
    for i, (query, true_cat) in enumerate(val_examples):
        pred_cat = le.inverse_transform([y_pred_val[i]])[0]
        if pred_cat != true_cat:
            probs = clf.predict_proba(X_val[i:i+1])[0]
            confidence = max(probs)
            errors.append((query, true_cat, pred_cat, confidence))

    if errors:
        print(f"Ошибки ({len(errors)}):")
        for q, true, pred, conf in errors:
            print(f"  [{true} -> {pred}] (conf={conf:.2f}) {q[:65]}")

    data = {
        "model_name": MODEL_NAME,
        "classifier": clf,
        "label_encoder": le,
        "categories": list(le.classes_),
    }
    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(data, f)
    print(f"\nСохранено в {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
