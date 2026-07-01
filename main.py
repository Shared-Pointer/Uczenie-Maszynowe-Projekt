from src.preprocessing import load_data, preprocess, split_and_scale
from src.model import build_baseline, tune_hyperparameters, cross_validate
from src.evaluation import (
    compute_metrics, plot_confusion_matrix,
    plot_roc_curve, plot_feature_importance, plot_learning_curve,
)


def main():
    print("--- Predykcja choroby serca - Random Forest ---\n")

    print("[1/5] Wczytywanie danych...")
    df = load_data('data/heart.csv')
    X, y = preprocess(df)
    print(f"  Próbki: {X.shape[0]}, Cechy: {X.shape[1]}")
    print(f"  Klasy: {dict(y.value_counts().sort_index())}")

    print("\n[2/5] Podział 80/20 + standaryzacja...")
    _, _, X_train, X_test, y_train, y_test, _ = split_and_scale(X, y)
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    print("\n[3/5] GridSearchCV...")
    best_model, grid_search = tune_hyperparameters(X_train, y_train)

    print("\n[4/5] Ewaluacja na zbiorze testowym...")
    metrics = compute_metrics(best_model, X_test, y_test)

    cross_validate(best_model, X, y)

    print("\n[5/5] Wykresy...")
    plot_confusion_matrix(best_model, X_test, y_test)
    plot_roc_curve(best_model, X_test, y_test)
    plot_feature_importance(best_model, list(X.columns))
    plot_learning_curve(best_model, X, y)

    print("\nGotowe! Wykresy w katalogu plots/")
    return metrics


if __name__ == '__main__':
    main()
