"""Wspólny zestaw narzędzi dla notebooków porównujących algorytmy.

Ten moduł jest jednym źródłem prawdy dla 4 dodatkowych algorytmów
(regresja logistyczna, drzewo decyzyjne, gradient boosting, prosta sieć MLP).
Dzięki temu notebooki 03–06 oraz zbiorczy 07 używają IDENTYCZNYCH definicji
modeli i siatek hiperparametrów, co jest warunkiem sprawiedliwego porównania.

Reużywa istniejących funkcji z src/preprocessing.py, src/evaluation.py i
src/model.py (są model-agnostyczne). NIE modyfikuje żadnego z tych plików ani
master_notebook.ipynb — Random Forest ma swoją realizację w src/model.py.

Metryki liczymy tylko 4 (jedyne metryki statystyczne w projekcie):
accuracy, F1-Score, ROC-AUC, MCC.
"""

import os
import json
import time

import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, matthews_corrcoef,
)

RANDOM_STATE = 42
RESULTS_DIR = 'results'
PLOTS_DIR = 'plots'

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)


# --------------------------------------------------------------------------
# Buildery modeli bazowych (baseline) — sensowne, „domyślne" ustawienia
# --------------------------------------------------------------------------

def build_logreg(random_state=RANDOM_STATE):
    # max_iter podniesiony, bo dane skalowane a lbfgs czasem potrzebuje więcej
    return LogisticRegression(max_iter=1000, random_state=random_state)


def build_tree(random_state=RANDOM_STATE):
    return DecisionTreeClassifier(random_state=random_state)


def build_gboost(random_state=RANDOM_STATE):
    return GradientBoostingClassifier(random_state=random_state)


def build_mlp(random_state=RANDOM_STATE):
    return MLPClassifier(
        hidden_layer_sizes=(32, 16),
        max_iter=1000,
        random_state=random_state,
    )


# --------------------------------------------------------------------------
# Siatki hiperparametrów (dobrane tak, by tuning trwał kilka–kilkanaście s)
# --------------------------------------------------------------------------

LOGREG_GRID = {
    'C': [0.01, 0.1, 1, 10, 100],
    'penalty': ['l2'],
    'solver': ['lbfgs', 'liblinear'],
    'class_weight': [None, 'balanced'],
}

TREE_GRID = {
    'criterion': ['gini', 'entropy'],
    'max_depth': [None, 3, 5, 7, 10],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
}

GBOOST_GRID = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [2, 3, 4],
    'subsample': [0.8, 1.0],
}

MLP_GRID = {
    'hidden_layer_sizes': [(16,), (32, 16), (64, 32)],
    'activation': ['relu', 'tanh'],
    'alpha': [1e-4, 1e-3, 1e-2],
}


# Rejestr 4 dodatkowych algorytmów. RF jest dokładany osobno w notebooku 07
# (jego realizacja żyje w src/model.py) — tu trzymamy tylko nowe algorytmy.
ALGORITHMS = {
    'Regresja logistyczna': {
        'slug': 'logistic_regression',
        'build': build_logreg,
        'grid': LOGREG_GRID,
    },
    'Drzewo decyzyjne': {
        'slug': 'decision_tree',
        'build': build_tree,
        'grid': TREE_GRID,
    },
    'Gradient Boosting': {
        'slug': 'gradient_boosting',
        'build': build_gboost,
        'grid': GBOOST_GRID,
    },
    'Sieć neuronowa (MLP)': {
        'slug': 'neural_network',
        'build': build_mlp,
        'grid': MLP_GRID,
    },
}


# --------------------------------------------------------------------------
# Tuning (generyczny GridSearchCV — analogiczny do src/model.py)
# --------------------------------------------------------------------------

def tune(estimator, param_grid, X_train, y_train, scoring='f1', cv=5, n_jobs=-1):
    """GridSearchCV z 5-fold CV. Zwraca (best_estimator_, grid_search)."""
    grid = GridSearchCV(
        estimator, param_grid,
        cv=cv, scoring=scoring, n_jobs=n_jobs,
    )
    grid.fit(X_train, y_train)
    return grid.best_estimator_, grid


