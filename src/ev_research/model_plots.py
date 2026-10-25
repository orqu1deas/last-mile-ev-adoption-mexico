import numpy as np
import pandas as pd
from sklearn.metrics import (auc,roc_curve, precision_recall_curve,
                             confusion_matrix, ConfusionMatrixDisplay)
from .plotting_style import (PRIMARY, MID_BLUE, LIGHT_BLUE, GOLD, INK, MUTED,
                             MODEL_COLORS, make_panel, axis_style, title_axis,
                             export)

DISPLAY_NAMES={'dummy' : 'Majority baseline',' logistic_l2' : 'Logistic L2',
               'logistic_l1' : 'Logistic L1', 'linear_svm' : 'Linear SVM',
               'decision_tree' : 'Decision Tree', 'bernoulli_nb' : 'Bernoulli NB',
               'random_forest' : 'Random Forest', 'lightgbm' : 'LightGBM'}


def _subset(summary,outcome,scenario):
    return summary[(summary.outcome == outcome) & (summary.scenario == scenario)].copy()


def _section(outcome):
    return '03_ev_use' if outcome=='ev_use' else '04_ev_consideration'


def plot_model_dashboard(summary, outcome, scenario):
    frame = _subset(summary, outcome, scenario).sort_values('balanced_accuracy_mean')
    if frame.empty: return None
    fig, axs = make_panel(3, 'Cross-validated model performance — ' + ('current EV use' if outcome == 'ev_use' else 'EV consideration'),
        scenario.replace('_', ' ').title() + ' · three validation seeds · nested stratified cross-validation',
        height = 7.3, width_per_panel = 5.6)
    fig.subplots_adjust(left = .155, right = .97, wspace = .55)
    for ax, metric, title in zip(axs,['balanced_accuracy', 'roc_auc', 'f1'], ['Balanced accuracy', 'ROC-AUC', 'F1 score']):
        names = [DISPLAY_NAMES.get(name, name) for name in frame.model]
        means = frame[f'{metric}_mean'].to_numpy()
        sds = frame[f'{metric}_sd'].fillna(0).to_numpy()
        colors = [GOLD if name == frame.iloc[-1].model else PRIMARY for name in frame.model]
        ax.barh(names, means, color = colors,xerr = sds,
                error_kw = dict(ecolor = MUTED, capsize = 3, elinewidth = .9), height = .68)
        ax.set_xlim(0, 1.03)
        if metric in {'roc_auc', 'balanced_accuracy'}:ax.axvline(.5, color = MUTED, linewidth = 1, linestyle = '--')
        axis_style(ax,'x');title_axis(ax, title)
        ax.set_xlabel('Mean score over split seeds')
    return export(fig, _section(outcome), f'02_model_dashboard_{scenario}',
                  'Error bars show between-seed SD, not confidence intervals; the same survey was resplit.')


def _single_seed(predictions, outcome, scenario, seed = 42):
    frame = predictions[(predictions.outcome == outcome) & (predictions.scenario == scenario)].copy()
    if frame.empty: return frame, None
    choices = sorted(frame.seed.unique())
    selected = int(seed if seed in choices else choices[0])
    frame = frame[frame.seed == selected]
    assert not frame.duplicated(['model', 'source_record_index']).any(), 'Duplicate OOF respondent/model predictions'
    return frame, selected


def plot_roc_dashboard(predictions, outcome, scenario,seed = 42):
    frame, selected = _single_seed(predictions, outcome, scenario, seed)
    if frame.empty: return None
    fig, axs = make_panel(2, 'Out-of-fold ROC curves — ' + ('current EV use' if outcome == 'ev_use' else 'EV consideration'),
        scenario.replace('_', ' ').title() + f' · held-out predictions from seed {selected}', height = 7.4)
    fig.subplots_adjust(left = .12, right = .96, wspace = .42)
    scores = []
    for i, (name, group) in enumerate(frame.groupby('model', sort = True)):
        if group.y_true.nunique() < 2: continue
        fpr, tpr, _ = roc_curve(group.y_true, group.score)
        area = auc(fpr, tpr)
        axs[0].plot(fpr, tpr, color = MODEL_COLORS[i % len(MODEL_COLORS)], lw = 2,
                    label = f'{DISPLAY_NAMES.get(name, name)} · {area:.2f}')
        scores.append((DISPLAY_NAMES.get(name, name), area))
    axs[0].plot([0, 1], [0, 1], ls = '--', c = MUTED, lw = 1)
    axs[0].set_xlim(0, 1); axs[0].set_ylim(0, 1)
    axs[0].set_xlabel('False-positive rate'); axs[0].set_ylabel('True-positive rate')
    axis_style(axs[0], 'both'); title_axis(axs[0], 'Receiver operating characteristic')
    axs[0].legend(loc = 'lower right', frameon = False, fontsize = 8)
    fig.subplots_adjust(left = .12, right = .96, wspace = .46)
    scores = sorted(scores,key = lambda x:x[1])
    axs[1].barh([x[0] for x in scores], [x[1] for x in scores], color = PRIMARY, height = .62)
    axs[1].set_xlim(0,1.04); axis_style(axs[1],'x'); title_axis(axs[1], 'Same-seed ROC-AUC comparison')
    axs[1].set_xlabel('Area under ROC curve')
    return export(fig ,_section(outcome), f'03_roc_{scenario}',
                  'Cross-validation predictions, not an independent external test. SVM uses decision margins.')


