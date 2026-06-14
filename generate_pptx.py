"""
Generator prezentacji PPTX - Projekt Uczenie Maszynowe
Uruchom: python generate_pptx.py
"""

import io
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, '.')

# importujemy gotowe funkcje slajdów z generate_pdf.py
from generate_pdf import (
    slide_title, slide_dataset, slide_flow, slide_preprocessing,
    slide_tree, slide_forest, slide_two_models, slide_gridsearch,
    slide_metrics, slide_confusion, slide_results, slide_roc,
    slide_conclusions,
    W, H, BLUE, LBLUE, GRAY, DKGRAY, GREEN, RED, ORANGE,
    new_slide, code_block,
)


class _PngCapture:
    """Podmiennik za PdfPages — przechwytuje figury jako PNG do RAM"""
    def __init__(self):
        self.bufs = []

    def savefig(self, fig, **kwargs):
        kwargs.pop('bbox_inches', None)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', **kwargs)
        buf.seek(0)
        self.bufs.append(buf)


def _slide_features_fixed(pdf):
    """
    Poprawiona wersja slide_features — pokazuje wszystkie 13 cech.
    Wykres zajmuje pełną szerokość slajdu.
    """
    fig, ax = new_slide('Ważność Cech — Które informacje są kluczowe?',
                        'Feature Importance (Gini Importance) — wszystkie 13 cech')

    ax.text(0.5, 7.6,
            'Las Losowy sam nam mówi, które cechy były najważniejsze przy podejmowaniu decyzji.',
            fontsize=13, color=DKGRAY)
    ax.text(0.5, 7.15,
            'Ważność Gini = jak bardzo dana cecha zmniejsza nieczystość węzłów (im wyżej, tym ważniejsza).',
            fontsize=11, color='#666')

    features = ['thal', 'cp', 'ca', 'oldpeak', 'thalach', 'age', 'chol',
                'trestbps', 'slope', 'sex', 'restecg', 'exang', 'fbs']
    importances = [0.148, 0.131, 0.117, 0.108, 0.096, 0.076, 0.068,
                   0.065, 0.062, 0.044, 0.038, 0.025, 0.022]

    # pełna szerokość slajdu, więcej miejsca na etykiety
    ax_bar = fig.add_axes([0.04, 0.15, 0.92, 0.50])
    colors = [RED if i < 5 else BLUE if i < 9 else '#AAAAAA' for i in range(len(features))]
    bars = ax_bar.bar(range(len(features)), importances,
                      color=colors, alpha=0.85, edgecolor='white', linewidth=0.8)
    ax_bar.set_xticks(range(len(features)))
    ax_bar.set_xticklabels(features, rotation=35, ha='right', fontsize=10)
    ax_bar.set_ylabel('Ważność (Gini)', fontsize=10)
    ax_bar.set_title('Ważność cech wg. Random Forest (wszystkie 13)', fontsize=11)
    ax_bar.grid(True, alpha=0.25, axis='y')
    ax_bar.set_xlim(-0.6, len(features) - 0.4)

    # wartości nad słupkami
    for i, (bar, val) in enumerate(zip(bars, importances)):
        ax_bar.text(bar.get_x() + bar.get_width() / 2, val + 0.003,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=8, color='#444')

    # legenda kolorów
    ax.text(0.5, 1.3,
            '■ Top 5 (czerwone): thal, cp, ca, oldpeak, thalach — najsilniejszy wpływ kliniczny',
            fontsize=10.5, color=RED)
    ax.text(0.5, 0.95,
            '■ Cechy 6–9 (niebieskie): age, chol, trestbps, slope — umiarkowany wpływ',
            fontsize=10.5, color=BLUE)
    ax.text(0.5, 0.6,
            '■ Cechy 10–13 (szare): sex, restecg, exang, fbs — mały wpływ na tym datasecie',
            fontsize=10.5, color='#888')

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def generate(output='prezentacja.pptx',
             results_baseline=None, results_tuned=None):

    if results_baseline is None:
        results_baseline = {'accuracy': 0.8852, 'f1': 0.8852, 'roc_auc': 0.9513, 'mcc': 0.7825}
    if results_tuned is None:
        results_tuned = {'accuracy': 0.9016, 'f1': 0.8966, 'roc_auc': 0.9481, 'mcc': 0.8048}

    plt.rcParams.update({'font.family': 'DejaVu Sans'})

    cap = _PngCapture()

    slide_title(cap)
    slide_dataset(cap)
    slide_flow(cap)
    slide_preprocessing(cap)
    slide_tree(cap)
    slide_forest(cap)
    slide_two_models(cap)
    slide_gridsearch(cap)
    slide_metrics(cap)
    slide_confusion(cap)
    slide_results(cap, results_baseline, results_tuned)
    slide_roc(cap)
    _slide_features_fixed(cap)   # <-- poprawiona wersja (wszystkie 13)
    slide_conclusions(cap, results_tuned)

    from pptx import Presentation
    from pptx.util import Cm

    prs = Presentation()
    prs.slide_width = Cm(33.87)
    prs.slide_height = Cm(19.05)
    blank_layout = prs.slide_layouts[6]  # blank

    for buf in cap.bufs:
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(buf, 0, 0,
                                  width=prs.slide_width,
                                  height=prs.slide_height)

    prs.save(output)
    print(f"PPTX wygenerowany: {output}  ({len(cap.bufs)} slajdów)")


if __name__ == '__main__':
    generate()
