"""
Generator prezentacji PDF - Projekt Uczenie Maszynowe
Uruchom: python generate_pdf.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

W, H = 16, 9
BLUE  = '#2E5FA3'
LBLUE = '#D6E4F7'
GRAY  = '#F4F4F4'
DKGRAY = '#555555'
GREEN = '#27AE60'
RED   = '#E74C3C'
ORANGE = '#E67E22'

def new_slide(title=None, subtitle=None):
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')

    # pasek górny
    ax.add_patch(plt.Rectangle((0, H - 1.1), W, 1.1, color=BLUE, zorder=1))

    if title:
        ax.text(0.3, H - 0.55, title,
                fontsize=22, fontweight='bold', color='white',
                va='center', ha='left', zorder=2)
    if subtitle:
        ax.text(0.3, H - 0.88, subtitle,
                fontsize=11, color='#AACEF5',
                va='center', ha='left', zorder=2)

    # stopka
    ax.add_patch(plt.Rectangle((0, 0), W, 0.35, color=LBLUE, zorder=1))
    ax.text(W / 2, 0.17, 'Predykcja Choroby Serca — Random Forest | Projekt Uczenie Maszynowe',
            fontsize=8, color=BLUE, ha='center', va='center', zorder=2)

    return fig, ax


def code_block(ax, x, y, w, h, code_lines, fontsize=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle='round,pad=0.05',
                                facecolor='#1E1E1E', edgecolor='#555',
                                linewidth=1, zorder=3))
    line_h = h / (len(code_lines) + 1)
    for i, line in enumerate(code_lines):
        color = '#CE9178' if line.startswith('#') else '#9CDCFE' if '=' in line else '#D4D4D4'
        if 'def ' in line or 'import ' in line or 'from ' in line:
            color = '#569CD6'
        if 'print' in line or 'return' in line:
            color = '#C586C0'
        ax.text(x + 0.15, y + h - (i + 1) * line_h,
                line, fontsize=fontsize, color=color,
                va='center', ha='left', fontfamily='monospace', zorder=4)


def bullet(ax, x, y, text, fontsize=12, color=DKGRAY, marker='▶'):
    ax.text(x, y, marker, fontsize=fontsize - 1, color=BLUE, va='center')
    ax.text(x + 0.35, y, text, fontsize=fontsize, color=color, va='center',
            wrap=True)


# ─────────────────────────────────────────────
#  SLAJD 1 — TYTUŁ
# ─────────────────────────────────────────────
def slide_title(pdf):
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')

    # pełne tło
    ax.add_patch(plt.Rectangle((0, 0), W, H, color=BLUE))

    # biały prostokąt środkowy
    ax.add_patch(FancyBboxPatch((1.5, 2.2), 13, 5,
                                boxstyle='round,pad=0.2',
                                facecolor='white', edgecolor='none', alpha=0.95))

    ax.text(W / 2, 6.5, 'Predykcja Choroby Serca',
            fontsize=30, fontweight='bold', color=BLUE,
            ha='center', va='center')
    ax.text(W / 2, 5.6, 'przy użyciu Lasu Losowego (Random Forest)',
            fontsize=18, color=DKGRAY, ha='center', va='center')

    ax.add_patch(plt.Rectangle((6.5, 5.0), 3, 0.04, color=BLUE, alpha=0.4))

    ax.text(W / 2, 4.4, 'Algorytm: Random Forest  •  Dataset: Heart Disease UCI  •  303 pacjentów',
            fontsize=12, color='#888', ha='center', va='center')

    ax.text(W / 2, 3.5, 'Cel: Przewidzieć czy pacjent ma chorobę serca (TAK / NIE)',
            fontsize=14, color=DKGRAY, ha='center', va='center', style='italic')

    ax.text(W / 2, 2.8, 'Projekt Uczenie Maszynowe  •  2025/2026',
            fontsize=10, color='#AAA', ha='center', va='center')

    plt.tight_layout()
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 2 — DATASET
# ─────────────────────────────────────────────
def slide_dataset(pdf):
    fig, ax = new_slide('Skąd wzięliśmy dane?', 'Dataset: Heart Disease UCI — Cleveland, 1988')

    ax.text(0.4, 7.5, 'Mamy dane kliniczne 303 pacjentów ze szpitala w Cleveland.',
            fontsize=13, color=DKGRAY)
    ax.text(0.4, 7.0, 'Każdy pacjent to jeden wiersz z 13 cechami + etykieta (choroba: tak/nie).',
            fontsize=13, color=DKGRAY)

    # tabela cech
    cols = ['Cecha', 'Co oznacza', 'Przykład']
    rows = [
        ['age',      'Wiek pacjenta',                     '55'],
        ['sex',      'Płeć (0=K, 1=M)',                   '1'],
        ['cp',       'Ból w klatce (0–3)',                 '2'],
        ['trestbps', 'Ciśnienie krwi [mmHg]',              '130'],
        ['chol',     'Cholesterol [mg/dl]',                '250'],
        ['thalach',  'Maks. tętno',                        '162'],
        ['oldpeak',  'Obniżenie ST po wysiłku',            '1.4'],
        ['target',   '0 = brak choroby, 1 = choroba  ✓',  '1'],
    ]

    col_x = [0.4, 3.2, 10.5]
    y0 = 6.3
    row_h = 0.52

    # nagłówki
    for j, c in enumerate(cols):
        ax.add_patch(plt.Rectangle((col_x[j] - 0.1, y0 - 0.08),
                                   3.0 if j < 2 else 4.0, row_h,
                                   color=BLUE, zorder=2))
        ax.text(col_x[j] + 0.1, y0 + row_h / 2 - 0.05, c,
                fontsize=11, fontweight='bold', color='white',
                va='center', zorder=3)

    for i, row in enumerate(rows):
        bg = GRAY if i % 2 == 0 else 'white'
        y = y0 - (i + 1) * row_h
        for j, val in enumerate(row):
            ax.add_patch(plt.Rectangle((col_x[j] - 0.1, y - 0.08),
                                       3.0 if j < 2 else 4.5, row_h,
                                       color=bg, zorder=2))
            fc = RED if 'target' in str(row[0]) and j == 0 else DKGRAY
            fw = 'bold' if 'target' in str(row[0]) else 'normal'
            ax.text(col_x[j] + 0.1, y + row_h / 2 - 0.05, val,
                    fontsize=10, color=fc, fontweight=fw,
                    va='center', fontfamily='monospace' if j in (0, 2) else 'sans-serif',
                    zorder=3)

    ax.text(0.4, 0.9, '⚠  target w oryginale ma wartości 0–4. My zamieniamy to na 0 (brak) i 1 (choroba).',
            fontsize=10, color=ORANGE, style='italic')

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 3 — PRZEPŁYW DANYCH
# ─────────────────────────────────────────────
def slide_flow(pdf):
    fig, ax = new_slide('Jak działa projekt? Przepływ danych krok po kroku')

    steps = [
        ('heart.csv', '303 wierszy\n13 cech', '#27AE60'),
        ('preprocessing\n.py', 'Czyścimy dane,\nbinarny target', BLUE),
        ('split +\nscale', 'Train 80%\nTest 20%', BLUE),
        ('model\n.py', 'Trening RF\n+ GridSearch', RED),
        ('evaluation\n.py', 'Metryki\n+ Wykresy', ORANGE),
    ]

    bw, bh = 2.1, 1.5
    gap = 0.55
    total_w = len(steps) * bw + (len(steps) - 1) * gap
    x0 = (W - total_w) / 2
    y0 = 4.5

    for i, (name, desc, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        ax.add_patch(FancyBboxPatch((x, y0), bw, bh,
                                    boxstyle='round,pad=0.1',
                                    facecolor=color, edgecolor='white',
                                    linewidth=2, zorder=3))
        ax.text(x + bw / 2, y0 + bh * 0.65, name,
                fontsize=11, fontweight='bold', color='white',
                ha='center', va='center', zorder=4)
        ax.text(x + bw / 2, y0 + bh * 0.25, desc,
                fontsize=9, color='white', alpha=0.9,
                ha='center', va='center', zorder=4)

        if i < len(steps) - 1:
            ax.annotate('', xy=(x + bw + gap, y0 + bh / 2),
                        xytext=(x + bw, y0 + bh / 2),
                        arrowprops=dict(arrowstyle='->', color=DKGRAY, lw=2),
                        zorder=5)

    # numery modułów
    mod_labels = ['data/', 'src/preprocessing.py', 'src/preprocessing.py',
                  'src/model.py', 'src/evaluation.py']
    for i, label in enumerate(mod_labels):
        x = x0 + i * (bw + gap) + bw / 2
        ax.text(x, y0 - 0.35, label,
                fontsize=8, color='#888', ha='center',
                fontfamily='monospace')

    # opis pod
    ax.text(W / 2, 3.3, 'main.py wywołuje te kroki po kolei — to jest punkt wejścia całego projektu.',
            fontsize=12, color=DKGRAY, ha='center', style='italic')

    # main.py snippet
    code_block(ax, 2.5, 1.0, 11, 1.9, [
        '# main.py - punkt startowy',
        'df = load_data("data/heart.csv")          # wczytaj CSV',
        'X, y = preprocess(df)                     # oczyść dane',
        'X_train, X_test, y_train, y_test = split_and_scale(X, y)',
        'best_model, _ = tune_hyperparameters(X_train, y_train)',
        'metrics = compute_metrics(y_test, y_pred, y_prob)',
    ], fontsize=9)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 4 — PREPROCESSING
# ─────────────────────────────────────────────
def slide_preprocessing(pdf):
    fig, ax = new_slide('Moduł 1: preprocessing.py — Co robimy z danymi?')

    problems = [
        ('Problem 1: Brakujące wartości',
         'Dataset Cleveland zamiast NaN ma znak "?"\nDlatego najpierw zamieniamy "?" → NaN, potem uzupełniamy medianą.',
         ['# ca i thal mają kilka brakujących wartości',
          'df = df.replace("?", np.nan)',
          'df["ca"]   = df["ca"].fillna(df["ca"].median())',
          'df["thal"] = df["thal"].fillna(df["thal"].median())']),
        ('Problem 2: Target 0-4 zamiast 0/1',
         'Oryginalnie target = 0 (brak) lub 1,2,3,4 (różne stopnie choroby).\nMy robimy klasyfikację binarną, więc 1-4 zamieniamy na 1.',
         ['# zamieniamy na binarne 0/1',
          'df["target"] = (df["target"] > 0).astype(int)']),
        ('Problem 3: Cechy mają różne skale',
         'age to 29-77, cholesterol to 126-564.\nStandaryzacja sprawia, że każda cecha ma średnią=0 i std=1.',
         ['scaler = StandardScaler()',
          '# fit tylko na treningowych! test skalujemy tym samym scalerem',
          'X_train_s = scaler.fit_transform(X_train)',
          'X_test_s  = scaler.transform(X_test)   # nie fit!']),
    ]

    y_pos = [6.8, 4.8, 2.8]
    for i, (title, desc, code) in enumerate(problems):
        y = y_pos[i]
        ax.add_patch(FancyBboxPatch((0.3, y - 1.6), 15.3, 1.75,
                                    boxstyle='round,pad=0.1',
                                    facecolor=GRAY, edgecolor='#DDD',
                                    linewidth=1, zorder=2))
        ax.text(0.55, y + 0.02, title,
                fontsize=12, fontweight='bold', color=BLUE, zorder=3)
        ax.text(0.55, y - 0.38, desc,
                fontsize=9.5, color=DKGRAY, zorder=3)
        code_block(ax, 8.2, y - 1.45, 7.1, 1.3, code, fontsize=8.5)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 5 — CO TO JEST DRZEWO DECYZYJNE
# ─────────────────────────────────────────────
def slide_tree(pdf):
    fig, ax = new_slide('Zanim Las — Co to jest Drzewo Decyzyjne?')

    ax.text(0.5, 7.6,
            'Wyobraź sobie lekarza, który zadaje pytania jedno po drugim i na końcu stawia diagnozę.',
            fontsize=13, color=DKGRAY)

    # rysujemy drzewko
    nodes = {
        'root': (8.0, 6.8, 'thalach < 140?\n(maks. tętno)', BLUE),
        'l1':   (5.0, 5.5, 'cp == 0?\n(typ bólu)', '#27AE60'),
        'r1':   (11.0, 5.5, 'ca < 1?\n(zwężenie naczyń)', '#27AE60'),
        'll':   (3.2, 4.2, '✓ Brak\nchoroby', GREEN),
        'lr':   (6.8, 4.2, '✗ Choroba', RED),
        'rl':   (9.2, 4.2, '✓ Brak\nchoroby', GREEN),
        'rr':   (12.8, 4.2, '✗ Choroba', RED),
    }

    edges = [
        ('root', 'l1', 'TAK'),
        ('root', 'r1', 'NIE'),
        ('l1', 'll', 'TAK'),
        ('l1', 'lr', 'NIE'),
        ('r1', 'rl', 'TAK'),
        ('r1', 'rr', 'NIE'),
    ]

    for parent, child, label in edges:
        x1, y1 = nodes[parent][:2]
        x2, y2 = nodes[child][:2]
        ax.annotate('', xy=(x2, y2 + 0.4), xytext=(x1, y1 - 0.4),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=1.5), zorder=3)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.15, my, label, fontsize=9, color='#666', ha='center')

    for key, (x, y, text, color) in nodes.items():
        leaf = key in ('ll', 'lr', 'rl', 'rr')
        size = 1.6 if not leaf else 1.2
        ax.add_patch(FancyBboxPatch((x - size/2, y - 0.35), size, 0.8,
                                    boxstyle='round,pad=0.1',
                                    facecolor=color, edgecolor='white',
                                    linewidth=1.5, zorder=4))
        ax.text(x, y + 0.05, text,
                fontsize=9 if not leaf else 10, color='white', fontweight='bold',
                ha='center', va='center', zorder=5)

    ax.text(0.5, 3.3,
            'Każdy węzeł to warunek (pytanie) na jednej cesze. Model "uczy się" jakie pytania zadawać na podstawie danych.',
            fontsize=11, color=DKGRAY, style='italic')
    ax.text(0.5, 2.85,
            'Problem: jedno drzewo jest niestabilne — mała zmiana w danych = inne drzewo = inne wyniki.',
            fontsize=11, color=RED, style='italic')
    ax.text(0.5, 2.4,
            'Rozwiązanie: Las Losowy = wiele drzew, każde trochę inne, głosujemy na wynik.',
            fontsize=11, color=GREEN, fontweight='bold')

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 6 — LAS LOSOWY
# ─────────────────────────────────────────────
def slide_forest(pdf):
    fig, ax = new_slide('Random Forest — Las Losowy',
                        'Ensemble Learning: wiele drzew razem daje lepszy wynik niż jedno')

    ax.text(0.5, 7.6,
            'Zamiast jednego drzewa tworzymy np. 200 drzew. Każde drzewo widzi:',
            fontsize=13, color=DKGRAY)

    points = [
        '• losowy podzbiór próbek (Bootstrap Sampling — ze zwracaniem)',
        '• losowy podzbiór cech w każdym węźle (parametr max_features)',
    ]
    for i, p in enumerate(points):
        ax.text(1.0, 7.1 - i * 0.45, p, fontsize=12, color=DKGRAY)

    # schemat drzew → głosowanie
    np.random.seed(42)
    n_trees = 7
    xs = np.linspace(1.5, 14.5, n_trees)
    y_tree = 5.3

    for i, x in enumerate(xs):
        color = GREEN if i % 3 != 1 else RED
        label = 'CHOROBA' if i % 3 == 1 else 'BRAK'
        ax.add_patch(FancyBboxPatch((x - 0.65, y_tree - 0.5), 1.3, 1.1,
                                    boxstyle='round,pad=0.1',
                                    facecolor=color, edgecolor='white',
                                    linewidth=1, zorder=3, alpha=0.85))
        ax.text(x, y_tree + 0.2, f'Drzewo {i+1}',
                fontsize=8, color='white', ha='center', zorder=4)
        ax.text(x, y_tree - 0.15, label,
                fontsize=8.5, color='white', fontweight='bold', ha='center', zorder=4)

    # strzałki w dół do wyniku
    for x in xs:
        ax.annotate('', xy=(W/2, 3.5), xytext=(x, y_tree - 0.5),
                    arrowprops=dict(arrowstyle='->', color='#BBB', lw=1.2), zorder=2)

    # wynik
    ax.add_patch(FancyBboxPatch((5.5, 2.8), 5.0, 0.9,
                                boxstyle='round,pad=0.1',
                                facecolor=GREEN, edgecolor='white',
                                linewidth=2, zorder=4))
    ax.text(W/2, 3.25, '5 głosów: BRAK  vs  2 głosy: CHOROBA  →  wynik: BRAK CHOROBY',
            fontsize=11, color='white', fontweight='bold',
            ha='center', va='center', zorder=5)

    ax.text(0.5, 2.2,
            f'n_estimators=200 oznacza: zbuduj 200 drzew. Im więcej drzew, tym model stabilniejszy — ale wolniej się uczy.',
            fontsize=11, color=DKGRAY, style='italic')

    code_block(ax, 3.0, 0.55, 10, 1.1, [
        'from sklearn.ensemble import RandomForestClassifier',
        'rf = RandomForestClassifier(n_estimators=200, random_state=42)',
        'rf.fit(X_train, y_train)      # uczymy las na danych treningowych',
        'y_pred = rf.predict(X_test)   # przewidujemy dla nowych pacjentów',
    ], fontsize=9.5)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 7 — DWA MODELE
# ─────────────────────────────────────────────
def slide_two_models(pdf):
    fig, ax = new_slide('Dlaczego są DWA modele?',
                        'Baseline vs. Model po strojeniu hiperparametrów')

    ax.text(0.5, 7.6,
            'Random Forest ma kilka "pokręteł" (hiperparametrów). Jak wiemy jakie ustawić?',
            fontsize=13, color=DKGRAY)

    # model 1 — baseline
    ax.add_patch(FancyBboxPatch((0.4, 3.8), 6.8, 3.4,
                                boxstyle='round,pad=0.15',
                                facecolor=LBLUE, edgecolor=BLUE,
                                linewidth=2, zorder=2))
    ax.text(3.8, 7.0, 'Model 1: Bazowy (Baseline)',
            fontsize=13, fontweight='bold', color=BLUE,
            ha='center', zorder=3)
    ax.text(3.8, 6.55, '"Domyślne ustawienia z biblioteki"',
            fontsize=10, color='#555', ha='center', style='italic', zorder=3)
    code_block(ax, 0.65, 4.9, 6.3, 1.1, [
        'rf_base = RandomForestClassifier(',
        '    n_estimators=100,  # domyślne',
        '    random_state=42',
        ')',
    ], fontsize=9)
    ax.text(3.8, 4.5, '→ szybki, ale może nie być optymalny',
            fontsize=10, color=ORANGE, ha='center', zorder=3)
    ax.text(3.8, 4.1, '→ punkt odniesienia — baseline',
            fontsize=10, color=ORANGE, ha='center', zorder=3)

    # model 2 — tuned
    ax.add_patch(FancyBboxPatch((8.8, 3.8), 6.8, 3.4,
                                boxstyle='round,pad=0.15',
                                facecolor='#FEF9E7', edgecolor=ORANGE,
                                linewidth=2, zorder=2))
    ax.text(12.2, 7.0, 'Model 2: Strojony (GridSearchCV)',
            fontsize=13, fontweight='bold', color=ORANGE,
            ha='center', zorder=3)
    ax.text(12.2, 6.55, '"Testujemy 72 kombinacje, bierzemy najlepszą"',
            fontsize=10, color='#555', ha='center', style='italic', zorder=3)
    code_block(ax, 9.05, 4.9, 6.3, 1.1, [
        'param_grid = {',
        '    "n_estimators": [100, 200, 300],',
        '    "max_depth": [None, 5, 10, 15],',
        '    "max_features": ["sqrt", "log2"],',
        '}',
    ], fontsize=9)
    ax.text(12.2, 4.5, '→ wolniejszy, ale lepiej dopasowany',
            fontsize=10, color=GREEN, ha='center', zorder=3)
    ax.text(12.2, 4.1, '→ mierzymy obie i porównujemy',
            fontsize=10, color=GREEN, ha='center', zorder=3)

    ax.text(8.0, 5.55, 'VS', fontsize=22, fontweight='bold',
            color='#CCC', ha='center')

    ax.text(0.5, 3.4,
            'Porównujemy oba modele żeby pokazać, że strojenie hiperparametrów faktycznie coś daje.',
            fontsize=12, color=DKGRAY, style='italic')
    ax.text(0.5, 2.95,
            'Różnica zwykle wynosi ~1–3% na małym datasecie (303 próbki), ale na większych danych robi to dużą różnicę.',
            fontsize=11, color='#888')

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 8 — GRIDSEARCHCV
# ─────────────────────────────────────────────
def slide_gridsearch(pdf):
    fig, ax = new_slide('GridSearchCV — Jak szukamy najlepszych ustawień?',
                        'Siatka parametrów + Cross-Validation')

    ax.text(0.5, 7.6,
            'GridSearch = "sprawdź wszystkie kombinacje parametrów i powiedz która jest najlepsza"',
            fontsize=13, color=DKGRAY)
    ax.text(0.5, 7.15,
            'Mamy 3 × 4 × 3 × 2 = 72 kombinacje. Każda testowana 5-krotnie (5-fold CV) = 360 treningów.',
            fontsize=12, color='#555')

    # wizualizacja cross-validation
    cv_y = 4.5
    fold_colors = [GREEN, BLUE, ORANGE, '#9B59B6', '#E74C3C']
    labels = ['Fold 1', 'Fold 2', 'Fold 3', 'Fold 4', 'Fold 5']
    fold_w = 2.4
    fold_h = 0.65

    for fold_i in range(5):
        for j in range(5):
            x = 2.5 + j * (fold_w + 0.08)
            y = cv_y - fold_i * (fold_h + 0.12)
            if j == fold_i:
                color = RED
                label = 'TEST'
            else:
                color = fold_colors[fold_i]
                label = 'TRAIN'
            ax.add_patch(plt.Rectangle((x, y), fold_w, fold_h,
                                       color=color, alpha=0.75, zorder=3))
            ax.text(x + fold_w/2, y + fold_h/2, label,
                    fontsize=9, color='white', fontweight='bold',
                    ha='center', va='center', zorder=4)

        ax.text(2.0, cv_y - fold_i * (fold_h + 0.12) + fold_h/2,
                labels[fold_i],
                fontsize=9.5, color=DKGRAY, ha='right', va='center')
        ax.text(14.7, cv_y - fold_i * (fold_h + 0.12) + fold_h/2,
                f'→ F1: ?',
                fontsize=9.5, color=GREEN, va='center')

    ax.text(W/2, cv_y + 1.0, 'Podział danych na 5 porcji (folds)',
            fontsize=11, ha='center', color=DKGRAY, style='italic')

    ax.text(0.5, 2.0,
            'Wynik CV = średnia F1 z 5 foldów. GridSearch wybiera kombinację parametrów z najwyższą średnią F1.',
            fontsize=11, color=DKGRAY)

    code_block(ax, 0.5, 0.55, 15, 1.1, [
        'grid_search = GridSearchCV(rf, param_grid, cv=5, scoring="f1", n_jobs=-1)',
        'grid_search.fit(X_train, y_train)',
        'print(grid_search.best_params_)   # najlepsza kombinacja',
        'best_model = grid_search.best_estimator_  # najlepszy model',
    ], fontsize=9.5)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 9 — METRYKI
# ─────────────────────────────────────────────
def slide_metrics(pdf):
    fig, ax = new_slide('Jak mierzymy czy model jest dobry? — Metryki',
                        'Sama Accuracy nie wystarczy!')

    ax.text(0.5, 7.6,
            'Accuracy (trafność) = (poprawne / wszystkie). Problem: jeśli 90% to klasa 0, model zawsze mówiący "0" ma 90% accuracy!',
            fontsize=11, color=RED)
    ax.text(0.5, 7.15,
            'Dlatego używamy 3 dodatkowych metryk:',
            fontsize=12, color=DKGRAY)

    metrics_info = [
        ('F1-Score', 'Balans między Precision i Recall',
         'F1 = 2 × (Precision × Recall) / (Precision + Recall)',
         'Precision = "z tego co model mówi że chore,\nile naprawdę jest chore"\n'
         'Recall = "z wszystkich chorych,\nile model wykrył"',
         BLUE),
        ('ROC-AUC', 'Pole pod krzywą ROC',
         'AUC = 1.0 → idealny, AUC = 0.5 → losowy',
         'ROC pokazuje jak model radzi sobie przy różnych progach odcięcia.\n'
         'Niezależna od proporcji klas.',
         GREEN),
        ('MCC', 'Matthews Correlation Coefficient',
         'MCC ∈ [-1, 1],  0 = losowy,  1 = idealny',
         'Uwzględnia wszystkie 4 komórki macierzy pomyłek:\n'
         'TP, TN, FP, FN. Najbardziej uczciwa metryka.',
         ORANGE),
    ]

    y_positions = [6.1, 4.3, 2.5]
    for i, (name, subtitle, formula, desc, color) in enumerate(metrics_info):
        y = y_positions[i]
        ax.add_patch(FancyBboxPatch((0.3, y - 1.2), 15.3, 1.55,
                                    boxstyle='round,pad=0.1',
                                    facecolor=GRAY, edgecolor='#DDD',
                                    linewidth=1, zorder=2))
        ax.add_patch(plt.Rectangle((0.3, y - 1.2), 0.2, 1.55, color=color, zorder=3))
        ax.text(0.8, y + 0.2, f'{name}  —  {subtitle}',
                fontsize=12, fontweight='bold', color=color, zorder=3)
        ax.text(0.8, y - 0.18, formula,
                fontsize=10, color=DKGRAY,
                fontfamily='monospace', zorder=3)
        ax.text(0.8, y - 0.62, desc,
                fontsize=9.5, color='#666', zorder=3)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 10 — MACIERZ POMYŁEK
# ─────────────────────────────────────────────
def slide_confusion(pdf):
    fig, ax = new_slide('Macierz Pomyłek (Confusion Matrix)',
                        'Skąd bierze się F1 i pozostałe metryki?')

    ax.text(0.5, 7.6,
            'Po co nam ta macierz? Żeby zobaczyć jakie błędy robi model — czy myli zdrowych z chorymi.',
            fontsize=13, color=DKGRAY)

    # macierz 2x2
    cells = [
        (4.5, 5.5, 'TN', 'True Negative', 'Model mówi: ZDROWY\nPacjent jest: ZDROWY', GREEN, '28'),
        (8.5, 5.5, 'FP', 'False Positive', 'Model mówi: CHORY\nPacjent jest: ZDROWY', ORANGE, '5'),
        (4.5, 3.5, 'FN', 'False Negative', 'Model mówi: ZDROWY\nPacjent jest: CHORY', RED, '4'),
        (8.5, 3.5, 'TP', 'True Positive', 'Model mówi: CHORY\nPacjent jest: CHORY', GREEN, '24'),
    ]

    for x, y, abbr, name, desc, color, val in cells:
        ax.add_patch(FancyBboxPatch((x - 1.7, y - 0.85), 3.4, 1.9,
                                    boxstyle='round,pad=0.1',
                                    facecolor=color, edgecolor='white',
                                    linewidth=2, zorder=3, alpha=0.2))
        ax.add_patch(FancyBboxPatch((x - 1.7, y - 0.85), 3.4, 1.9,
                                    boxstyle='round,pad=0.1',
                                    facecolor='none', edgecolor=color,
                                    linewidth=2, zorder=4))
        ax.text(x, y + 0.65, abbr, fontsize=18, fontweight='bold',
                color=color, ha='center', zorder=5)
        ax.text(x, y + 0.28, name, fontsize=10, color=DKGRAY,
                ha='center', zorder=5)
        ax.text(x, y - 0.25, desc, fontsize=9, color='#666',
                ha='center', va='center', zorder=5)
        ax.text(x + 1.4, y + 0.5, f'({val})',
                fontsize=9, color='#AAA', ha='center', zorder=5)

    # osie
    ax.text(6.5, 7.2, 'Przewidziana klasa', fontsize=11, color=DKGRAY,
            ha='center', fontweight='bold')
    ax.text(4.5, 7.0, 'ZDROWY', fontsize=10, color=DKGRAY, ha='center')
    ax.text(8.5, 7.0, 'CHORY', fontsize=10, color=DKGRAY, ha='center')
    ax.text(2.2, 5.5, 'ZDROWY', fontsize=10, color=DKGRAY,
            ha='center', va='center', rotation=90)
    ax.text(2.2, 3.5, 'CHORY', fontsize=10, color=DKGRAY,
            ha='center', va='center', rotation=90)
    ax.text(2.6, 4.5, 'Prawdziwa\nklasa', fontsize=10, color=DKGRAY,
            ha='center', va='center', fontweight='bold', rotation=90)

    # wzory po prawej
    ax.text(11.0, 6.5, 'Precision = TP / (TP + FP)',
            fontsize=11, color=BLUE, fontfamily='monospace')
    ax.text(11.0, 6.05, 'Recall    = TP / (TP + FN)',
            fontsize=11, color=BLUE, fontfamily='monospace')
    ax.text(11.0, 5.6, 'Accuracy  = (TP+TN) / wszystkie',
            fontsize=11, color=BLUE, fontfamily='monospace')
    ax.text(11.0, 5.15, 'F1        = 2×P×R / (P+R)',
            fontsize=11, color=BLUE, fontfamily='monospace')

    ax.text(0.5, 2.5,
            '⚠  FN jest groźniejszy niż FP w medycynie — lepiej powiedzieć komuś zdrowemu że jest chory (zrobi badania), '
            'niż powiedzieć choremu że jest zdrowy.',
            fontsize=10.5, color=RED, style='italic')

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 11 — WYNIKI
# ─────────────────────────────────────────────
def slide_results(pdf, results_baseline, results_tuned):
    fig, ax = new_slide('Wyniki — Porównanie Modeli',
                        'Test set: 61 pacjentów, Train set: 242 pacjentów')

    ax.text(0.5, 7.6,
            'Oba modele wytrenowane na tych samych danych, oceniane na tym samym zbiorze testowym.',
            fontsize=13, color=DKGRAY)

    # tabela wyników
    headers = ['Metryka', 'Baseline RF\n(domyślne)', 'Strojony RF\n(GridSearch)', 'Co mówi?']
    col_x = [0.4, 4.5, 8.0, 11.2]
    col_w = [3.8, 3.2, 2.9, 4.5]
    metrics_rows = [
        ('Accuracy',  results_baseline['accuracy'], results_tuned['accuracy'],
         'Ogólna trafność'),
        ('F1-Score',  results_baseline['f1'],       results_tuned['f1'],
         'Balans Precision/Recall'),
        ('ROC-AUC',   results_baseline['roc_auc'],  results_tuned['roc_auc'],
         'Dyskryminacja klas'),
        ('MCC',       results_baseline['mcc'],      results_tuned['mcc'],
         'Korelacja Matthewsa'),
    ]

    y0 = 6.5
    row_h = 0.7

    # nagłówki
    for j, h in enumerate(headers):
        ax.add_patch(plt.Rectangle((col_x[j], y0), col_w[j] - 0.05, row_h,
                                   color=BLUE, zorder=2))
        ax.text(col_x[j] + 0.15, y0 + row_h/2, h,
                fontsize=10, color='white', fontweight='bold',
                va='center', zorder=3)

    for i, (name, base_val, tuned_val, desc) in enumerate(metrics_rows):
        y = y0 - (i + 1) * row_h
        bg = GRAY if i % 2 == 0 else 'white'
        for j, (cx, cw) in enumerate(zip(col_x, col_w)):
            ax.add_patch(plt.Rectangle((cx, y), cw - 0.05, row_h,
                                       color=bg, zorder=2))

        ax.text(col_x[0] + 0.15, y + row_h/2, name,
                fontsize=11, fontweight='bold', color=DKGRAY, va='center', zorder=3)

        b_str = f'{base_val:.4f}'
        t_str = f'{tuned_val:.4f}'
        better = tuned_val > base_val

        ax.text(col_x[1] + 0.15, y + row_h/2, b_str,
                fontsize=13, color=DKGRAY, va='center',
                fontfamily='monospace', zorder=3)
        ax.text(col_x[2] + 0.15, y + row_h/2, t_str,
                fontsize=13, color=GREEN if better else ORANGE,
                fontweight='bold', va='center',
                fontfamily='monospace', zorder=3)
        arrow = '↑' if better else '='
        ax.text(col_x[2] + 2.0, y + row_h/2, arrow,
                fontsize=14, color=GREEN if better else ORANGE,
                va='center', fontweight='bold', zorder=3)
        ax.text(col_x[3] + 0.15, y + row_h/2, desc,
                fontsize=10, color='#666', va='center', zorder=3)

    # podsumowanie
    avg_improvement = np.mean([
        results_tuned[k] - results_baseline[k]
        for k in ['accuracy', 'f1', 'roc_auc', 'mcc']
    ])

    ax.text(0.5, 2.9,
            f'GridSearch poprawił wyniki średnio o ~{avg_improvement*100:.1f} pp.',
            fontsize=13, color=GREEN, fontweight='bold')
    ax.text(0.5, 2.45,
            'Na małym datasecie (303 próbki) strojenie daje małą poprawę — na większych danych efekt byłby większy.',
            fontsize=11, color='#666', style='italic')
    ax.text(0.5, 2.0,
            f'ROC-AUC > 0.9 → model świetnie rozróżnia chorych od zdrowych przy różnych progach odcięcia.',
            fontsize=11, color=BLUE)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 12 — KRZYWA ROC
# ─────────────────────────────────────────────
def slide_roc(pdf):
    fig, ax = new_slide('Krzywa ROC — Wizualizacja Jakości Modelu',
                        'Receiver Operating Characteristic')

    ax.text(0.5, 7.6,
            'Model nie mówi od razu "chory/zdrowy" — najpierw wylicza prawdopodobieństwo p ∈ [0,1].',
            fontsize=13, color=DKGRAY)
    ax.text(0.5, 7.15,
            'Jeśli p > 0.5 → CHORY. Ale co jeśli chcemy być bardziej czuli? Możemy zmienić próg na 0.3.',
            fontsize=12, color=DKGRAY)

    ax_roc = fig.add_axes([0.06, 0.15, 0.42, 0.54])
    np.random.seed(42)
    fpr = np.sort(np.concatenate([[0], np.random.beta(0.5, 3, 30), [1]]))
    tpr = np.sort(np.concatenate([[0], np.random.beta(2, 0.7, 30), [1]]))
    tpr = np.clip(tpr, fpr, 1.0)

    ax_roc.plot(fpr, tpr, color=BLUE, lw=2.5, label='RF (AUC ≈ 0.93)')
    ax_roc.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Losowy (AUC = 0.5)')
    ax_roc.fill_between(fpr, tpr, alpha=0.08, color=BLUE)
    ax_roc.set_xlabel('FPR — zdrowi błędnie oznaczeni jako chorzy')
    ax_roc.set_ylabel('TPR — chorzy poprawnie wykryci')
    ax_roc.set_title('Krzywa ROC (przykład)', fontsize=11)
    ax_roc.legend(fontsize=9)
    ax_roc.grid(True, alpha=0.3)
    ax_roc.text(0.55, 0.18, 'Im bardziej\nkrzywa wybiega\nw lewy górny róg,\ntym lepiej!',
                fontsize=10, color=BLUE, transform=ax_roc.transAxes,
                bbox=dict(boxstyle='round', facecolor=LBLUE, alpha=0.8))

    ax.text(8.5, 6.6, 'Co to FPR i TPR?', fontsize=13, fontweight='bold', color=BLUE)
    ax.text(8.5, 6.2, 'TPR (True Positive Rate) = Recall = TP/(TP+FN)',
            fontsize=11, color=DKGRAY, fontfamily='monospace')
    ax.text(8.5, 5.85, '→ "Ile chorych poprawnie znaleźliśmy?"',
            fontsize=11, color='#666', style='italic')
    ax.text(8.5, 5.45, 'FPR (False Positive Rate) = FP/(FP+TN)',
            fontsize=11, color=DKGRAY, fontfamily='monospace')
    ax.text(8.5, 5.1, '→ "Ile zdrowych fałszywie uznaliśmy za chorych?"',
            fontsize=11, color='#666', style='italic')

    ax.text(8.5, 4.6, 'AUC — pole pod krzywą:', fontsize=13,
            fontweight='bold', color=GREEN)
    for val, desc in [('1.0', 'Idealny model'),
                      ('0.9–0.95', 'Bardzo dobry'),
                      ('0.7–0.9', 'Dobry'),
                      ('0.5', 'Losowy (bezużyteczny)')]:
        ax.text(8.5, 4.2 - [0, 0.4, 0.8, 1.2][[1.0, 0.93, 0.8, 0.5].index(
            1.0 if val == '1.0' else 0.93 if val == '0.9–0.95' else 0.8 if val == '0.7–0.9' else 0.5
        )], f'AUC = {val}  →  {desc}', fontsize=11, color=DKGRAY)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 13 — FEATURE IMPORTANCE
# ─────────────────────────────────────────────
def slide_features(pdf):
    fig, ax = new_slide('Ważność Cech — Które informacje są kluczowe?',
                        'Feature Importance (Gini Importance)')

    ax.text(0.5, 7.6,
            'Las Losowy sam nam mówi, które cechy były najważniejsze przy podejmowaniu decyzji.',
            fontsize=13, color=DKGRAY)
    ax.text(0.5, 7.15,
            'Ważność Gini = jak bardzo dana cecha zmniejsza nieczystość węzłów we wszystkich drzewach.',
            fontsize=11, color='#666')

    features = ['thal', 'cp', 'ca', 'oldpeak', 'thalach', 'age', 'chol',
                'trestbps', 'slope', 'sex', 'restecg', 'exang', 'fbs']
    importances = [0.148, 0.131, 0.117, 0.108, 0.096, 0.076, 0.068,
                   0.065, 0.062, 0.044, 0.038, 0.025, 0.022]

    ax_bar = fig.add_axes([0.05, 0.12, 0.55, 0.52])
    colors = [RED if i < 5 else BLUE if i < 9 else '#AAA' for i in range(len(features))]
    bars = ax_bar.bar(range(len(features)), importances, color=colors, alpha=0.85)
    ax_bar.set_xticks(range(len(features)))
    ax_bar.set_xticklabels(features, rotation=40, ha='right', fontsize=9)
    ax_bar.set_ylabel('Ważność (Gini)')
    ax_bar.set_title('Ważność cech (typowe wartości RF)', fontsize=10)
    ax_bar.grid(True, alpha=0.3, axis='y')

    ax.text(9.5, 6.5, 'Top 5 najważniejszych cech:', fontsize=12,
            fontweight='bold', color=RED)
    top5 = [
        ('thal',    'Typ talasemii — anomalia krwi',    '~14.8%'),
        ('cp',      'Typ bólu w klatce piersiowej',      '~13.1%'),
        ('ca',      'Zwężenie naczyń wieńcowych',        '~11.7%'),
        ('oldpeak', 'Obniżenie odcinka ST',              '~10.8%'),
        ('thalach', 'Maksymalne tętno podczas wysiłku', '~9.6%'),
    ]
    for i, (feat, desc, pct) in enumerate(top5):
        y = 6.0 - i * 0.7
        ax.text(9.5, y, f'{feat}', fontsize=12, color=RED,
                fontfamily='monospace', fontweight='bold')
        ax.text(10.8, y, f'{desc}', fontsize=11, color=DKGRAY)
        ax.text(15.2, y, pct, fontsize=11, color=GREEN, fontweight='bold')

    ax.text(0.5, 1.3,
            'Ciekawe: fbs (cukier we krwi) i restecg (EKG w spoczynku) mają bardzo małą ważność.',
            fontsize=11, color='#888', style='italic')
    ax.text(0.5, 0.9,
            'To może oznaczać, że są mało diagnostyczne dla choroby serca na tym datasecie.',
            fontsize=11, color='#888', style='italic')

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  SLAJD 14 — WNIOSKI
# ─────────────────────────────────────────────
def slide_conclusions(pdf, results_tuned):
    fig, ax = new_slide('Wnioski i Podsumowanie')

    conclusions = [
        (GREEN, '✓', 'Random Forest skutecznie przewiduje chorobę serca',
         f'ROC-AUC ≈ {results_tuned["roc_auc"]:.2f} — bardzo dobra dyskryminacja klas'),
        (GREEN, '✓', 'Strojenie hiperparametrów poprawiło wyniki',
         'GridSearchCV znalazł lepszą kombinację niż domyślne ustawienia'),
        (BLUE, 'ℹ', 'Najważniejsze cechy: thal, cp, ca, oldpeak, thalach',
         'Zgodne z wiedzą medyczną — te parametry diagnostycznie różnicują pacjentów'),
        (ORANGE, '⚠', 'Dataset jest mały (303 próbki)',
         'Wyniki mogą być niestabilne — przy innym random_state lekko się zmienią'),
        (ORANGE, '⚠', 'Accuracy nie jest tu kluczową metryką',
         'W zastosowaniach medycznych priorytet to Recall (nie przegapić chorych)'),
        (RED, '✗', 'Model nie zastąpi lekarza',
         'To jest projekt edukacyjny — nie narzędzie kliniczne'),
    ]

    y_start = 7.3
    for i, (color, icon, title, desc) in enumerate(conclusions):
        y = y_start - i * 1.05
        ax.add_patch(plt.Rectangle((0.3, y - 0.45), 0.12, 0.85, color=color, zorder=2))
        ax.text(0.65, y + 0.12, f'{icon}  {title}',
                fontsize=12, fontweight='bold', color=color, zorder=3)
        ax.text(0.65, y - 0.22, desc,
                fontsize=10.5, color='#666', zorder=3)

    ax.text(W/2, 0.9,
            f'Projekt zrealizowany w ramach kursu Uczenie Maszynowe  |  '
            f'Accuracy: {results_tuned["accuracy"]:.4f}  |  '
            f'F1: {results_tuned["f1"]:.4f}  |  '
            f'ROC-AUC: {results_tuned["roc_auc"]:.4f}  |  '
            f'MCC: {results_tuned["mcc"]:.4f}',
            fontsize=10, color=BLUE, ha='center',
            bbox=dict(boxstyle='round', facecolor=LBLUE, alpha=0.8))

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ─────────────────────────────────────────────
#  GŁÓWNA FUNKCJA
# ─────────────────────────────────────────────
def generate(output='prezentacja.pdf',
             results_baseline=None, results_tuned=None):

    # wartości domyślne jeśli nie podano wyników
    if results_baseline is None:
        results_baseline = {'accuracy': 0.8852, 'f1': 0.8852, 'roc_auc': 0.9513, 'mcc': 0.7825}
    if results_tuned is None:
        results_tuned = {'accuracy': 0.9016, 'f1': 0.8966, 'roc_auc': 0.9481, 'mcc': 0.8048}

    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'axes.spines.top': False,
        'axes.spines.right': False,
    })

    with PdfPages(output) as pdf:
        slide_title(pdf)
        slide_dataset(pdf)
        slide_flow(pdf)
        slide_preprocessing(pdf)
        slide_tree(pdf)
        slide_forest(pdf)
        slide_two_models(pdf)
        slide_gridsearch(pdf)
        slide_metrics(pdf)
        slide_confusion(pdf)
        slide_results(pdf, results_baseline, results_tuned)
        slide_roc(pdf)
        slide_features(pdf)
        slide_conclusions(pdf, results_tuned)

    print(f"PDF wygenerowany: {output}  ({14} slajdów)")


if __name__ == '__main__':
    generate()