def plot_precision_recall_and_confusion(predictions, summary, outcome, scenario, seed = 42):
    frame, selected = _single_seed(predictions, outcome, scenario, seed)
    ranked = _subset(summary, outcome, scenario)
    if frame.empty or ranked.empty:return None
    winner = ranked.sort_values(['balanced_accuracy_mean', 'roc_auc_mean'], ascending = False).iloc[0].model
    best = frame[frame.model == winner]
    if best.empty: return None
    fig, axs = make_panel(2, 'Out-of-fold classification diagnostics — ' + ('EV use' if outcome == 'ev_use' else 'EV consideration'),
        scenario.replace('_', ' ').title() + f' · model selected by multi-seed balanced accuracy · seed {selected}', height = 7.3)
    y = best.y_true.astype(int).to_numpy()
    yhat = best.y_pred.astype(int).to_numpy()
    precision, recall, _ = precision_recall_curve(y, best.score.to_numpy())
    axs[0].plot(recall, precision, color = PRIMARY, lw = 2.4)
    axs[0].axhline(y.mean(), color = GOLD, ls = '--', lw = 1.5,label = f'Observed prevalence {y.mean():.1%}')
    axs[0].set_xlim(0,1); axs[0].set_ylim(0,1)
    axs[0].set_xlabel('Recall'); axs[0].set_ylabel('Precision')
    axs[0].legend(loc = 'lower left', frameon = False);axis_style(axs[0], 'both')
    title_axis(axs[0], f'Precision–recall · {DISPLAY_NAMES.get(winner, winner)}')
    cm = confusion_matrix(y,yhat,labels=[0,1])
    
    from matplotlib.colors import LinearSegmentedColormap
    from .plotting_style import PALE_BLUE
    cmap = LinearSegmentedColormap.from_list('research_blue', ['#ffffff', PALE_BLUE, PRIMARY])
    axs[1].imshow(cm, cmap = cmap, vmin = 0, vmax = max(cm.max(), 1) * 1.15)
    axs[1].set_xticks([0, 1] ,['Predicted no', 'Predicted yes']); axs[1].set_yticks([0, 1], ['Actual no', 'Actual yes'])
    axs[1].set_xlabel('Predicted outcome'); axis_style(axs[1], 'none')
    for i in range(2):
        for j in range(2):
            axs[1].text(j, i, str(cm[i,j]), ha = 'center', va = 'center', fontsize = 20,
                        color = 'white' if cm[i,j] > cm.max() * .58 else PRIMARY)
    title_axis(axs[1], 'Held-out confusion matrix')
    return export(fig, _section(outcome), f'04_pr_confusion_{scenario}',
                  'The displayed model was selected using these same survey outcomes; diagnostic is descriptive.')


def plot_seed_stability(summary, outcome):
    frame = summary[summary.outcome == outcome]
    if frame.empty: return None
    fig, axs = make_panel(2, 'Stability across predictor scenarios',
        'Reported means and between-seed variation summarize repeated stratified resplits.', height = 7.1)
    fig.subplots_adjust(left = .16, right = .96, wspace = .42)
    for ax,scenario in zip(axs, ['fleet_baseline', 'operational_extended']):
        d = frame[frame.scenario == scenario].sort_values('balanced_accuracy_mean')
        if d.empty: continue
        x = d.balanced_accuracy_mean.to_numpy(); err = d.balanced_accuracy_sd.fillna(0).to_numpy()
        ax.barh([DISPLAY_NAMES.get(x, x) for x in d.model], x, color = PRIMARY, height = .66)
        ax.errorbar(x, np.arange(len(x)), xerr = err, fmt = 'none', ecolor = GOLD, capsize = 4)
        ax.axvline(.5, color = MUTED, lw = 1, ls = '--'); ax.set_xlim(0, 1)
        title_axis(ax, scenario.replace('_',' ').title()); axis_style(ax, 'x')
        ax.set_xlabel('Balanced accuracy ± between-seed SD')
    return export(fig, _section(outcome), '05_seed_stability',
                  'Error bars are not independent-sample uncertainty intervals.')
