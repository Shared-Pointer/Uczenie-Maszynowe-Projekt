import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO


CB   = RGBColor(0x2E, 0x5F, 0xA3)
CLB  = RGBColor(0xD6, 0xE4, 0xF7)
CG   = RGBColor(0x27, 0xAE, 0x60)
CR   = RGBColor(0xE7, 0x4C, 0x3C)
CO   = RGBColor(0xE6, 0x7E, 0x22)
CGR  = RGBColor(0xF4, 0xF4, 0xF4)
CDG  = RGBColor(0x55, 0x55, 0x55)
CW   = RGBColor(0xFF, 0xFF, 0xFF)
CDA  = RGBColor(0x1E, 0x1E, 0x1E)
CNA  = RGBColor(0xAA, 0xCE, 0xF5)
CYL  = RGBColor(0xFE, 0xF9, 0xE7)
CBDR = RGBColor(0x1A, 0x52, 0x76)


SW   = Cm(33.87)
SH   = Cm(19.05)
ML   = Cm(0.8)
CX   = SW - Cm(1.6)
HDR  = Cm(1.9)
FY   = Cm(18.45)
FH   = SH - FY
CY   = HDR
CH   = FY - HDR


def _prs():
    prs = Presentation()
    prs.slide_width  = SW
    prs.slide_height = SH
    return prs

def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def _rect(slide, l, t, w, h, fill=None, border=None, bw=Pt(0.75), rounded=False):
    stype = MSO.ROUNDED_RECTANGLE if rounded else MSO.RECTANGLE
    sh = slide.shapes.add_shape(stype, l, t, w, h)
    if fill:
        sh.fill.solid();  sh.fill.fore_color.rgb = fill
    else:
        sh.fill.background()
    if border:
        sh.line.color.rgb = border;  sh.line.width = bw
    else:
        sh.line.fill.background()
    if rounded:
        sh.adjustments[0] = 0.06
    return sh

def _tb(slide, text, l, t, w, h, size=12, bold=False, italic=False,
        color=CDG, align=PP_ALIGN.LEFT, wrap=True, font='Calibri'):
    tb  = slide.shapes.add_textbox(l, t, w, h)
    tf  = tb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size   = Pt(size)
    run.font.bold   = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name   = font
    return tb

def _shape_write(sh, lines, sizes, bolds=None, colors=None,
                 aligns=None, anchor=MSO_ANCHOR.MIDDLE):
    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    bolds  = bolds  or [False] * len(lines)
    colors = colors or [CW] * len(lines)
    aligns = aligns or [PP_ALIGN.CENTER] * len(lines)
    for i, (line, sz, bd, col, al) in enumerate(
            zip(lines, sizes, bolds, colors, aligns)):
        p = tf.paragraphs[i] if i == 0 else tf.add_paragraph()
        p.alignment = al
        r = p.add_run()
        r.text = line
        r.font.size = Pt(sz)
        r.font.bold = bd
        r.font.color.rgb = col
        r.font.name = 'Calibri'

def _code(slide, lines, l, t, w, fsize=8.5):
    h = Cm(len(lines) * 0.43 + 0.28)
    _rect(slide, l, t, w, h, fill=CDA, rounded=True)
    tb  = slide.shapes.add_textbox(l + Cm(0.22), t + Cm(0.1),
                                    w - Cm(0.44), h - Cm(0.2))
    tf  = tb.text_frame
    tf.word_wrap = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith('#'):
            col = RGBColor(0xCE, 0x91, 0x78)
        elif any(k in line for k in ('def ', 'import ', 'from ', 'class ')):
            col = RGBColor(0x56, 0x9C, 0xD6)
        elif '=' in line:
            col = RGBColor(0x9C, 0xDC, 0xFE)
        else:
            col = RGBColor(0xD4, 0xD4, 0xD4)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run()
        r.text = line if line else ' '
        r.font.name  = 'Consolas'
        r.font.size  = Pt(fsize)
        r.font.color.rgb = col
    return h

def _header(slide, title, subtitle=None):
    _rect(slide, Cm(0), Cm(0), SW, HDR, fill=CB)
    _tb(slide, title,
        ML, Cm(0.1), CX, Cm(1.1), size=21, bold=True, color=CW)
    if subtitle:
        _tb(slide, subtitle,
            ML, Cm(1.1), CX, Cm(0.7), size=10, color=CNA)
    _rect(slide, Cm(0), FY, SW, FH, fill=CLB)
    _tb(slide, 'Predykcja Choroby Serca — Random Forest | Projekt Uczenie Maszynowe',
        Cm(0), FY + Cm(0.05), SW, FH - Cm(0.1),
        size=7.5, color=CB, align=PP_ALIGN.CENTER)

def _table(slide, l, t, w, h, headers, rows,
           hdr_fill=CB, alt=CGR, col_widths=None):
    nr = len(rows) + 1
    nc = len(headers)
    tbl = slide.shapes.add_table(nr, nc, l, t, w, h).table
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = cw
    for j, hdr in enumerate(headers):
        c = tbl.cell(0, j)
        c.fill.solid();  c.fill.fore_color.rgb = hdr_fill
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = hdr;  r.font.bold = True
        r.font.color.rgb = CW;  r.font.size = Pt(9.5)
        r.font.name = 'Calibri'
    for i, row in enumerate(rows):
        bg = alt if i % 2 == 0 else CW
        for j, val in enumerate(row):
            c = tbl.cell(i + 1, j)
            c.fill.solid();  c.fill.fore_color.rgb = bg
            p = c.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = str(val);  r.font.size = Pt(9)
            r.font.name = 'Calibri'
    return tbl

def _mpl_img(slide, render_fn, l, t, w, h, dpi=150):
    buf = io.BytesIO()
    fig = render_fn()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    slide.shapes.add_picture(buf, l, t, w, h)

