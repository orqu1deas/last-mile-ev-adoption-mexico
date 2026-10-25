from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Rectangle

PRIMARY = '#1e3453' ; GOLD = '#cea64d' ; CREAM = '#f9f0e1'
OFFWHITE = '#fdfbf7' ; LIGHT_BLUE = '#a3b7d5' ; MID_BLUE = '#6d88a6'
PALE_BLUE = '#dbe6f0' ; INK = '#1e3453' ; MUTED = '#61748b'
GRID = '#dee6ec' ; SPINE = '#d2dfe9'
MODEL_COLORS = ['#1e3453','#6d88a6','#cea64d','#9a7642','#78919c',
                '#7488b5','#986b69','#b28e62','#4b7292']
SOURCE = 'Source: Mexican small-cargo survey (105 submissions; 92 distinct rows).'


def apply_style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'figure.dpi': 110, 'savefig.dpi': 240,
        'figure.facecolor': 'white', 'savefig.facecolor': 'white',
        'axes.facecolor': 'white', 'axes.titlesize': 14, 'axes.labelsize': 11,
        'xtick.labelsize': 10.5, 'ytick.labelsize': 10.5, 'legend.fontsize': 9,
        'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': INK,
        'ytick.color': INK, 'axes.edgecolor': SPINE, 'axes.axisbelow': True,
        'axes.spines.top': False, 'axes.spines.right': False,
        'grid.color': GRID, 'grid.linewidth': 0.85, 'grid.alpha': 1.0,
        'svg.fonttype': 'none', 'pdf.fonttype': 42})


def axis_style(ax, orientation = 'y'):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(SPINE)
    ax.spines['left'].set_color(SPINE) 

    ax.tick_params(axis = 'both', direction = 'out', length = 0, width = 0.7, pad = 5, labelcolor = INK)
    if orientation in {'x', 'y', 'both'}:
        ax.grid(axis = orientation, color = GRID, linewidth = 0.85)
    else:
        ax.grid(False)
    ax.set_axisbelow(True)
    return ax


def make_panel(ncols, title, subtitle, *, height = 7.1, width_per_panel = 7.0):
    apply_style()
    width = width_per_panel * ncols + 0.4
    fig, axes = plt.subplots(1, ncols, figsize=(width, height), squeeze = False)
    fig.subplots_adjust(left = (.165 if ncols >= 3 else .09), right = .96,
                        bottom = .19, top = .75, wspace = .40)
    fig.add_artist(plt.Line2D([.047, .985], [.977, .977], transform = fig.transFigure,
                              color = PRIMARY, linewidth = 1.15))
    fig.add_artist(Rectangle((.047, .957), .05, .020, transform = fig.transFigure,
                             facecolor = PRIMARY, edgecolor = 'none', clip_on = False))
    fig.text(.047, .918, title, size = 20.5, color = INK, weight = 'bold', ha = 'left')
    fig.text(.047, .867, subtitle, size = 12.3, color = MUTED, ha = 'left')
    return fig, axes.flatten()


def title_axis(ax, title):
    ax.set_title(title, fontsize = 14.0, color = INK, pad = 11, loc = 'left', weight = 'normal')


def set_percent(ax, orientation = 'x'):
    if orientation == 'x':
        ax.set_xlim(0, 1.03)
        ax.xaxis.set_major_formatter(mticker.PercentFormatter(1))
    else:
        ax.set_ylim(0, 1.03)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1))


def export(fig, section, stem, note = '', root = None):
    if root is None:
        from .config import FIGURES
        root = FIGURES
    folder = Path(root) / section
    folder.mkdir(parents = True, exist_ok = True)
    fig.text(.047, .045, SOURCE, fontsize = 10.3, color = MUTED, ha = 'left')
    if note:
        fig.text(.047, .018, note, fontsize = 8.6, color = MUTED, ha = 'left')
    for extension in ('png', 'svg'):
        fig.savefig(folder / f'{stem}.{extension}', dpi = 240, facecolor = 'white')
    plt.close(fig)
    return folder / f'{stem}.png'
