import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score, cross_validate as sk_cross_validate


PARAM_GRID = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 5, 10, 15],
    'min_samples_split': [2, 5, 10],
    'max_features': ['sqrt', 'log2'],
}


def build_baseline(random_state=42):
    return RandomForestClassifier(n_estimators=100, random_state=random_state)


def tune_hyperparameters(X_train, y_train, param_grid=None, random_state=42):
    if param_grid is None:
        param_grid = PARAM_GRID

    rf = RandomForestClassifier(random_state=random_state)
    grid_search = GridSearchCV(
        rf, param_grid,
        cv=5, scoring='f1',
        n_jobs=-1, verbose=1
    )
    grid_search.fit(X_train, y_train)

    print(f"Najlepsze parametry: {grid_search.best_params_}")
    print(f"Najlepszy F1 (CV): {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_, grid_search


def cross_validate(model, X, y, cv=5):
    scoring = {'f1': 'f1', 'accuracy': 'accuracy', 'roc_auc': 'roc_auc'}
    raw = sk_cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
    results = {metric: raw[f'test_{metric}'] for metric in scoring}
    return results