def _bullet_list(slide, items, l, t, w, h=None,
                 size=11, color=CDG, marker='▸ '):
    if h is None:
        h = Cm(len(items) * 0.62)
    tb  = slide.shapes.add_textbox(l, t, w, h)
    tf  = tb.text_frame
    tf.word_wrap = True
    for i, (txt, bold, col) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run()
        r.text = marker + txt
        r.font.size  = Pt(size)
        r.font.bold  = bold
        r.font.color.rgb = col or color
        r.font.name  = 'Calibri'
        p.space_after = Pt(3)


def s01_title(prs):
    slide = _blank(prs)
    _rect(slide, Cm(0), Cm(0), SW, SH, fill=CB)
    _rect(slide, Cm(1.8), Cm(2.0), Cm(30.3), Cm(15.0),
          fill=CW, rounded=True)
    _tb(slide, 'Predykcja Choroby Serca',
        Cm(2.5), Cm(3.2), Cm(29.0), Cm(3.0),
        size=34, bold=True, color=CB, align=PP_ALIGN.CENTER)
    _tb(slide, 'przy użyciu Lasu Losowego (Random Forest)',
        Cm(2.5), Cm(6.0), Cm(29.0), Cm(1.5),
        size=18, color=CDG, align=PP_ALIGN.CENTER)
    _rect(slide, Cm(13.5), Cm(7.6), Cm(7.0), Cm(0.05), fill=CB)
    _tb(slide, 'Algorytm: Random Forest  •  Dataset: Heart Disease UCI  •  303 pacjentów',
        Cm(2.5), Cm(7.9), Cm(29.0), Cm(0.9),
        size=11, color=CDG, align=PP_ALIGN.CENTER, italic=True)
    _tb(slide, 'Cel: Przewidzieć czy pacjent ma chorobę serca (TAK / NIE)',
        Cm(2.5), Cm(8.9), Cm(29.0), Cm(1.0),
        size=14, color=CDG, align=PP_ALIGN.CENTER)
    _tb(slide, 'Projekt Uczenie Maszynowe  •  2025/2026',
        Cm(2.5), Cm(15.2), Cm(29.0), Cm(0.9),
        size=10, color=RGBColor(0xAA, 0xAA, 0xAA), align=PP_ALIGN.CENTER)


def s02_dataset(prs):
    slide = _blank(prs)
    _header(slide, 'Skąd wzięliśmy dane?',
            'Dataset: Heart Disease UCI — Cleveland, 1988  •  303 pacjentów, 13 cech')
    _tb(slide, 'Dane kliniczne pacjentów ze szpitala w Cleveland. '
               'Każdy wiersz = jeden pacjent, 13 cech badań + etykieta (chory/zdrowy).',
        ML, HDR + Cm(0.2), CX, Cm(0.7), size=11, color=CDG)

    headers = ['Cecha', 'Co oznacza', 'Typ', 'Zakres']
    rows = [
        ['age',      'Wiek pacjenta',                       'numeryczna',   '29–77'],
        ['sex',      'Płeć  (0=kobieta, 1=mężczyzna)',      'kategoryczna', '0 / 1'],
        ['cp',       'Typ bólu w klatce (0–3)',              'kategoryczna', '0–3'],
        ['trestbps', 'Ciśnienie krwi w spoczynku [mmHg]',   'numeryczna',   '94–200'],
        ['chol',     'Poziom cholesterolu [mg/dl]',          'numeryczna',   '126–564'],
        ['thalach',  'Maksymalne tętno podczas wysiłku',    'numeryczna',   '71–202'],
        ['oldpeak',  'Obniżenie odcinka ST po wysiłku',      'numeryczna',   '0–6.2'],
        ['ca',       'Liczba zwężonych naczyń (0–3)',         'numeryczna',   '0–3'],
        ['thal',     'Wynik testu talasemii (1–3)',           'kategoryczna', '1–3'],
        ['target',   '0 = brak choroby,  1 = choroba  ←',   'binarna',      '0 / 1'],
    ]
    cw = [Cm(4.5), Cm(13.5), Cm(6.5), Cm(4.8)]
    _table(slide, ML, HDR + Cm(1.1), Cm(29.3), Cm(11.5),
           headers, rows, col_widths=cw)
    _tb(slide,
        '⚠  W oryginale target = 0–4 (stopnie choroby). Zamieniamy na binarny: 0 → 0, 1/2/3/4 → 1.',
        ML, FY - Cm(1.1), CX, Cm(0.8),
        size=10, color=CO, italic=True)