# --------------------------------------------------------------------------
# Ewaluacja — DOKŁADNIE 4 metryki (jedyne metryki statystyczne w projekcie)
# --------------------------------------------------------------------------

def evaluate(model, X_test, y_test):
    """Liczy 4 metryki: accuracy, F1, ROC-AUC, MCC. Zwraca dict (bez druku)."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    return {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'f1': float(f1_score(y_test, y_pred)),
        'roc_auc': float(roc_auc_score(y_test, y_prob)),
        'mcc': float(matthews_corrcoef(y_test, y_pred)),
    }


def print_metrics(metrics, title='WYNIKI'):
    """Ładny wydruk 4 metryk (bez classification_report — rygor 4 metryk)."""
    print(f'=== {title} ===')
    print(f"  Accuracy : {metrics['accuracy']:.4f}")
    print(f"  F1-Score : {metrics['f1']:.4f}")
    print(f"  ROC-AUC  : {metrics['roc_auc']:.4f}")
    print(f"  MCC      : {metrics['mcc']:.4f}")


# --------------------------------------------------------------------------
# Pomiary czasu (do porównania w notebooku zbiorczym)
# --------------------------------------------------------------------------

def timed_fit(model, X, y):
    """Trenuje model i zwraca (model, czas_trenowania_w_sekundach)."""
    t0 = time.perf_counter()
    model.fit(X, y)
    return model, time.perf_counter() - t0


def timed_predict(model, X, repeat=5):
    """Średni czas predykcji na zbiorze X (uśredniony po `repeat` powtórzeniach)."""
    t0 = time.perf_counter()
    for _ in range(repeat):
        model.predict(X)
    return (time.perf_counter() - t0) / repeat


# --------------------------------------------------------------------------
# Ważność cech — adaptacyjna wg typu modelu
# --------------------------------------------------------------------------

def plot_importance(model, feature_names, X_test=None, y_test=None,
                    title=None, save_path=None, random_state=RANDOM_STATE):
    """Wykres ważności cech dobrany do rodzaju modelu.

    - modele liniowe (coef_)      -> |współczynnik| (kolor = znak wpływu)
    - drzewa/boosting             -> feature_importances_ (impurity)
    - reszta (np. MLP)            -> permutation_importance (spadek F1)
    """
    feature_names = list(feature_names)

    if hasattr(model, 'coef_'):
        coefs = np.ravel(model.coef_)
        importances = np.abs(coefs)
        signs = np.sign(coefs)
        ylabel = '|współczynnik| (waga cechy)'
        subtitle = 'niebieski = zwiększa ryzyko choroby, czerwony = zmniejsza'
    elif hasattr(model, 'feature_importances_'):
        importances = np.asarray(model.feature_importances_, dtype=float)
        signs = None
        ylabel = 'Ważność (redukcja impurity)'
        subtitle = None
    else:
        result = permutation_importance(
            model, X_test, y_test,
            scoring='f1', n_repeats=10, random_state=random_state,
        )
        importances = result.importances_mean
        signs = None
        ylabel = 'Spadek F1 przy permutacji cechy'
        subtitle = 'permutation importance (model bez natywnej ważności)'

    order = np.argsort(importances)[::-1]
    if signs is not None:
        colors = ['#2E5FA3' if signs[i] >= 0 else '#E8834A' for i in order]
    else:
        colors = 'steelblue'

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(range(len(order)), importances[order], color=colors, alpha=0.85)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([feature_names[i] for i in order], rotation=40, ha='right')
    ax.set_ylabel(ylabel)
    full_title = title or 'Ważność cech'
    if subtitle:
        full_title += f'\n({subtitle})'
    ax.set_title(full_title)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()


# --------------------------------------------------------------------------
# Zapis / odczyt wyników (artefakty dla notebooka zbiorczego)
# --------------------------------------------------------------------------

def _json_default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, tuple):
        return list(o)
    return str(o)


def save_results(slug, data):
    """Zapisuje słownik wyników do results/<slug>.json."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f'{slug}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=_json_default)
    return path


def load_results(slug):
    """Wczytuje results/<slug>.json (lub None, jeśli nie istnieje)."""
    path = os.path.join(RESULTS_DIR, f'{slug}.json')
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)
