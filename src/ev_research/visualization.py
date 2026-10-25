import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from .config import FIGURES, PALETTE


def set_research_style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 14,
        'axes.titleweight': 'bold', 'axes.labelcolor': PALETTE['ink'],
        'axes.edgecolor': PALETTE['grid'], 'axes.spines.top': False,
        'axes.spines.right': False, 'xtick.color': PALETTE['gray'],
        'ytick.color': PALETTE['gray'], 'text.color': PALETTE['ink'],
        'grid.color': PALETTE['grid'], 'axes.facecolor': 'white',
        'figure.facecolor': 'white', 'savefig.facecolor': 'white',
        'savefig.dpi': 220, 'axes.axisbelow': True})


def save_figure(fig, stem, folder = FIGURES):
    folder.mkdir(parents = True, exist_ok = True)
    fig.savefig(folder / f'{stem}.png', bbox_inches = 'tight', dpi = 230)
    fig.savefig(folder / f'{stem}.svg', bbox_inches = 'tight')
    plt.close(fig)


def plot_prevalence(prevalence):
    set_research_style()
    fig, ax = plt.subplots(figsize = (8.5, 4.5))
    mapping = {'ev_use': 'Current EV use', 'ev_consideration': 'EV consideration'}
    labels = [mapping[k] for k in prevalence.outcome]
    x = np.arange(len(labels))
    lo = (prevalence.rate - prevalence.wilson_95_low).to_numpy()
    hi = (prevalence.wilson_95_high - prevalence.rate).to_numpy()
    ax.bar(x, prevalence.rate, width = 0.53, color = [PALETTE['navy'], PALETTE['medium']])
    ax.errorbar(x, prevalence.rate, yerr = np.array([lo, hi]), fmt = 'none', color = PALETTE['ink'], capsize = 5)
    for index, row in prevalence.iterrows():
        ax.text(index, row.rate + hi[index] + .04, f'{row.positive}/{row.n} ({row.rate:.1%})',
                ha = 'center', fontsize = 10, weight = 'bold')
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 0.95)
    ax.set_ylabel('Proportion of valid responses')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.set_title('EV adoption and consideration among eligible respondents', loc = 'left', pad = 20)
    ax.grid(axis='y', alpha=.7)
    fig.text(.09, .005, 'Wilson 95% intervals assume independent responses; non-probability sampling limits generalization.',
             fontsize=8, color=PALETTE['gray'])
    fig.tight_layout(rect=[0, .055, 1, .99])
    save_figure(fig, '01_ev_outcomes')


def plot_model_comparison(summary):
    if summary.empty:
        return
    set_research_style()
    outcome_names = {'ev_use': 'Current EV use', 'ev_consideration': 'EV consideration'}
    for (outcome, scenario), subset in summary.groupby(['outcome', 'scenario']):
        subset = subset.sort_values('balanced_accuracy_mean', ascending = True)
        fig, ax = plt.subplots(figsize = (9.5, max(4.0, len(subset) * .55 + 1.6)))
        bars = ax.barh(subset.model, subset.balanced_accuracy_mean, height = .65,
                       color = PALETTE['blue'])
        error = subset.balanced_accuracy_sd.fillna(0).to_numpy()
        ax.errorbar(subset.balanced_accuracy_mean, np.arange(len(subset)), xerr = error,
                    fmt = 'none', ecolor = PALETTE['navy'], capsize = 3)
        for index, (bar, score) in enumerate(zip(bars, subset.balanced_accuracy_mean)):
            ax.text(min(score + error[index] + .025, .96), bar.get_y() + bar.get_height() / 2,
                    f'{score:.3f}', va = 'center', fontsize = 9)
        ax.axvline(.5, color = PALETTE['gray'], ls = '--', lw = 1)
        ax.set_xlim(0, 1)
        ax.set_xlabel('Mean out-of-fold balanced accuracy across split seeds')
        ax.set_title(f'{outcome_names[outcome]} | {scenario.replace('_', ' ').title()}', loc = 'left', pad = 18)
        ax.grid(axis = 'x', alpha = 0.6)
        fig.text(0.12, 0.01,
                 'Error bars: standard deviation across split seeds, NOT a confidence interval or independent replication.',
                 color = PALETTE['gray'], fontsize = 8)
        fig.tight_layout(rect = [0, 0.05, 1, 1])
        save_figure(fig, f'02_models_{outcome}_{scenario}')