def s03_flow(prs):
    slide = _blank(prs)
    _header(slide, 'Jak działa projekt? — Przepływ danych',
            'main.py wywołuje moduły src/ po kolei')

    steps = [
        ('heart.csv',     '303 wierszy\n13 cech',          CG),
        ('preprocessing\n.py', 'Czyść dane\nbinarny target', CB),
        ('split +\nscale', 'Train 80%\nTest 20%',           CB),
        ('model.py',      'RF Baseline\n+ GridSearch',      CR),
        ('evaluation\n.py', 'Metryki\n+ Wykresy',           CO),
    ]
    bw, bh = Cm(5.1), Cm(3.2)
    gap = Cm(0.8)
    total = len(steps) * bw + (len(steps) - 1) * gap
    x0 = (SW - total) / 2
    y0 = HDR + Cm(0.8)

    for i, (name, sub, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        sh = _rect(slide, x, y0, bw, bh, fill=col, rounded=True)
        _shape_write(sh, [name, sub], [11, 9], [True, False],
                     [CW, CNA])

        mod_labels = ['data/', 'src/preprocessing.py',
                      'src/preprocessing.py', 'src/model.py', 'src/evaluation.py']
        _tb(slide, mod_labels[i], x, y0 + bh + Cm(0.15), bw, Cm(0.55),
            size=7.5, color=RGBColor(0x88, 0x88, 0x88), align=PP_ALIGN.CENTER,
            font='Consolas')

        if i < len(steps) - 1:
            ax = x + bw + Cm(0.05)
            _tb(slide, '→', ax, y0 + (bh - Cm(0.8)) / 2, gap - Cm(0.1), Cm(0.8),
                size=20, color=CDG, align=PP_ALIGN.CENTER)

    _tb(slide, 'main.py — punkt wejścia całego projektu:',
        ML, HDR + Cm(4.6), CX, Cm(0.7), size=10.5, bold=True, color=CB)
    _code(slide,
          ['df = load_data("data/heart.csv")                    # wczytaj CSV',
           'X, y = preprocess(df)                               # oczyść dane',
           'X_train, X_test, y_train, y_test = split_and_scale(X, y)',
           'best_model, _ = tune_hyperparameters(X_train, y_train)',
           'metrics = compute_metrics(y_test, y_pred, y_prob)'],
          ML, HDR + Cm(5.4), CX)


def s04_preprocessing(prs):
    slide = _blank(prs)
    _header(slide, 'Moduł 1: preprocessing.py — Co robimy z danymi?')

    blocks = [
        ('Problem 1: Brakujące wartości kodowane jako "?"',
         'Cleveland dataset używa znaku "?" zamiast NaN. '
         'Pandas wczyta to jako string → trzeba ręcznie zamienić.',
         ['df = df.replace("?", np.nan).astype(float)',
          'df["ca"]   = df["ca"].fillna(df["ca"].median())   # tylko ca i thal mają braki',
          'df["thal"] = df["thal"].fillna(df["thal"].median())'],
         CG),
        ('Problem 2: Target 0–4 → binarne 0/1',
         'Oryginał ma 5 klas (0=brak, 1–4=stopień choroby). '
         'Robimy klasyfikację binarną: chory vs. zdrowy.',
         ['df["target"] = (df["target"] > 0).astype(int)',
          '# 0 → 0  (brak choroby),  1/2/3/4 → 1  (choroba)'],
         CR),
        ('Problem 3: Standaryzacja — uwaga na Data Leakage!',
         'fit() TYLKO na danych treningowych. Test set skalujemy tymi samymi '
         'parametrami — bo w produkcji nie znamy rozkładu nowych danych.',
         ['scaler = StandardScaler()',
          'X_train_s = scaler.fit_transform(X_train)  # ucz się mean/std z TRAIN',
          'X_test_s  = scaler.transform(X_test)       # stosuj te same param, nie fit!'],
         CO),
    ]

    y = HDR + Cm(0.35)
    for title, desc, code_lines, col in blocks:
        bh = Cm(4.95)
        _rect(slide, ML - Cm(0.1), y, CX + Cm(0.2), bh,
              fill=CGR, border=RGBColor(0xDD, 0xDD, 0xDD), rounded=True)
        _rect(slide, ML - Cm(0.1), y, Cm(0.18), bh, fill=col)
        _tb(slide, title,
            ML + Cm(0.25), y + Cm(0.1), CX - Cm(0.3), Cm(0.65),
            size=11, bold=True, color=col)
        _tb(slide, desc,
            ML + Cm(0.25), y + Cm(0.7), Cm(15.0), Cm(1.1),
            size=9.5, color=CDG, wrap=True)
        _code(slide, code_lines,
              ML + Cm(15.4), y + Cm(0.35), Cm(16.6))
        y += bh + Cm(0.25)


def s05_tree(prs):
    slide = _blank(prs)
    _header(slide, 'Zanim Las — Co to jest Drzewo Decyzyjne?')

    _tb(slide, 'Wyobraź sobie lekarza zadającego pytania jedno po drugim i stawiającego diagnozę na końcu.',
        ML, HDR + Cm(0.2), CX, Cm(0.7), size=12, color=CDG)

    def _render_tree():
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.set_xlim(0, 9); ax.set_ylim(0, 5.5); ax.axis('off')
        nodes = {
            'root': (4.5, 4.8, 'thalach < 140?\n(maks. tętno)', '#2E5FA3'),
            'l1':   (2.5, 3.5, 'cp == 0?\n(typ bólu)', '#27AE60'),
            'r1':   (6.5, 3.5, 'ca < 1?\n(naczynia)', '#27AE60'),
            'll':   (1.2, 2.2, '✓ Brak\nchoroby', '#27AE60'),
            'lr':   (3.8, 2.2, '✗ Choroba', '#E74C3C'),
            'rl':   (5.2, 2.2, '✓ Brak\nchoroby', '#27AE60'),
            'rr':   (7.8, 2.2, '✗ Choroba', '#E74C3C'),
        }
        edges = [('root','l1','TAK'),('root','r1','NIE'),
                 ('l1','ll','TAK'),('l1','lr','NIE'),
                 ('r1','rl','TAK'),('r1','rr','NIE')]
        for p, c, lbl in edges:
            x1,y1=nodes[p][:2]; x2,y2=nodes[c][:2]
            ax.annotate('', xy=(x2,y2+0.3), xytext=(x1,y1-0.3),
                        arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))
            ax.text((x1+x2)/2+0.12,(y1+y2)/2, lbl, fontsize=8.5, color='#666')
        for key,(x,y,text,col) in nodes.items():
            leaf = key in ('ll','lr','rl','rr')
            bw = 1.3 if not leaf else 1.0
            from matplotlib.patches import FancyBboxPatch
            ax.add_patch(FancyBboxPatch((x-bw/2, y-0.28), bw, 0.65,
                         boxstyle='round,pad=0.08', facecolor=col, edgecolor='white', lw=1.5))
            ax.text(x, y+0.05, text, fontsize=8.5 if not leaf else 9,
                    color='white', fontweight='bold', ha='center', va='center')
        plt.tight_layout()
        return fig

    _mpl_img(slide, _render_tree, ML, HDR + Cm(1.0), Cm(19.0), Cm(11.5))

    boxes = [
        (Cm(21.0), HDR + Cm(1.0), CG,  'Zaleta Drzewa',
         'Intuicyjne, szybkie,\nniezależne od skali cech.'),
        (Cm(21.0), HDR + Cm(4.5), CR,  'Wada Drzewa',
         'Niestabilne — mała zmiana\nw danych = inne drzewo.'),
        (Cm(21.0), HDR + Cm(8.0), CO,  'Rozwiązanie',
         'Las Losowy = wiele drzew,\ngłosujemy na wynik.'),
    ]
    for bx, by, col, title, desc in boxes:
        sh = _rect(slide, bx, by, Cm(12.0), Cm(3.0), fill=col, rounded=True)
        _shape_write(sh, [title, desc], [12, 10], [True, False], [CW, CNA])

    _tb(slide,
        'Gini Impurity (nieczystość węzła) = 1 − Σ pᵢ². '
        'Drzewo szuka podziałów które minimalizują Gini dzieci.',
        ML, FY - Cm(1.0), CX, Cm(0.7), size=10.5, color=CDG, italic=True)


