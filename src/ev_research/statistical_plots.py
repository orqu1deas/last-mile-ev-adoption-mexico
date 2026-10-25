import numpy as np
from .plotting_style import (PRIMARY,MID_BLUE,GOLD,INK,MUTED,make_panel,
                             axis_style,title_axis,export)


def plot_association_overview(associations):
    if associations.empty:return None
    fig,axs=make_panel(2,'Exploratory binary associations with EV outcomes',
        'Fisher exact tests with within-outcome FDR correction; no causal inference.',height=7.8)
    for ax,target,heading in zip(axs,['ev_use','ev_consideration'],['Current EV use','EV consideration']):
        frame=associations[associations.outcome==target].sort_values('fisher_p').head(8).iloc[::-1]
        if frame.empty:continue
        score=-np.log10(frame.fisher_p.clip(lower=1e-12))
        colors=[GOLD if q<.05 else PRIMARY for q in frame.fdr_bh_q]
        ax.barh(frame.exposure.str.replace('_',' ',regex=False),score,color=colors,height=.65)
        ax.axvline(-np.log10(.05),color=MUTED,ls='--',lw=1)
        title_axis(ax,heading);axis_style(ax,'x')
        ax.set_xlabel('−log10(Fisher p-value)')
    return export(fig,'05_statistical_associations','01_fisher_associations',
                  'Dashed line: unadjusted p = .05. Gold denotes FDR q < .05 if present.')
