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

sns.set_theme(style='whitegrid', palette='muted')


def compute_metrics(y_test, y_pred, y_prob):
    acc  = accuracy_score(y_test, y_pred)
    f1   = f1_score(y_test, y_pred)
    auc  = roc_auc_score(y_test, y_prob)
    mcc  = matthews_corrcoef(y_test, y_pred)

    print("\n" + "=" * 40)
    print("       WYNIKI MODELU")
    print("=" * 40)
    print(f"  Accuracy   : {acc:.4f}")
    print(f"  F1-Score   : {f1:.4f}")
    print(f"  ROC-AUC    : {auc:.4f}")
    print(f"  MCC        : {mcc:.4f}")
    print("=" * 40)
    print("\nRaport klasyfikacji:")
    print(classification_report(y_test, y_pred,
                                target_names=['Brak choroby (0)', 'Choroba (1)']))

    return {'accuracy': acc, 'f1': f1, 'roc_auc': auc, 'mcc': mcc}


def plot_confusion_matrix(y_test, y_pred, save=True):
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Brak choroby', 'Choroba'],
                yticklabels=['Brak choroby', 'Choroba'],
                linewidths=0.5, linecolor='gray')
    ax.set_title('Macierz Pomyłek (Confusion Matrix)', fontsize=14, pad=12)
    ax.set_ylabel('Wartość rzeczywista', fontsize=11)
    ax.set_xlabel('Wartość przewidywana', fontsize=11)
    plt.tight_layout()

    if save:
        plt.savefig(f'{PLOTS_DIR}/confusion_matrix.png', dpi=150, bbox_inches='tight')
        print(f"  Zapisano: {PLOTS_DIR}/confusion_matrix.png")
    plt.show()
    plt.close()


def plot_roc_curve(y_test, y_prob, save=True):
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(fpr, tpr, color='steelblue', lw=2.5,
            label=f'Random Forest (AUC = {auc:.4f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Losowy klasyfikator (AUC = 0.50)')
    ax.fill_between(fpr, tpr, alpha=0.07, color='steelblue')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate (FPR)', fontsize=11)
    ax.set_ylabel('True Positive Rate (TPR)', fontsize=11)
    ax.set_title('Krzywa ROC', fontsize=14, pad=12)
    ax.legend(loc='lower right', fontsize=10)
    plt.tight_layout()

    if save:
        plt.savefig(f'{PLOTS_DIR}/roc_curve.png', dpi=150, bbox_inches='tight')
        print(f"  Zapisano: {PLOTS_DIR}/roc_curve.png")
    plt.show()
    plt.close()


def plot_feature_importance(model, feature_names, top_n=13, save=True):
    importances = model.feature_importances_
    std = np.std([tree.feature_importances_ for tree in model.estimators_], axis=0)
    indices = np.argsort(importances)[::-1][:top_n]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(range(top_n), importances[indices],
           yerr=std[indices], color='steelblue', alpha=0.85,
           error_kw={'elinewidth': 1.5, 'capsize': 4})
    ax.set_xticks(range(top_n))
    ax.set_xticklabels([feature_names[i] for i in indices], rotation=40, ha='right')
    ax.set_title('Ważność Cech (Feature Importance – Gini)', fontsize=14, pad=12)
    ax.set_ylabel('Średni spadek zanieczyszczenia Gini', fontsize=11)
    plt.tight_layout()

    if save:
        plt.savefig(f'{PLOTS_DIR}/feature_importance.png', dpi=150, bbox_inches='tight')
        print(f"  Zapisano: {PLOTS_DIR}/feature_importance.png")
    plt.show()
    plt.close()


def plot_learning_curve(model, X, y, save=True):
    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y,
        cv=5, scoring='f1',
        train_sizes=np.linspace(0.1, 1.0, 10),
        n_jobs=-1,
    )

    t_mean, t_std = train_scores.mean(axis=1), train_scores.std(axis=1)
    v_mean, v_std = val_scores.mean(axis=1),   val_scores.std(axis=1)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(train_sizes, t_mean, 'o-', color='steelblue', lw=2, label='Trening')
    ax.fill_between(train_sizes, t_mean - t_std, t_mean + t_std, alpha=0.12, color='steelblue')
    ax.plot(train_sizes, v_mean, 'o-', color='tomato', lw=2, label='Walidacja (5-fold CV)')
    ax.fill_between(train_sizes, v_mean - v_std, v_mean + v_std, alpha=0.12, color='tomato')
    ax.set_xlabel('Liczba próbek treningowych', fontsize=11)
    ax.set_ylabel('F1-Score', fontsize=11)
    ax.set_title('Krzywa Uczenia (Learning Curve)', fontsize=14, pad=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        plt.savefig(f'{PLOTS_DIR}/learning_curve.png', dpi=150, bbox_inches='tight')
        print(f"  Zapisano: {PLOTS_DIR}/learning_curve.png")
    plt.show()
    plt.close()