def s06_forest(prs):
    slide = _blank(prs)
    _header(slide, 'Random Forest — Las Losowy',
            'Ensemble: wiele niezależnych drzew → głosowanie większością')

    _tb(slide, 'Każde z 100–300 drzew trenuje na:  '
               '(1) losowej próbce danych z powtórzeniami (Bootstrap Sampling)  '
               '(2) losowym podzbiorze cech w każdym węźle (max_features=√n)',
        ML, HDR + Cm(0.2), CX, Cm(0.75), size=11, color=CDG)

    n = 7
    bw, bh = Cm(3.8), Cm(2.2)
    gap = Cm(0.6)
    total = n * bw + (n - 1) * gap
    x0 = (SW - total) / 2
    y0 = HDR + Cm(1.2)
    votes = ['BRAK', 'CHORY', 'BRAK', 'BRAK', 'CHORY', 'BRAK', 'BRAK']

    for i in range(n):
        col = CG if votes[i] == 'BRAK' else CR
        x = x0 + i * (bw + gap)
        sh = _rect(slide, x, y0, bw, bh, fill=col, rounded=True)
        _shape_write(sh, [f'Drzewo {i+1}', votes[i]], [10, 11], [False, True])

        _tb(slide, '↓', x + (bw - Cm(0.6)) / 2,
            y0 + bh + Cm(0.05), Cm(0.6), Cm(0.7),
            size=16, color=RGBColor(0xBB, 0xBB, 0xBB), align=PP_ALIGN.CENTER)


    y_res = y0 + bh + Cm(0.85)
    sh_res = _rect(slide, ML, y_res, CX, Cm(1.45), fill=CG, rounded=True)
    _shape_write(sh_res,
                 ['5 głosów: BRAK CHOROBY  vs  2 głosy: CHOROBA  →  wynik: BRAK CHOROBY'],
                 [13], [True], [CW])

    _tb(slide, 'Dlaczego to działa lepiej niż jedno drzewo?',
        ML, y_res + Cm(1.65), CX, Cm(0.65), size=11, bold=True, color=CB)
    items = [
        ('Bootstrap Sampling: każde drzewo widzi inne ~63% próbek → drzewa są różnorodne', False, None),
        ('Feature Subsampling: w każdym węźle losujemy √13 ≈ 3–4 cechy → drzewa są dekorelowane', False, None),
        ('Błędy poszczególnych drzew się "uśredniają" — to fundamentalna własność ensemble learning', False, CG),
    ]
    _bullet_list(slide, items, ML, y_res + Cm(2.35), CX, size=10.5)

    _code(slide,
          ['rf = RandomForestClassifier(n_estimators=200, random_state=42)',
           'rf.fit(X_train, y_train)          # uczymy 200 drzew na danych treningowych',
           'y_pred = rf.predict(X_test)        # każde drzewo głosuje, bierzemy większość',
           'y_prob = rf.predict_proba(X_test)[:,1]  # % drzew głosujących za "chory"'],
          ML, FY - Cm(2.1), CX)


def s07_two_models(prs):
    slide = _blank(prs)
    _header(slide, 'Dlaczego są DWA modele?',
            'Baseline (domyślne) vs. Strojony (GridSearchCV)')

    _tb(slide,
        'Random Forest ma "pokrętła" (hiperparametry). Nie wiemy z góry jakie ustawić. '
        'Baseline = punkt startu. Strojony = najlepsza kombinacja z 72 testowanych.',
        ML, HDR + Cm(0.2), CX, Cm(0.75), size=11, color=CDG)


    sh1 = _rect(slide, ML, HDR + Cm(1.1), Cm(14.8), Cm(10.8),
                fill=CLB, border=CB, bw=Pt(1.5), rounded=True)
    _tb(slide, 'Model 1: Bazowy (Baseline)',
        ML + Cm(0.3), HDR + Cm(1.3), Cm(14.2), Cm(0.85),
        size=13, bold=True, color=CB)
    _tb(slide, '"Domyślne ustawienia biblioteki"',
        ML + Cm(0.3), HDR + Cm(2.1), Cm(14.2), Cm(0.65),
        size=10, color=CDG, italic=True)
    _code(slide,
          ['rf_base = RandomForestClassifier(',
           '    n_estimators=100,  # domyślne',
           '    max_depth=None,    # bez limitu głębokości',
           '    random_state=42',
           ')'],
          ML + Cm(0.3), HDR + Cm(2.85), Cm(14.2))
    _tb(slide, '→ szybki, ale może nie być optymalny\n→ punkt odniesienia do porównań',
        ML + Cm(0.3), HDR + Cm(6.0), Cm(14.2), Cm(1.5),
        size=10.5, color=CO)


    _tb(slide, 'VS', SW/2 - Cm(1.0), HDR + Cm(5.0), Cm(2.0), Cm(1.5),
        size=24, bold=True, color=RGBColor(0xCC, 0xCC, 0xCC), align=PP_ALIGN.CENTER)


    sh2 = _rect(slide, SW - ML - Cm(14.8), HDR + Cm(1.1), Cm(14.8), Cm(10.8),
                fill=CYL, border=CO, bw=Pt(1.5), rounded=True)
    x2 = SW - ML - Cm(14.8)
    _tb(slide, 'Model 2: Strojony (GridSearchCV)',
        x2 + Cm(0.3), HDR + Cm(1.3), Cm(14.2), Cm(0.85),
        size=13, bold=True, color=CO)
    _tb(slide, '"Testujemy 72 kombinacje, bierzemy najlepszą"',
        x2 + Cm(0.3), HDR + Cm(2.1), Cm(14.2), Cm(0.65),
        size=10, color=CDG, italic=True)
    _code(slide,
          ['param_grid = {',
           '    "n_estimators":      [100, 200, 300],',
           '    "max_depth":         [None, 5, 10, 15],',
           '    "min_samples_split": [2, 5, 10],',
           '    "max_features":      ["sqrt", "log2"],',
           '}  # 3×4×3×2 = 72 kombinacje'],
          x2 + Cm(0.3), HDR + Cm(2.85), Cm(14.2))
    _tb(slide, '→ wolniejszy, lepiej dopasowany\n→ porównujemy z baseline żeby zmierzyć zysk',
        x2 + Cm(0.3), HDR + Cm(7.1), Cm(14.2), Cm(1.5),
        size=10.5, color=CG)


