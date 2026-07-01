import textwrap
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages


PW, PH = 8.27, 11.69
MARGIN_L = 0.65
MARGIN_R = 0.65
TEXT_W = PW - MARGIN_L - MARGIN_R
LINE_H = 0.215
FONT_BODY = 10.0
FONT_CODE = 9.0

BLUE   = '#2E5FA3'
LBLUE  = '#D6E4F7'
GREEN  = '#1E8449'
RED    = '#C0392B'
ORANGE = '#D35400'
GRAY   = '#F4F4F4'
DGRAY  = '#444444'


class Doc:

    def __init__(self, pdf):
        self.pdf = pdf
        self.page_num = 0
        self._new_page()

    def _new_page(self):
        if hasattr(self, 'fig'):
            self._close_page()
        self.page_num += 1
        self.fig = plt.figure(figsize=(PW, PH))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, PW)
        self.ax.set_ylim(0, PH)
        self.ax.axis('off')

        self.ax.add_patch(plt.Rectangle((0, PH - 0.45), PW, 0.45, color=BLUE, zorder=1))
        self.ax.text(MARGIN_L, PH - 0.22,
                     'Random Forest — Skrypt Prezentacji | Projekt Uczenie Maszynowe',
                     fontsize=8, color='white', va='center', zorder=2)
        self.ax.text(PW - MARGIN_R, PH - 0.22, f'str. {self.page_num}',
                     fontsize=8, color='white', va='center', ha='right', zorder=2)

        self.ax.add_patch(plt.Rectangle((0, 0), PW, 0.28, color=LBLUE, zorder=1))
        self.y = PH - 0.62

    def _close_page(self):
        self.pdf.savefig(self.fig, bbox_inches='tight')
        plt.close(self.fig)

    def finish(self):
        self._close_page()

    def _space(self, needed):
        if self.y - needed < 0.38:
            self._new_page()


    def chapter(self, num, title):
        self._space(0.95)
        y = self.y
        self.ax.add_patch(plt.Rectangle(
            (0, y - 0.62), PW, 0.72, color=BLUE, alpha=0.12, zorder=0))
        self.ax.add_patch(plt.Rectangle(
            (0, y - 0.62), 0.18, 0.72, color=BLUE, zorder=1))
        self.ax.text(0.35, y - 0.17,
                     f'Slajd {num}: {title}',
                     fontsize=13, fontweight='bold', color=BLUE,
                     va='center', zorder=2)
        self.y -= 0.85
        self.vspace(0.05)

    def h2(self, text, color=ORANGE):
        self._space(0.48)
        self.ax.text(MARGIN_L, self.y, text,
                     fontsize=10.5, fontweight='bold', color=color,
                     va='top')
        self.y -= 0.38

    def p(self, text, indent=0, color=DGRAY, fontsize=FONT_BODY, bold=False):
        avail_chars = int((TEXT_W - indent * 0.18) / 0.092)
        avail_chars = max(avail_chars, 50)
        lines = textwrap.wrap(text, width=avail_chars) if text.strip() else ['']
        fw = 'bold' if bold else 'normal'
        for line in lines:
            self._space(LINE_H)
            self.ax.text(MARGIN_L + indent * 0.18, self.y,
                         line, fontsize=fontsize, color=color,
                         va='top', fontweight=fw)
            self.y -= LINE_H
        self.y -= 0.04

    def bullet(self, text, depth=0, color=DGRAY):
        prefix = '  ' * depth + ('▸ ' if depth == 0 else '– ')
        self.p(prefix + text, indent=depth, color=color)

    def code(self, lines):
        h = len(lines) * 0.195 + 0.12
        self._space(h + 0.1)
        self.ax.add_patch(mpatches.FancyBboxPatch(
            (MARGIN_L - 0.1, self.y - h), TEXT_W + 0.2, h,
            boxstyle='round,pad=0.04',
            facecolor='#1E1E1E', edgecolor='#555', linewidth=0.8, zorder=3))
        for i, line in enumerate(lines):
            col = '#CE9178' if line.lstrip().startswith('#') else \
                  '#569CD6' if any(kw in line for kw in ('def ', 'import ', 'from ', 'class ')) else \
                  '#9CDCFE' if '=' in line else '#D4D4D4'
            self.ax.text(MARGIN_L, self.y - 0.1 - i * 0.195,
                         line, fontsize=FONT_CODE, color=col,
                         va='top', fontfamily='monospace', zorder=4)
        self.y -= h + 0.16

    def qa(self, question, answer):
        self._space(0.42)
        self.ax.add_patch(plt.Rectangle(
            (MARGIN_L - 0.05, self.y - 0.32), TEXT_W + 0.1, 0.34,
            color=LBLUE, zorder=0))
        self.ax.text(MARGIN_L, self.y - 0.03,
                     f'Q:  {question}',
                     fontsize=10, fontweight='bold', color=BLUE,
                     va='top', zorder=1)
        self.y -= 0.40
        self.p(f'→  {answer}', indent=1, color='#1A5276')

    def divider(self):
        self._space(0.22)
        self.ax.plot([MARGIN_L, PW - MARGIN_R], [self.y, self.y],
                     color='#CCC', lw=0.7)
        self.y -= 0.22

    def vspace(self, h=0.15):
        self.y -= h


