import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, matthews_corrcoef,
    confusion_matrix, roc_curve, classification_report,
)
from sklearn.model_selection import learning_curve

PLOTS_DIR = 'plots'
os.makedirs(PLOTS_DIR, exist_ok=True)


def compute_metrics(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    mcc = matthews_corrcoef(y_test, y_pred)

    print("\n=== WYNIKI MODELU ===")
    print(f"Accuracy  : {acc:.4f}")
    print(f"F1-Score  : {f1:.4f}")
    print(f"ROC-AUC   : {auc:.4f}")
    print(f"MCC       : {mcc:.4f}")
    print()
    print(classification_report(y_test, y_pred,
                                target_names=['Brak choroby (0)', 'Choroba (1)']))

    return {'accuracy': acc, 'f1': f1, 'roc_auc': auc, 'mcc': mcc}


def plot_confusion_matrix(model, X_test, y_test, save_path=None):
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Brak choroby', 'Choroba'],
                yticklabels=['Brak choroby', 'Choroba'])
    ax.set_title('Macierz Pomyłek')
    ax.set_ylabel('Prawdziwa klasa')
    ax.set_xlabel('Przewidziana klasa')
    plt.tight_layout()

    path = save_path or f'{PLOTS_DIR}/confusion_matrix.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()


def plot_roc_curve(model, X_test, y_test, save_path=None):
    y_prob = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(fpr, tpr, color='steelblue', lw=2, label=f'RF (AUC = {auc:.4f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=1.5, label='losowy (AUC = 0.50)')
    ax.set_xlabel('FPR (False Positive Rate)')
    ax.set_ylabel('TPR (True Positive Rate)')
    ax.set_title('Krzywa ROC')
    ax.legend(loc='lower right')
    plt.tight_layout()

    path = save_path or f'{PLOTS_DIR}/roc_curve.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()


def plot_feature_importance(model, feature_names, save_path=None):
    importances = model.feature_importances_
    std = np.std([t.feature_importances_ for t in model.estimators_], axis=0)
    idx = np.argsort(importances)[::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(range(len(idx)), importances[idx], yerr=std[idx],
           color='steelblue', alpha=0.85,
           error_kw={'elinewidth': 1.5, 'capsize': 4})
    ax.set_xticks(range(len(idx)))
    ax.set_xticklabels([feature_names[i] for i in idx], rotation=40, ha='right')
    ax.set_title('Ważność Cech (Feature Importance)')
    ax.set_ylabel('Ważność (Gini)')
    plt.tight_layout()

    path = save_path or f'{PLOTS_DIR}/feature_importance.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()


def plot_learning_curve(model, X, y, save_path=None):
    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y,
        cv=5, scoring='f1',
        train_sizes=np.linspace(0.1, 1.0, 10),
        n_jobs=-1,
    )

    t_mean = train_scores.mean(axis=1)
    t_std = train_scores.std(axis=1)
    v_mean = val_scores.mean(axis=1)
    v_std = val_scores.std(axis=1)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(train_sizes, t_mean, 'o-', color='steelblue', lw=2, label='trening')
    ax.fill_between(train_sizes, t_mean - t_std, t_mean + t_std, alpha=0.12, color='steelblue')
    ax.plot(train_sizes, v_mean, 'o-', color='tomato', lw=2, label='walidacja (CV)')
    ax.fill_between(train_sizes, v_mean - v_std, v_mean + v_std, alpha=0.12, color='tomato')
    ax.set_xlabel('Liczba próbek treningowych')
    ax.set_ylabel('F1-Score')
    ax.set_title('Krzywa Uczenia')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    path = save_path or f'{PLOTS_DIR}/learning_curve.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()