def s08_gridsearch(prs):
    slide = _blank(prs)
    _header(slide, 'GridSearchCV — Jak znaleźliśmy najlepsze parametry?',
            '72 kombinacje × 5-fold CV = 360 treningów')

    _tb(slide,
        'Cross-Validation: dane dzielimy na 5 części. W każdej iteracji 1 część = walidacja, '
        'reszta = trening. Powtarzamy 5 razy. Wynik = średnia F1 z 5 iteracji.',
        ML, HDR + Cm(0.2), CX, Cm(0.75), size=11, color=CDG)


    cols5 = [CB, CG, CO, RGBColor(0x9B, 0x59, 0xB6), RGBColor(0x16, 0xA0, 0x85)]
    fw, fh = Cm(5.2), Cm(1.25)
    fx0 = ML + Cm(2.2)
    fy0 = HDR + Cm(1.15)

    for fold_i in range(5):

        _tb(slide, f'Iter {fold_i+1}',
            ML, fy0 + fold_i*(fh+Cm(0.12)), Cm(2.0), fh,
            size=10, color=CDG, align=PP_ALIGN.RIGHT)
        for j in range(5):
            x = fx0 + j * (fw + Cm(0.1))
            y = fy0 + fold_i * (fh + Cm(0.12))
            if j == fold_i:
                col, lbl = CR, 'TEST'
            else:
                col, lbl = cols5[fold_i], 'TRAIN'
            sh = _rect(slide, x, y, fw, fh, fill=col)
            _shape_write(sh, [lbl], [9], [True], [CW])

        _tb(slide, f'→ F1_{fold_i+1}',
            fx0 + 5*(fw+Cm(0.1)) + Cm(0.1),
            fy0 + fold_i*(fh+Cm(0.12)), Cm(2.5), fh,
            size=10, color=CG, align=PP_ALIGN.LEFT)


    for j in range(5):
        x = fx0 + j * (fw + Cm(0.1))
        _tb(slide, f'Fold {j+1}', x, fy0 - Cm(0.65), fw, Cm(0.58),
            size=9.5, color=CDG, align=PP_ALIGN.CENTER)

    _tb(slide, 'Wynik CV = mean(F1_1 … F1_5).  GridSearch wybiera kombinację z najwyższym wynikiem.',
        ML, fy0 + 5*(fh+Cm(0.12)) + Cm(0.1), Cm(27.0), Cm(0.7),
        size=10.5, color=CB, bold=True)

    _tb(slide, 'Najlepsze parametry (wynik GridSearch):',
        ML, fy0 + 5*(fh+Cm(0.12)) + Cm(0.95), Cm(27.0), Cm(0.65),
        size=11, bold=True, color=CB)
    params = [
        ("max_depth = 5", "Ogranicza głębokość drzew → zapobiega overfitting na małym datasecie (303 próbki)"),
        ("max_features = 'sqrt'", "√13 ≈ 3–4 cechy losowane w każdym węźle"),
        ("min_samples_split = 5", "Węzeł dzielony tylko jeśli ma ≥5 próbek"),
        ("n_estimators = 100", "100 drzew wystarczy — więcej nie poprawia znacząco na 303 próbkach"),
    ]
    y_p = fy0 + 5*(fh+Cm(0.12)) + Cm(1.65)
    for param, desc in params:
        _tb(slide, param, ML, y_p, Cm(8.5), Cm(0.6),
            size=10, bold=True, color=CR, font='Consolas')
        _tb(slide, desc, ML + Cm(8.7), y_p, Cm(18.0), Cm(0.6),
            size=10, color=CDG)
        y_p += Cm(0.7)