def build(doc):


    doc.chapter(1, 'Tytuł — Cel projektu')

    doc.h2('O czym jest ten projekt?')
    doc.p('Celem projektu jest zbudowanie modelu uczenia maszynowego, który na podstawie '
          'wyników badań klinicznych pacjenta przewiduje, czy ma on chorobę serca. '
          'Jest to klasyfikacja binarna: wynik to 0 (brak choroby) lub 1 (choroba).')
    doc.p('Użyty algorytm to Random Forest (Las Losowy) — metoda oparta na wielu drzewach '
          'decyzyjnych, która jest odporna na overfitting i dobrze radzi sobie z danymi '
          'klinicznymi.')

    doc.h2('Dlaczego Random Forest, a nie np. regresja logistyczna?')
    doc.bullet('RF automatycznie wykrywa nieliniowe zależności między cechami')
    doc.bullet('Nie wymaga ręcznego feature engineeringu')
    doc.bullet('Generuje Feature Importance — wiemy, które cechy "decydują"')
    doc.bullet('Odporny na outliery i braki w danych (po imputacji)')
    doc.bullet('W praktyce klinicznej często osiąga lepsze wyniki niż proste modele')

    doc.h2('Dataset: Heart Disease UCI — Cleveland, 1988')
    doc.p('Dane pochodzą z badań przeprowadzonych w Cleveland Clinic Foundation '
          'w 1988 roku. Jest to jeden z najbardziej popularnych zbiorów do klasyfikacji '
          'medycznej w historii uczenia maszynowego.')
    doc.bullet('303 pacjentów')
    doc.bullet('13 cech wejściowych (wyniki badań)')
    doc.bullet('1 zmienna docelowa: target (0 = brak, 1–4 = choroba)')
    doc.bullet('Klasy względnie zbalansowane: 164 zdrowych (54%), 139 chorych (46%)')

    doc.qa('Dlaczego tak mały dataset?',
           'Heart Disease UCI to klasyczny benchmark edukacyjny — liczy 303 próbki. '
           'W rzeczywistych zastosowaniach klinicznych mamy tysiące lub miliony rekordów. '
           'Na tym datasecie uczymy się metodologii, nie budujemy narzędzia klinicznego.')

    doc.divider()


    doc.chapter(2, 'Dataset — Co oznaczają cechy?')

    doc.h2('Opis wszystkich 13 cech wejściowych')
    features_desc = [
        ('age',      'Wiek pacjenta (lata)',
                     'Im starszy, tym większe ryzyko — ale nie jest najważniejszą cechą.'),
        ('sex',      'Płeć: 0 = kobieta, 1 = mężczyzna',
                     'Mężczyźni mają statystycznie wyższe ryzyko choroby serca w młodym wieku.'),
        ('cp',       'Typ bólu w klatce piersiowej (0–3)',
                     '0=typowy ból wieńcowy, 1=atypowy, 2=nieanginalny, 3=bezobjawowy. '
                     'Paradoks: pacjenci z cp=0 mają wyższe ryzyko mimo "niespecyficznego" bólu.'),
        ('trestbps', 'Ciśnienie krwi w spoczynku [mmHg]',
                     'Norma: 120/80. Podwyższone ciśnienie zwiększa ryzyko.'),
        ('chol',     'Poziom cholesterolu [mg/dl]',
                     'Norma: <200. Wartości 200–239 to "granica", >240 to podwyższone ryzyko.'),
        ('fbs',      'Czy cukier na czczo > 120 mg/dl (0/1)',
                     'Związek z cukrzycą, która jest czynnikiem ryzyka chorób sercowo-naczyniowych.'),
        ('restecg',  'Wynik EKG w spoczynku (0–2)',
                     '0=normalny, 1=anomalie ST-T, 2=przerost lewej komory (LVH).'),
        ('thalach',  'Maksymalne tętno podczas wysiłku',
                     'WAŻNA CECHA: niskie maksymalne tętno może wskazywać na słabą wydolność serca.'),
        ('exang',    'Dławica piersiowa wywołana wysiłkiem (0/1)',
                     'Ból w klatce podczas wysiłku — silny predyktor choroby serca.'),
        ('oldpeak',  'Obniżenie odcinka ST po wysiłku',
                     'ST depression = marker niedokrwienia mięśnia sercowego. Im wyższe, tym gorzej.'),
        ('slope',    'Kształt odcinka ST (0–2)',
                     '0=rosnący, 1=płaski, 2=malejący. Płaski i malejący sugerują niedokrwienie.'),
        ('ca',       'Liczba naczyń wieńcowych zwężonych (0–3)',
                     'Widocznych przy fluoroskopii. Więcej zwężeń = poważniejsza choroba.'),
        ('thal',     'Wynik testu talasemii (1–3)',
                     '1=normalny, 2=utrwalony defekt, 3=odwracalny defekt. NAJWAŻNIEJSZA cecha!'),
    ]
    for feat, short, detail in features_desc:
        doc.p(f'  {feat:<12} {short}', fontsize=9.5, bold=False)
        doc.p(f'               {detail}', fontsize=9.0, color='#666')

    doc.vspace(0.1)
    doc.h2('Zmienna docelowa (target)')
    doc.p('W oryginalnym datasecie target = 0 (brak choroby), 1, 2, 3, 4 (różne stopnie '
          'zaawansowania choroby serca). Ponieważ robimy klasyfikację binarną, '
          'zamieniamy wartości 1–4 na 1, czyli "chory".')
    doc.code(['df["target"] = (df["target"] > 0).astype(int)',
              '# 0 pozostaje 0, 1/2/3/4 stają się 1'])

    doc.qa('Dlaczego nie robimy klasyfikacji wieloklasowej (0–4)?',
           'Projekt skupia się na zagadnieniu binarnym: chory vs. zdrowy. '
           'Klasyfikacja wieloklasowa wymagałaby innej metodologii, więcej danych na klasę, '
           'i innej interpretacji metryk. Binaryzacja upraszcza problem i jest standardem '
           'dla tego datasetu w literaturze.')

    doc.divider()


    doc.chapter(3, 'Przepływ danych — Jak działa main.py?')

    doc.h2('Architektura projektu')
    doc.p('Projekt jest podzielony na moduły w katalogu src/. main.py to punkt wejścia '
          'który wywołuje poszczególne moduły po kolei. Taka struktura to standard '
          'w projektach ML — każdy moduł ma jedną odpowiedzialność (separation of concerns).')

    doc.code(['heart.csv',
              '   ↓  load_data()          # src/preprocessing.py',
              '   ↓  preprocess()         # czyści dane, binaryzuje target',
              '   ↓  split_and_scale()    # podział 80/20 + standaryzacja',
              '   ↓  tune_hyperparameters()  # src/model.py — GridSearchCV',
              '   ↓  compute_metrics()    # src/evaluation.py',
              '   ↓  plot_*()             # wykresy do plots/'])

    doc.h2('Dlaczego moduły, nie jeden plik?')
    doc.bullet('preprocessing.py — wczytywanie i czyszczenie danych')
    doc.bullet('model.py — trening, GridSearch, cross-validation')
    doc.bullet('evaluation.py — metryki i wizualizacje')
    doc.bullet('main.py — orchestracja (wywołuje pozostałe)')
    doc.p('Dzięki temu każdy moduł można testować osobno, kod jest czytelny '
          'i łatwy do rozbudowy.')

    doc.qa('Dlaczego main.py importuje z src/ a nie bezpośrednio z plików?',
           'src/ to pakiet Python (jest tam plik __init__.py). Dzięki temu można pisać '
           '"from src.model import ..." co jest bardziej czytelne i zgodne z konwencjami. '
           'Alternatywnie można by mieć pliki bezpośrednio w katalogu głównym, '
           'ale to byłoby mniej porządnie przy większych projektach.')

    doc.divider()


    doc.chapter(4, 'Preprocessing — Przygotowanie danych')

    doc.h2('Problem 1: Brakujące wartości kodowane jako "?"')
    doc.p('Dataset Cleveland nie używa standardowego NaN/null — brakujące wartości '
          'są zapisane jako znak zapytania "?". Pandas wczyta to jako string, '
          'więc trzeba najpierw zamieniać "?" → NaN.')
    doc.code(['df = df.replace("?", np.nan).astype(float)',
              'df["ca"]   = df["ca"].fillna(df["ca"].median())',
              'df["thal"] = df["thal"].fillna(df["thal"].median())'])
    doc.p('Tylko cechy ca i thal mają braki (4–6 wierszy na ~303). '
          'Uzupełniamy medianą, nie średnią.')

    doc.qa('Dlaczego mediana, a nie średnia?',
           'Mediana jest odporna na wartości skrajne (outliers). Cholesterol ma np. '
           'wartości od 126 do 564 mg/dl — średnia ciągnie się w stronę ekstremalnych wartości. '
           'Mediana po prostu bierze wartość środkową, więc jest bardziej "bezpieczna" '
           'do imputacji w danych medycznych.')

    doc.h2('Problem 2: Standaryzacja — WAŻNE: Data Leakage!')
    doc.p('Cechy mają bardzo różne skale: age to 29–77, chol to 126–564, oldpeak to 0–6.2. '
          'Standaryzacja (mean=0, std=1) sprawia że wszystkie cechy są na równej stopce.')
    doc.code(['scaler = StandardScaler()',
              '# TYLKO fit na danych treningowych!',
              'X_train_s = scaler.fit_transform(X_train)',
              '# test skalujemy PARAMETRAMI z train (nie fit!)',
              'X_test_s  = scaler.transform(X_test)'])

    doc.qa('Dlaczego nie robimy scaler.fit_transform() na całym datasecie?',
           'To byłby Data Leakage (przeciek danych). Zbiór testowy udaje "dane z przyszłości" '
           'które model nigdy nie widział. Gdybyśmy fitowali scaler na całym datasecie, '
           'informacja o rozkładzie wartości testowych "przeciekłaby" do procesu uczenia. '
           'W prawdziwej produkcji nowe dane przychodzą jeden po jednym — musimy skalować '
           'je parametrami uczonymi tylko na danych historycznych.')

    doc.qa('Czy Random Forest w ogóle wymaga standaryzacji?',
           'Random Forest jest oparty na drzewach decyzyjnych, które dzielą dane według '
           'progów — nie obliczają odległości euklidesowych. Technicznie RF NIE wymaga '
           'standaryzacji. My i tak ją robimy dla spójności (gdybyśmy porównywali z '
           'innymi algorytmami jak SVM czy KNN, które jej wymagają). To nie pogarsza RF.')

    doc.divider()


    doc.chapter(5, 'Drzewo Decyzyjne — Budulec Lasu Losowego')

    doc.h2('Jak drzewo decyzyjne się uczy?')
    doc.p('Drzewo decyzyjne to model, który zadaje serię pytań "tak/nie" o cechy danych, '
          'żeby dotrzeć do ostatecznej decyzji (klasy). Uczenie polega na znalezieniu '
          'optymalnych pytań (podziałów) na każdym poziomie drzewa.')
    doc.p('Przykład: "czy thalach < 140?" → jeśli TAK, idź w lewo; jeśli NIE, idź w prawo.')

    doc.h2('Gini Impurity — jak mierzymy "czystość" węzła?')
    doc.p('Gini impurity mierzy jak "zmieszane" są klasy w danym węźle:')
    doc.code(['Gini(węzeł) = 1 - Σ(p_i²)',
              '# p_i = proporcja klasy i w węźle',
              '',
              '# Przykłady:',
              '# Węzeł z 50% chorych, 50% zdrowych:   Gini = 1 - (0.5² + 0.5²) = 0.5',
              '# Węzeł z 100% chorych (czysty):        Gini = 1 - (1.0²) = 0.0',
              '# Węzeł z 80% chorych, 20% zdrowych:   Gini = 1 - (0.8² + 0.2²) = 0.32'])
    doc.p('Algorytm szuka podziału który minimalizuje ważoną sumę Gini dzieci. '
          'Im bardziej "czyste" węzły po podziale, tym lepsza cecha.')

    doc.h2('Overfitting drzewa')
    doc.p('Jeśli drzewo rośnie bez ograniczeń, może "zapamiętać" dane treningowe '
          '(każdy liść = 1 próbka). Na treningu: 100% accuracy. Na teście: słabo.')
    doc.p('Kontrolujemy to przez hiperparametry: max_depth, min_samples_split, min_samples_leaf.')

    doc.qa('Czy samo drzewo decyzyjne byłoby wystarczające?',
           'Dla tego datasetu jedno drzewo osiągnęłoby może 75–80% accuracy, ale byłoby '
           'niestabilne — mała zmiana w danych treningowych → inne drzewo. '
           'Random Forest rozwiązuje ten problem przez uśrednianie wielu drzew.')

    doc.divider()


    doc.chapter(6, 'Las Losowy (Random Forest) — Ensemble Learning')

    doc.h2('Bootstrap Sampling — każde drzewo widzi inne dane')
    doc.p('Przy n_estimators=200 tworzymy 200 drzew. Każde drzewo trenuje na losowej '
          'próbie z powtórzeniami (bootstrap sample) z oryginalnego zbioru treningowego.')
    doc.code(['# Pseudokod bootstrap dla jednego drzewa:',
              'n = len(X_train)         # np. 242',
              'indices = random.choice(n, size=n, replace=True)  # z powtórzeniami',
              'X_boot, y_boot = X_train[indices], y_train[indices]',
              '# ok. 63% unikalnych próbek, reszta to duplikaty'])

    doc.h2('Feature Subsampling — każdy węzeł widzi inne cechy')
    doc.p('W każdym węźle drzewa losujemy tylko max_features cech i szukamy najlepszego '
          'podziału tylko spośród nich. Dla max_features="sqrt": √13 ≈ 3–4 cechy.')
    doc.p('DLACZEGO? Gdyby wszystkie drzewa widziały te same cechy, byłyby ze sobą '
          'silnie skorelowane — błędy nie uśredniałyby się. Losowość cech dekorreluje drzewa.')

    doc.h2('Głosowanie większością (Majority Voting)')
    doc.p('Dla klasyfikacji: każde drzewo daje głos (0 lub 1). Liczymy głosy i bierzemy '
          'klasę z większością. Prawdopodobieństwo (predict_proba) = % drzew głosujących za 1.')
    doc.code(['# Dla nowego pacjenta:',
              'y_prob = rf.predict_proba(x_new)[:, 1]   # % drzew: "chory"',
              'y_pred = rf.predict(x_new)               # > 0.5 → chory, inaczej zdrowy'])

    doc.qa('Ile drzew wybrać? Czy więcej zawsze lepiej?',
           'Powyżej ~200–300 drzew jakość modelu się plateau — nie rośnie, ale '
           'czas treningu rośnie liniowo. GridSearch wybrał n_estimators=100, '
           'co sugeruje że dla 303 próbek 100 drzew jest już wystarczające. '
           'Na większych datasetach (>100k próbek) warto testować 500–1000.')

    doc.qa('Czym różni się Random Forest od Bagging?',
           'Bagging (Bootstrap Aggregating) to metoda gdzie każde drzewo trenuje na bootstrap '
           'sample, ale na WSZYSTKICH cechach. Random Forest dodaje do tego feature subsampling '
           '(max_features), co dodatkowo dekorreluje drzewa i poprawia wyniki.')

    doc.divider()


    doc.chapter(7, 'Dwa modele — Baseline vs. Strojony')

    doc.h2('Co to są hiperparametry?')
    doc.p('Hiperparametry to ustawienia modelu które ustalamy PRZED treningiem — '
          'nie są "uczone" z danych. Parametry modelu (wagi) są uczone, '
          'hiperparametry są naszą decyzją.')
    features_hp = [
        ('n_estimators',      'Liczba drzew w lesie',
                              'Więcej = stabilniejszy model, ale wolniejszy trening'),
        ('max_depth',         'Maksymalna głębokość drzewa',
                              'Głębsze = bardziej skomplikowany model, ryzyko overfitting'),
        ('min_samples_split', 'Min. próbek żeby węzeł dzielić',
                              'Wyższe = bardziej "konserwatywne" drzewa, mniej overfitting'),
        ('max_features',      'Ile cech losować w każdym węźle',
                              '"sqrt" = √n_cech ≈ 3–4, "log2" = log₂(13) ≈ 3–4'),
    ]
    for hp, short, detail in features_hp:
        doc.p(f'  {hp:<25} {short}', fontsize=9.5)
        doc.p(f'  {"":<25} {detail}', fontsize=9.0, color='#666')
        doc.vspace(0.03)

    doc.h2('Model bazowy (baseline)')
    doc.p('Model z domyślnymi parametrami biblioteki scikit-learn: n_estimators=100, '
          'max_depth=None (bez limitu), min_samples_split=2, max_features="sqrt". '
          'To jest punkt odniesienia — chcemy wiedzieć ile zyskujemy przez strojenie.')

    doc.h2('Model strojony (GridSearchCV)')
    doc.p('GridSearch testuje wszystkie kombinacje z PARAM_GRID i wybiera najlepszą '
          'wg. cross-validation F1. Wybrał: max_depth=5, max_features="sqrt", '
          'min_samples_split=5, n_estimators=100.')
    doc.p('Dlaczego max_depth=5 jest lepszy niż None (bez limitu)?')
    doc.bullet('Dataset ma tylko 303 próbki — bez limitu głębokości drzewo "zapamiętuje" '
               'dane (overfitting)')
    doc.bullet('max_depth=5 ogranicza złożoność, co poprawia generalizację na zbiorze testowym')
    doc.bullet('Kompromis bias-variance: płytsze drzewo ma wyższy bias ale niższy variance')

    doc.qa('Dlaczego baseline ma takie same Accuracy i F1 (0.8852)?',
           'To zbieg okoliczności dla tego konkretnego podziału danych (random_state=42). '
           'Klasy są zbalansowane (54%/46%), więc Accuracy i F1 dają podobne wyniki. '
           'Przy bardzo niezbalansowanych klasach (np. 90%/10%) Accuracy byłaby ~90% '
           'nawet dla modelu który zawsze mówi "klasa większości", podczas gdy F1 byłoby ~0.')

    doc.divider()


    doc.chapter(8, 'GridSearchCV — Jak znaleźliśmy najlepsze parametry?')

    doc.h2('Cross-Validation (walidacja krzyżowa)')
    doc.p('Zamiast podzielić dane raz (train/test), dzielimy na K części (folds). '
          'Powtarzamy K razy: za każdym razem 1 fold = walidacja, pozostałe = trening. '
          'Wynik = średnia z K iteracji.')
    doc.code(['# 5-Fold Cross-Validation na zbiorze treningowym (242 próbki)',
              '',
              '  Fold 1: [VAL|TRN|TRN|TRN|TRN] → F1_1',
              '  Fold 2: [TRN|VAL|TRN|TRN|TRN] → F1_2',
              '  Fold 3: [TRN|TRN|VAL|TRN|TRN] → F1_3',
              '  Fold 4: [TRN|TRN|TRN|VAL|TRN] → F1_4',
              '  Fold 5: [TRN|TRN|TRN|TRN|VAL] → F1_5',
              '',
              '  Wynik CV = mean([F1_1, F1_2, F1_3, F1_4, F1_5])'])

    doc.h2('Dlaczego 5 foldów?')
    doc.bullet('3 foldy: za mało danych na walidację, wysoka wariancja wyniku')
    doc.bullet('5 foldy: dobry kompromis — popularny standard')
    doc.bullet('10 foldów: dokładniejsza ocena, ale 2x dłuższy czas obliczeń')
    doc.bullet('Leave-One-Out: 303 foldy — bardzo dokładne ale bardzo wolne')

    doc.h2('Jak GridSearch wybiera najlepsze parametry?')
    doc.p('Dla każdej z 72 kombinacji (3×4×3×2) przeprowadza 5-fold CV i oblicza '
          'średnie F1. Wybiera kombinację z najwyższym średnim F1.')
    doc.code(['param_grid = {',
              '    "n_estimators":      [100, 200, 300],     # 3 wartości',
              '    "max_depth":         [None, 5, 10, 15],   # 4 wartości',
              '    "min_samples_split": [2, 5, 10],          # 3 wartości',
              '    "max_features":      ["sqrt", "log2"],    # 2 wartości',
              '}',
              '# 3 × 4 × 3 × 2 = 72 kombinacje × 5 foldów = 360 treningów'])

    doc.h2('Wynik GridSearchCV dla naszego projektu')
    doc.p('Najlepsze parametry: {max_depth: 5, max_features: "sqrt", '
          'min_samples_split: 5, n_estimators: 100}')
    doc.bullet('max_depth=5: drzewo może mieć max 5 poziomów (32 liście). '
               'To "skraca" drzewa i zapobiega overfitting na małym datasecie.')
    doc.bullet('min_samples_split=5: węzeł jest dzielony tylko jeśli ma ≥5 próbek. '
               'Wyklucza podziały na podstawie 2–3 przypadków które mogą być szumem.')
    doc.bullet('n_estimators=100: optymalny ze względu na czas/jakość na 303 próbkach.')

    doc.qa('Dlaczego nie użyć RandomizedSearchCV lub Bayesian Optimization?',
           'GridSearch jest wyczerpujący (testuje wszystkie kombinacje). '
           'Przy 72 kombinacjach to jest rozsądne. Dla dużych grid (np. 1000+ kombinacji) '
           'lepiej użyć RandomizedSearchCV (losujemy N kombinacji) lub Optuna/Hyperopt '
           '(optymalizacja bayesowska). Tutaj GridSearch wystarczy.')

    doc.divider()


    doc.chapter(9, 'Metryki Ewaluacji — Jak mierzymy jakość modelu?')

    doc.h2('Dlaczego Accuracy nie wystarczy?')
    doc.p('Accuracy = (TP+TN)/(wszystkie). Problem: niezbalansowane klasy.')
    doc.code(['# Przykład patologiczny:',
              '# Dataset: 90% zdrowych, 10% chorych',
              '# Model który ZAWSZE mówi "zdrowy":',
              '#   Accuracy = 90%  (wygląda dobrze!)',
              '#   F1-Score = 0.0  (tragiczne — nie wykryto ani jednego chorego)'])

    doc.h2('F1-Score')
    doc.p('F1 łączy dwie metryki: Precision i Recall.')
    doc.code(['Precision = TP / (TP + FP)',
              '# "Z tych co model oznaczyło jako chore, ile naprawdę jest chore?"',
              '',
              'Recall (Czułość) = TP / (TP + FN)',
              '# "Z wszystkich chorych pacjentów, ile model wykrył?"',
              '',
              'F1 = 2 × (Precision × Recall) / (Precision + Recall)',
              '# Harmoniczna średnia — karze mocno za niskie P lub R'])
    doc.p('W medycynie często ważniejszy jest wysoki Recall (nie przeoczaj chorych) '
          'kosztem niższego Precision (trochę fałszywych alarmów jest ok).')

    doc.h2('ROC-AUC (Area Under the ROC Curve)')
    doc.p('Model nie daje bezpośrednio klasy — najpierw oblicza prawdopodobieństwo '
          'p ∈ [0,1]. Próg odcięcia (threshold θ) decyduje: jeśli p > θ → chory.')
    doc.bullet('θ = 0.5: domyślne, standardowe')
    doc.bullet('θ = 0.3: więcej chorych wykrytych (wyższy Recall), ale więcej fałszywych alarmów')
    doc.bullet('θ = 0.7: mało fałszywych alarmów, ale część chorych przeoczona')
    doc.p('Krzywa ROC: dla każdego θ rysujemy punkt (FPR, TPR). AUC = pole pod tą krzywą.')
    doc.code(['AUC = P(score(chory) > score(zdrowy))',
              '# Dla losowych modeli: AUC = 0.5',
              '# Dla idealnego modelu: AUC = 1.0',
              '# Nasz model baseline:  AUC = 0.9513',
              '# Nasz model strojony:  AUC = 0.9481'])
    doc.p('AUC jest niezależna od progu θ — mierzy ogólną zdolność modelu do '
          'rozróżniania klas.')

    doc.h2('MCC — Matthews Correlation Coefficient')
    doc.code(['MCC = (TP×TN - FP×FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))',
              '# Zakres: [-1, 1]',
              '# MCC = 1:   idealny model',
              '# MCC = 0:   predykcja losowa',
              '# MCC = -1:  model zawsze się myli (odwróć decyzje!)'])
    doc.p('MCC uwzględnia WSZYSTKIE 4 komórki macierzy pomyłek (TP, TN, FP, FN). '
          'Jest uważana za jedną z najuczciwszych metryk dla klasyfikacji binarnej, '
          'szczególnie przy niezbalansowanych klasach.')

    doc.qa('Który model jest lepszy gdy F1 rośnie ale ROC-AUC spada?',
           'Zależy od zastosowania. Jeśli zależy nam na konkretnym progu θ=0.5, '
           'lepszy jest model z wyższym F1 (strojony). Jeśli chcemy model który dobrze '
           'rankuje pacjentów niezależnie od progu (np. do triage), lepszy jest model '
           'z wyższym AUC (baseline). W praktyce różnica AUC 0.9513 vs 0.9481 jest '
           'statystycznie nieistotna przy 61 próbkach testowych.')

    doc.divider()


    doc.chapter(10, 'Macierz Pomyłek — Co dokładnie model pomylił?')

    doc.h2('Cztery możliwe wyniki klasyfikacji')
    doc.code(['                  Przewidziana klasa',
              '                  | ZDROWY  | CHORY  |',
              '  ----------------+---------+--------|',
              '  Prawdziwa ZDROWY|   TN    |   FP   |',
              '  klasa    CHORY  |   FN    |   TP   |'])
    doc.vspace(0.1)
    results = [
        ('TN — True Negative',
         'Model mówi ZDROWY, pacjent jest ZDROWY.',
         'Dobry wynik — uniknęliśmy niepotrzebnych badań.'),
        ('FP — False Positive',
         'Model mówi CHORY, pacjent jest ZDROWY. (Fałszywy alarm)',
         'Niekomfortowe dla pacjenta (zbędne badania) ale nie niebezpieczne.'),
        ('FN — False Negative',
         'Model mówi ZDROWY, pacjent jest CHORY. (Przeoczenie!)',
         'NAJGORSZY wynik klinicznie — chory pacjent nie dostaje leczenia!'),
        ('TP — True Positive',
         'Model mówi CHORY, pacjent jest CHORY.',
         'Dobry wynik — chory pacjent zostanie zbadany i leczony.'),
    ]
    for name, meaning, consequence in results:
        doc.p(f'  {name}:', bold=True, fontsize=10)
        doc.p(f'    {meaning}', fontsize=9.5, indent=1)
        doc.p(f'    ⟹ {consequence}', fontsize=9.5, indent=1, color='#555')
        doc.vspace(0.05)

    doc.h2('Wzory metryk z macierzy pomyłek')
    doc.code(['Accuracy  = (TP + TN) / (TP + TN + FP + FN)',
              'Precision = TP / (TP + FP)',
              'Recall    = TP / (TP + FN)',
              'F1        = 2 × Precision × Recall / (Precision + Recall)',
              'Specificity = TN / (TN + FP)   # jak dobrze wykrywamy ZDROWYCH',
              'FPR = FP / (FP + TN)            # = 1 - Specificity (oś X krzywej ROC)'])

    doc.qa('Gdybyś miał wybrać jedną metrykę dla tego problemu medycznego, co by to było?',
           'Recall (czułość). W diagnostyce chorób serca najgorsze jest przeoczenie '
           'chorego pacjenta (FN). Wolimy mieć więcej fałszywych alarmów (FP) — '
           'pacjent zrobi dodatkowe badania — niż przeoczyć kogoś kto naprawdę potrzebuje leczenia. '
           'W praktyce klinicznej próg θ byłby obniżony poniżej 0.5 żeby zwiększyć Recall '
           'kosztem Precision.')

    doc.divider()


    doc.chapter(11, 'Wyniki — Analiza i Interpretacja')

    doc.h2('Wyniki obu modeli')
    doc.code(['               Baseline RF    Strojony RF    Zmiana',
              '  Accuracy  :   0.8852         0.9016       +0.0164',
              '  F1-Score  :   0.8852         0.8966       +0.0114',
              '  ROC-AUC   :   0.9513         0.9481       -0.0032  ←',
              '  MCC       :   0.7825         0.8048       +0.0223'])

    doc.h2('Dlaczego ROC-AUC SPADŁO po strojeniu?')
    doc.p('To ważna obserwacja! GridSearch optymalizował pod scoring="f1", nie pod AUC. '
          'Strojony model jest lepszy w F1 (próg θ=0.5), ale może mieć lekko gorszy '
          'ranking prawdopodobieństw (co mierzy AUC).')
    doc.bullet('max_depth=5 ogranicza drzewa — prawdopodobieństwa mogą być mniej '
               '"precyzyjne" niż przy max_depth=None')
    doc.bullet('Różnica 0.9513 vs 0.9481 wynosi 0.003 — przy 61 próbkach testowych '
               'to statystyczny szum (przedział ufności by się nakładał)')
    doc.bullet('Wniosek: strojenie pod F1 dało model lepszy wg. F1/MCC, '
               'ale nie poprawiło rankingu prawdopodobieństw')

    doc.h2('Co oznaczają te liczby w praktyce?')
    doc.bullet('Accuracy 0.9016 → model poprawnie klasyfikuje ~90% przypadków (55/61)')
    doc.bullet('F1 0.8966 → dobry balans Precision i Recall')
    doc.bullet('ROC-AUC 0.9481 → w ~95% par (chory, zdrowy) model daje choremu wyższy score')
    doc.bullet('MCC 0.8048 → silna korelacja między predykcjami a prawdziwymi etykietami')

    doc.qa('Czy wyniki 90% accuracy to dużo? Czy to wystarczy klinicznie?',
           'Na datasecie edukacyjnym (303 próbki) to dobry wynik. Ale w klinice '
           'progi wymagań są znacznie wyższe — FDA wymaga walidacji na tysiącach pacjentów, '
           'specyficznych grup demograficznych, i niezależnych zbiorach testowych. '
           'Nasze 90% na 61 próbkach ma duży margines błędu (±5–8%).')

    doc.qa('Dlaczego cross-validation daje inne wyniki niż test set?',
           'Cross-validation jest robiona NA ZBIORZE TRENINGOWYM (242 próbki) — '
           'mierzy jak model generalizuje na danych podobnych do treningowych. '
           'Test set (61 próbek) to zupełnie nowe dane — może trochę inny rozkład. '
           'Stąd różnica. Dla małych datasetów CV jest bardziej miarodajne.')

    doc.divider()


    doc.chapter(12, 'Krzywa ROC — Wizualizacja Jakości Modelu')

    doc.h2('Jak krok po kroku tworzymy krzywą ROC?')
    doc.code(['# 1. Dla każdego pacjenta w test set oblicz prawdopodobieństwo:',
              'y_prob = best_model.predict_proba(X_test)[:, 1]',
              '# y_prob = [0.82, 0.13, 0.67, 0.91, 0.05, ...]  61 wartości',
              '',
              '# 2. sklearn oblicza FPR i TPR dla wszystkich progów θ:',
              'fpr, tpr, thresholds = roc_curve(y_test, y_prob)',
              '# thresholds to unikalne wartości w y_prob (ok. 60 progów)',
              '',
              '# 3. Dla każdego θ mamy punkt (FPR, TPR) na wykresie',
              '# θ=1.0 → punkt (0, 0): nie klasyfikujemy nic jako chore',
              '# θ=0.0 → punkt (1, 1): wszystko klasyfikujemy jako chore'])

    doc.h2('Interpretacja krzywej ROC')
    doc.bullet('Linia "k--" (przekątna): model losowy (AUC=0.5). Rzut monetą.')
    doc.bullet('Im bardziej krzywa wygina się ku lewemu górnemu rogowi, tym lepiej.')
    doc.bullet('Idealny model: punkt (0,0) → (0,1) → (1,1). AUC=1.0')
    doc.bullet('Nasz model: AUC=0.9481 — blisko ideału, krzywa mocno nad przekątną.')

    doc.h2('Probabilistyczna interpretacja AUC')
    doc.code(['AUC = P( score(losowy_chory) > score(losowy_zdrowy) )',
              '',
              '# AUC = 0.9481 oznacza:',
              '# "Weź losowego chorego i losowego zdrowego z test set.',
              '#  W 94.81% przypadków model da choremu wyższy score."',
              '',
              '# To elegancka interpretacja niezależna od progów.'])

    doc.qa('Jak wybrać próg θ w praktyce?',
           'Zależy od kontekstu. Jeśli FN jest droższy niż FP (jak w diagnostyce): '
           'obniżamy θ poniżej 0.5, np. θ=0.3. Zwiększamy Recall kosztem Precision. '
           'Możemy narysować krzywą Precision-Recall i wybrać punkt odpowiadający '
           'akceptowalnemu poziomowi fałszywych alarmów.')

    doc.divider()


    doc.chapter(13, 'Ważność Cech — Które dane są kluczowe?')

    doc.h2('Jak obliczana jest Gini Importance?')
    doc.p('Dla każdego węzła w każdym drzewie obliczamy "spadek zanieczyszczenia":')
    doc.code(['spadek_Gini(węzeł) = Gini_przed - (w_lewy × Gini_lewy + w_prawy × Gini_prawy)',
              '# w_lewy/w_prawy = proporcja próbek idących w lewo/prawo',
              '',
              '# Dla cechy X sumujemy spadki Gini z wszystkich węzłów gdzie X był użyty',
              '# Normalizujemy i uśredniamy po 100 (lub 200) drzewach',
              '# Wynik: feature_importances_  (suma = 1.0)'])

    doc.h2('Interpretacja wyników dla Heart Disease UCI')
    top5 = [
        ('thal (14.8%)',    'Typ talasemii — anomalia transportu tlenu we krwi. '
                           'Utrwalony defekt (typ 2) silnie koreluje z chorobą serca.'),
        ('cp (13.1%)',      'Typ bólu w klatce piersiowej. Paradoksalnie pacjenci '
                           'z cp=0 (typowy ból wieńcowy) mają MNIEJSZE ryzyko niż '
                           'z cp=2,3 (niespecyficzny ból).'),
        ('ca (11.7%)',      'Liczba zwężonych naczyń wieńcowych. Bezpośredni wskaźnik '
                           'miażdżycy. Więcej zwężeń = wyższe ryzyko.'),
        ('oldpeak (10.8%)', 'Obniżenie odcinka ST po wysiłku. Marker niedokrwienia '
                           'serca podczas wysiłku fizycznego.'),
        ('thalach (9.6%)',  'Maksymalne tętno. Niskie tętno podczas wysiłku może '
                           'wskazywać na niewydolność chronotropową serca.'),
    ]
    for name, desc in top5:
        doc.p(f'  {name}:', bold=True, fontsize=10)
        doc.p(f'    {desc}', fontsize=9.5, indent=1, color='#444')
        doc.vspace(0.04)

    doc.h2('Ograniczenia Gini Importance')
    doc.bullet('Zawyżone dla cech z wieloma unikalnymi wartościami (np. age z 41 wartościami '
               'vs. sex z 2). Dlatego age (7.6%) może być zawyżona.')
    doc.bullet('Lepszą alternatywą jest Permutation Importance: tasujemy jedną cechę i '
               'mierzymy spadek F1. Ale to 13× więcej obliczeń.')
    doc.bullet('SHAP values to najdokładniejsza metoda, ale wymaga dodatkowej biblioteki.')

    doc.qa('Dlaczego fbs (cukier we krwi) ma tak niską ważność (2.2%)?',
           'fbs to cecha binarna (0 lub 1) z małą zmiennością — ~85% pacjentów ma fbs=0. '
           'To ogranicza jej moc predykcyjną. Ponadto w tym zbiorze innych czynników '
           '(thal, cp, ca) jest silniejszych predyktorów. To nie znaczy że cukrzyca '
           'jest klinicznie nieważna — to znaczy że w tym konkretnym datasecie '
           'inne cechy lepiej różnicują chorych od zdrowych.')

    doc.divider()


    doc.chapter(14, 'Wnioski i Podsumowanie')

    doc.h2('Co osiągnęliśmy?')
    doc.bullet('Zbudowaliśmy kompletny pipeline ML: EDA → preprocessing → trening → ewaluacja')
    doc.bullet('Random Forest z GridSearchCV osiągnął Accuracy=90%, F1=0.897, AUC=0.948')
    doc.bullet('Strojenie hiperparametrów poprawiło F1 i MCC, ale nieznacznie obniżyło AUC')
    doc.bullet('Feature Importance wskazało cechy zgodne z wiedzą kliniczną (thal, cp, ca)')
    doc.bullet('Projekt jest kompletnie udokumentowany i reprodukowalny (random_state=42)')

    doc.h2('Ograniczenia projektu')
    doc.bullet('Mały dataset: 303 próbki → duży margines błędu, wyniki niestabilne '
               'przy zmianie random_state')
    doc.bullet('Tylko jeden dataset (Cleveland) — wyniki mogą nie generalizować na inne '
               'populacje (rasowe, geograficzne różnice w kardiologii)')
    doc.bullet('Brak klinicznej walidacji — nie testowaliśmy na niezależnym zbiorze z innego szpitala')
    doc.bullet('Gini Importance zamiast Permutation Importance — może zawyżać cechy ciągłe')

    doc.h2('Co można by poprawić?')
    doc.bullet('Więcej danych: Cleveland + Hungarian + Switzerland UCI (łącznie ~900 próbek)')
    doc.bullet('SMOTE: synthetic oversampling jeśli klasy byłyby niezbalansowane')
    doc.bullet('Porównanie modeli: XGBoost, LightGBM, SVM, Logistic Regression')
    doc.bullet('Threshold tuning: obniżyć θ żeby zoptymalizować Recall dla zastosowań klinicznych')
    doc.bullet('Permutation Importance lub SHAP zamiast Gini Importance')
    doc.bullet('Kalibracja prawdopodobieństw (Platt scaling) dla lepszego predict_proba')

    doc.h2('Podsumowanie wyników')
    doc.code(['Model           | Accuracy | F1-Score | ROC-AUC | MCC',
              '----------------|----------|----------|---------|------',
              'Baseline RF     |  0.8852  |  0.8852  | 0.9513  | 0.7825',
              'Strojony RF     |  0.9016  |  0.8966  | 0.9481  | 0.8048',
              '                |          |          |         |',
              'Najlepszy model: Strojony RF (F1=0.8966, MCC=0.8048)'])

    doc.qa('Gdybyś miał wdrożyć ten model produkcyjnie, co byś zrobił inaczej?',
           '1) Więcej danych — minimum kilka tysięcy pacjentów. '
           '2) Kalibracja modelu — predict_proba musi być dobrze skalibrowane dla "pewności diagnozy". '
           '3) Monitorowanie: model w produkcji "dryftuje" — nowe leki, zmiany demograficzne. '
           '4) Explainability: SHAP dla każdego pacjenta indywidualnie. '
           '5) Fairness audit: czy model działa równie dobrze dla kobiet i mężczyzn, '
           'różnych grup wiekowych.')

    doc.vspace(0.2)
    doc.p('Projekt realizowany w ramach kursu Uczenie Maszynowe | 2025/2026',
          color='#888', fontsize=9)


def generate(output='skrypt.pdf'):
    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    with PdfPages(output) as pdf:
        doc = Doc(pdf)
        build(doc)
        doc.finish()
    print(f"Skrypt wygenerowany: {output}")


if __name__ == '__main__':
    generate()