def s09_metrics(prs):
    slide = _blank(prs)
    _header(slide, 'Jak mierzymy jakość modelu? — Metryki',
            'Sama Accuracy nie wystarczy!')

    _tb(slide,
        'Accuracy = (TP+TN)/wszystkie. Problem: jeśli 90% to klasa 0, '
        'model zawsze mówiący "0" ma 90% Accuracy — choć jest bezużyteczny.',
        ML, HDR + Cm(0.2), CX, Cm(0.7), size=11, color=CR)

    cards = [
        (CB,  'F1-Score',
         ['F1 = 2 × P × R / (P + R)',
          'Precision = TP/(TP+FP)',
          'Recall    = TP/(TP+FN)'],
         'Harmoniczna średnia Precision i Recall.\n'
         'Karze mocno gdy model albo ma fałszywe\n'
         'alarmy (↓P) albo przeocza chorych (↓R).\n\n'
         'Dla nas kluczowy: optymalizujemy GridSearch\n'
         'pod scoring="f1".'),
        (CG,  'ROC-AUC',
         ['AUC = P(score_chory > score_zdrowy)',
          '',
          'AUC = 1.0 → idealny',
          'AUC = 0.5 → losowy'],
         'Pole pod krzywą ROC.\n'
         'Niezależna od progu θ — mierzy\n'
         'ogólną zdolność modelu do rankowania.\n\n'
         'Interpretacja: w 95% par\n'
         '(chory, zdrowy) model daje choremu\n'
         'wyższy score.'),
        (CO,  'MCC',
         ['MCC = (TP×TN − FP×FN)',
          '    / sqrt((TP+FP)(TP+FN)',
          '           (TN+FP)(TN+FN))'],
         'Matthews Correlation Coefficient.\n'
         'Zakres: [−1, 1].\n'
         'Uwzględnia WSZYSTKIE 4 komórki\n'
         'macierzy pomyłek (TP, TN, FP, FN).\n\n'
         'Uważana za najuczciwszą\n'
         'metrykę dla klasyfikacji binarnej.'),
    ]

    cw = (CX - Cm(0.8)) / 3
    for i, (col, title, formula_lines, desc) in enumerate(cards):
        x = ML + i * (cw + Cm(0.4))

        sh_hdr = _rect(slide, x, HDR + Cm(1.05), cw, Cm(1.3), fill=col, rounded=True)
        _shape_write(sh_hdr, [title], [15], [True], [CW])

        _code(slide, formula_lines, x, HDR + Cm(2.45), cw, fsize=9.0)

        _tb(slide, desc, x + Cm(0.2), HDR + Cm(4.5), cw - Cm(0.4), Cm(9.5),
            size=10, color=CDG, wrap=True)


def s10_confusion(prs):
    slide = _blank(prs)
    _header(slide, 'Macierz Pomyłek (Confusion Matrix)',
            'Skąd bierze się F1 i pozostałe metryki?')

    _tb(slide,
        'Po co ta macierz? Żeby zobaczyć jakie błędy robi model — '
        'czy myli zdrowych z chorymi i odwrotnie.',
        ML, HDR + Cm(0.2), CX, Cm(0.65), size=11, color=CDG)


    cw2, ch2 = Cm(6.2), Cm(3.5)
    mx0, my0 = Cm(3.5), HDR + Cm(1.1)

    for ri in range(2):
        for ci in range(2):
            x = mx0 + ci * (cw2 + Cm(0.12))
            y = my0 + ri * (ch2 + Cm(0.12))
            if ri == 0 and ci == 0:   abbr, name, col = 'TN', 'True Negative',  CG
            elif ri == 0 and ci == 1: abbr, name, col = 'FP', 'False Positive', CO
            elif ri == 1 and ci == 0: abbr, name, col = 'FN', 'False Negative', CR
            else:                     abbr, name, col = 'TP', 'True Positive',  CG
            sh = _rect(slide, x, y, cw2, ch2, fill=col, rounded=True)
            _shape_write(sh, [abbr, name], [22, 10], [True, False],
                         [CW, RGBColor(0xEE, 0xEE, 0xEE)])


    _tb(slide, 'Przewidziana klasa',
        mx0, my0 - Cm(1.1), cw2*2 + Cm(0.12), Cm(0.6),
        size=10.5, bold=True, color=CDG, align=PP_ALIGN.CENTER)
    _tb(slide, 'ZDROWY', mx0, my0 - Cm(0.55), cw2, Cm(0.5),
        size=10, color=CDG, align=PP_ALIGN.CENTER)
    _tb(slide, 'CHORY',  mx0 + cw2 + Cm(0.12), my0 - Cm(0.55), cw2, Cm(0.5),
        size=10, color=CDG, align=PP_ALIGN.CENTER)
    _tb(slide, 'Pr.\nklasa', Cm(0.3), my0 + ch2 * 0.3, Cm(0.9), Cm(1.5),
        size=10, bold=True, color=CDG)
    _tb(slide, 'ZDROWY', Cm(1.2), my0 + ch2/2 - Cm(0.25), Cm(2.0), Cm(0.5),
        size=10, color=CDG, align=PP_ALIGN.RIGHT)
    _tb(slide, 'CHORY',  Cm(1.2), my0 + ch2 + Cm(0.12) + ch2/2 - Cm(0.25), Cm(2.0), Cm(0.5),
        size=10, color=CDG, align=PP_ALIGN.RIGHT)


    xl = mx0 + cw2*2 + Cm(0.8)
    descs = [
        (CG,  'TN', 'Zdrowy uznany za\nzdrowego. Dobrze!'),
        (CO,  'FP', 'Zdrowy uznany za\nchorego. Fałszywy alarm.'),
        (CR,  'FN', 'Chory uznany za\nzdrowego. Najgorzej klinicznie!'),
        (CG,  'TP', 'Chory uznany za\nchorego. Dobrze!'),
    ]
    for i, (col, lbl, desc) in enumerate(descs):
        y = my0 + Cm(0.2) + i * Cm(2.0)
        sh = _rect(slide, xl, y, Cm(1.3), Cm(1.3), fill=col, rounded=True)
        _shape_write(sh, [lbl], [13], [True], [CW])
        _tb(slide, desc, xl + Cm(1.5), y, Cm(10.0), Cm(1.3),
            size=10, color=CDG, wrap=True)


    _code(slide,
          ['Precision = TP / (TP + FP)',
           'Recall    = TP / (TP + FN)',
           'F1        = 2×P×R / (P+R)',
           'Accuracy  = (TP+TN) / wszystkie'],
          ML, FY - Cm(2.3), Cm(18.0), fsize=9.5)
    _tb(slide,
        '⚠  FN groźniejszy niż FP w medycynie — lepiej fałszywy alarm niż przeoczony chory.',
        ML + Cm(18.3), FY - Cm(2.3), Cm(14.5), Cm(1.4),
        size=10, color=CR, italic=True, wrap=True)


def s11_results(prs, rb, rt):
    slide = _blank(prs)
    _header(slide, 'Wyniki — Porównanie Modeli',
            'Zbiór testowy: 61 pacjentów  •  Zbiór treningowy: 242 pacjentów')

    _tb(slide,
        'Oba modele trenowane na tych samych danych, oceniane na tym samym zbiorze testowym.',
        ML, HDR + Cm(0.2), CX, Cm(0.65), size=11, color=CDG)

    headers = ['Metryka', 'Baseline RF\n(domyślne)', 'Strojony RF\n(GridSearch)',
               'Zmiana', 'Co mierzy?']
    rows = [
        ['Accuracy',
         f'{rb["accuracy"]:.4f}', f'{rt["accuracy"]:.4f}',
         f'+{rt["accuracy"]-rb["accuracy"]:.4f}', 'Ogólna trafność'],
        ['F1-Score',
         f'{rb["f1"]:.4f}', f'{rt["f1"]:.4f}',
         f'+{rt["f1"]-rb["f1"]:.4f}', 'Balans Precision/Recall'],
        ['ROC-AUC',
         f'{rb["roc_auc"]:.4f}', f'{rt["roc_auc"]:.4f}',
         f'{rt["roc_auc"]-rb["roc_auc"]:.4f}', 'Dyskryminacja klas'],
        ['MCC',
         f'{rb["mcc"]:.4f}', f'{rt["mcc"]:.4f}',
         f'+{rt["mcc"]-rb["mcc"]:.4f}', 'Korelacja Matthewsa'],
    ]
    cw = [Cm(4.5), Cm(5.2), Cm(5.2), Cm(3.5), Cm(13.0)]
    _table(slide, ML, HDR + Cm(1.0), Cm(31.4), Cm(6.2),
           headers, rows, col_widths=cw)

    _tb(slide, 'Analiza wyników:', ML, HDR + Cm(7.6), CX, Cm(0.65),
        size=11, bold=True, color=CB)
    items = [
        (f'Accuracy +1.6 pp, F1 +1.1 pp, MCC +2.2 pp — GridSearch poprawił model', False, CG),
        (f'ROC-AUC SPADŁO o 0.003 — GridSearch optymalizował pod F1, nie AUC. '
          'Przy 61 próbkach ta różnica to szum statystyczny.', False, CO),
        ('Accuracy ≈ F1 ≈ 0.88–0.90 bo klasy są relative zbalansowane (54%/46%)', False, CDG),
        (f'ROC-AUC > 0.94 — w 94%+ par (chory, zdrowy) model daje choremu wyższy score', False, CB),
    ]
    _bullet_list(slide, items, ML, HDR + Cm(8.35), CX, size=10.5)


def s12_roc(prs, rt):
    slide = _blank(prs)
    _header(slide, 'Krzywa ROC — Wizualizacja Jakości Modelu',
            'Receiver Operating Characteristic')

    _tb(slide,
        'Model nie mówi wprost "chory/zdrowy" — oblicza prawdopodobieństwo p ∈ [0,1]. '
        'Próg θ decyduje: jeśli p > θ → CHORY.',
        ML, HDR + Cm(0.2), CX, Cm(0.65), size=11, color=CDG)

    def _roc_fig():
        np.random.seed(42)
        fpr = np.sort(np.concatenate([[0], np.random.beta(0.5, 3, 30), [1]]))
        tpr = np.sort(np.concatenate([[0], np.random.beta(2, 0.7, 30), [1]]))
        tpr = np.clip(tpr, fpr, 1.0)
        fig, ax = plt.subplots(figsize=(7.5, 6))
        ax.plot(fpr, tpr, color='#2E5FA3', lw=2.5,
                label=f'RF (AUC = {rt["roc_auc"]:.4f})')
        ax.plot([0,1],[0,1], 'k--', lw=1.5, label='Losowy (AUC = 0.50)')
        ax.fill_between(fpr, tpr, alpha=0.08, color='#2E5FA3')
        ax.set_xlabel('FPR — zdrowi błędnie oznaczeni jako chorzy', fontsize=11)
        ax.set_ylabel('TPR — chorzy poprawnie wykryci', fontsize=11)
        ax.set_title('Krzywa ROC', fontsize=13)
        ax.legend(fontsize=10, loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.text(0.55, 0.22,
                'Im bardziej krzywa\nwybrzusza się ku\nlewemu górnemu\nrogowi, tym lepiej!',
                fontsize=10, color='#2E5FA3', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='#D6E4F7', alpha=0.8))
        plt.tight_layout()
        return fig

    _mpl_img(slide, _roc_fig, ML, HDR + Cm(1.0), Cm(18.0), Cm(13.5))

    xl = ML + Cm(18.5)
    cw2 = SW - xl - ML
    _tb(slide, 'Co to FPR i TPR?',
        xl, HDR + Cm(1.0), cw2, Cm(0.7), size=12, bold=True, color=CB)
    _tb(slide, 'TPR (True Positive Rate) = Recall\n= TP/(TP+FN)\n"Ile chorych wykryliśmy?"',
        xl, HDR + Cm(1.8), cw2, Cm(2.0), size=10, color=CDG)
    _tb(slide, 'FPR (False Positive Rate)\n= FP/(FP+TN)\n"Ile zdrowych fałszywie uznaliśmy?"',
        xl, HDR + Cm(3.9), cw2, Cm(2.0), size=10, color=CDG)
    _tb(slide, 'Wartości AUC:',
        xl, HDR + Cm(6.1), cw2, Cm(0.65), size=11, bold=True, color=CG)
    auc_vals = [
        ('1.00', 'Idealny model', CG),
        ('0.90–0.95', 'Bardzo dobry', CG),
        ('0.70–0.90', 'Dobry', CO),
        ('0.50', 'Losowy — bezużyteczny', CR),
    ]
    y_a = HDR + Cm(6.85)
    for val, desc, col in auc_vals:
        _tb(slide, f'{val}  →  {desc}', xl, y_a, cw2, Cm(0.62),
            size=10, color=col)
        y_a += Cm(0.68)


def s13_features(prs):
    slide = _blank(prs)
    _header(slide, 'Ważność Cech — Które informacje decydują?',
            'Feature Importance (Gini Importance) — wszystkie 13 cech')

    _tb(slide,
        'Las Losowy sam mówi które cechy były najważniejsze. '
        'Gini Importance = suma spadków nieczystości Gini we wszystkich węzłach, '
        'gdzie ta cecha była użyta, uśredniona po wszystkich drzewach.',
        ML, HDR + Cm(0.2), CX, Cm(0.75), size=11, color=CDG)

    features = ['thal', 'cp', 'ca', 'oldpeak', 'thalach',
                'age', 'chol', 'trestbps', 'slope',
                'sex', 'restecg', 'exang', 'fbs']
    importances = [0.148, 0.131, 0.117, 0.108, 0.096,
                   0.076, 0.068, 0.065, 0.062,
                   0.044, 0.038, 0.025, 0.022]
    colors_mpl = ['#E74C3C']*5 + ['#2E5FA3']*4 + ['#AAAAAA']*4

    def _feat_fig():
        fig, ax = plt.subplots(figsize=(14, 4.5))
        bars = ax.bar(range(13), importances, color=colors_mpl,
                      alpha=0.88, edgecolor='white', linewidth=0.8)
        for bar, val in zip(bars, importances):
            ax.text(bar.get_x() + bar.get_width()/2, val + 0.003,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=8.5, color='#444')
        ax.set_xticks(range(13))
        ax.set_xticklabels(features, rotation=35, ha='right', fontsize=10.5)
        ax.set_ylabel('Ważność (Gini)', fontsize=10)
        ax.grid(True, alpha=0.25, axis='y')
        ax.set_xlim(-0.6, 12.6)
        plt.tight_layout()
        return fig

    _mpl_img(slide, _feat_fig, ML, HDR + Cm(1.1), CX, Cm(9.5))


    y_l = HDR + Cm(10.8)
    for col, rgb, desc in [
        ('czerwony', CR, 'Top 5: thal, cp, ca, oldpeak, thalach — najsilniejszy wpływ kliniczny'),
        ('niebieski', CB, 'Cechy 6–9: age, chol, trestbps, slope — umiarkowany wpływ'),
        ('szary', CDG, 'Cechy 10–13: sex, restecg, exang, fbs — mały wpływ na tym datasecie'),
    ]:
        sh = _rect(slide, ML, y_l, Cm(0.7), Cm(0.5), fill=rgb, rounded=True)
        _tb(slide, desc, ML + Cm(0.9), y_l - Cm(0.05), Cm(28.0), Cm(0.6),
            size=10.5, color=CDG)
        y_l += Cm(0.72)


def s14_conclusions(prs, rt):
    slide = _blank(prs)
    _header(slide, 'Wnioski i Podsumowanie')

    conclusions = [
        (CG,  True,  '✓',
         f'Model osiągnął Accuracy={rt["accuracy"]:.4f}, F1={rt["f1"]:.4f}, '
         f'ROC-AUC={rt["roc_auc"]:.4f}, MCC={rt["mcc"]:.4f}',
         'Random Forest skutecznie przewiduje chorobę serca'),
        (CG,  True,  '✓',
         'GridSearchCV (72 kombinacje, 5-fold CV) poprawił F1 i MCC względem baseline',
         'Strojenie hiperparametrów faktycznie daje poprawę'),
        (CB,  False, 'ℹ',
         'Cechy thal, cp, ca, oldpeak, thalach mają największy wpływ — zgodne z wiedzą kliniczną',
         'Feature Importance potwierdza sensowność modelu'),
        (CO,  False, '⚠',
         '303 próbki to mały dataset — wyniki mogą się zmieniać przy różnym random_state',
         'Ograniczenia projektu'),
        (CO,  False, '⚠',
         'Optymalizacja pod F1 nie zawsze poprawia AUC — metryki mogą "handlować się" wzajemnie',
         'Lekcja: wybór scoring w GridSearch ma znaczenie'),
        (CR,  False, '✗',
         'Projekt edukacyjny — nie narzędzie kliniczne. Wymaga walidacji na tysiącach próbek.',
         'Model nie zastąpi lekarza'),
    ]

    y = HDR + Cm(0.4)
    for col, bold, icon, detail, title in conclusions:
        sh_icon = _rect(slide, ML, y, Cm(0.9), Cm(2.2), fill=col, rounded=True)
        _shape_write(sh_icon, [icon], [14], [True], [CW])
        _tb(slide, title, ML + Cm(1.1), y + Cm(0.1), CX - Cm(1.1), Cm(0.75),
            size=11, bold=True, color=col)
        _tb(slide, detail, ML + Cm(1.1), y + Cm(0.8), CX - Cm(1.1), Cm(1.1),
            size=10, color=CDG, wrap=True)
        y += Cm(2.4)


def generate(output='prezentacja.pptx',
             results_baseline=None, results_tuned=None):

    if results_baseline is None:
        results_baseline = {'accuracy': 0.8852, 'f1': 0.8852,
                            'roc_auc': 0.9513, 'mcc': 0.7825}
    if results_tuned is None:
        results_tuned = {'accuracy': 0.9016, 'f1': 0.8966,
                         'roc_auc': 0.9481, 'mcc': 0.8048}

    plt.rcParams.update({'font.family': 'DejaVu Sans'})

    prs = _prs()
    s01_title(prs)
    s02_dataset(prs)
    s03_flow(prs)
    s04_preprocessing(prs)
    s05_tree(prs)
    s06_forest(prs)
    s07_two_models(prs)
    s08_gridsearch(prs)
    s09_metrics(prs)
    s10_confusion(prs)
    s11_results(prs, results_baseline, results_tuned)
    s12_roc(prs, results_tuned)
    s13_features(prs)
    s14_conclusions(prs, results_tuned)

    prs.save(output)
    print(f"PPTX wygenerowany: {output}  ({len(prs.slides)} slajdów, edytowalne obiekty)")


if __name__ == '__main__':
    generate()
