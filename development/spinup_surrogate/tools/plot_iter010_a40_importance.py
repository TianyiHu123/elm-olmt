#!/usr/bin/env python3
import json, os, pickle, re, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT='/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output'
REPO='/xdisk/chopinsong/tianyihu/elm-olmt'
sys.path.insert(0, REPO)
VARIANTS=['s32_tanh_lbfgs_a40_lr1e3_full45','s32_tanh_lbfgs_a40_lr1e3_corr080_prioritydrop','s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf']
TARGETS=['TOTSOMC','TOTSOMN']
COLORS={'full45':'#1f77b4','corr080':'#ff7f0e','drop32':'#2ca02c'}

class _Placeholder:
    pass
class _MetadataUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith('model_ELM'):
            return _Placeholder
        return super().find_class(module, name)
with open(os.path.join(REPO,'pklfiles','ABBY_ppe6_I20TRCNPRDCTCBC.pkl'),'rb') as f:
    case=_MetadataUnpickler(f).load()
names=getattr(case,'ensemble_parms',None) if not isinstance(case,dict) else case.get('ensemble_parms')
if names is None: raise RuntimeError('ensemble_parms not found')
labels={f'parm_{i}':str(x) for i,x in enumerate(list(names)[:14])}

def short(v):
    return 'full45' if 'full45' in v else ('corr080' if 'corr080' in v else 'drop32')
def load(v,t):
    p=os.path.join(ROOT,'spinup_surrogate_iter010_'+v+'_importance_100seed.json')
    # importance artifacts are in the repository summary directory, not scratch output
    p=os.path.join(REPO,'development','spinup_surrogate','summaries','iter010',v+'_importance_100seed.json')
    with open(p) as f: d=json.load(f)
    rows=d['by_target'][t]
    out={r['feature']:float(r.get('median_rmse_increase',r.get('rmse_increase',r.get('mean_rmse_increase')))) for r in rows}
    return out

data={(v,t):load(v,t) for v in VARIANTS for t in TARGETS}
all_features=set().union(*(x.keys() for x in data.values()))
score={f:np.median([data[(v,t)].get(f,0.0) for v in VARIANTS for t in TARGETS]) for f in all_features}
top=sorted(all_features,key=lambda f:score[f],reverse=True)[:15]
display=[labels.get(f,f) for f in top]
for v in VARIANTS:
    for t in TARGETS:
        for f in top: labels.setdefault(f,f)

fig,axes=plt.subplots(1,2,figsize=(15,9),sharey=True,constrained_layout=True)
y=np.arange(len(top))
for ax,t in zip(axes,TARGETS):
    for j,v in enumerate(VARIANTS):
        vals=[data[(v,t)].get(f,0.0) for f in top]
        ax.barh(y+(j-1)*0.25,vals,height=0.23,label=short(v),color=COLORS[short(v)],alpha=.8)
    ax.set_yticks(y); ax.set_yticklabels(display); ax.invert_yaxis(); ax.set_title(t)
    ax.set_xlabel('Median RMSE increase'); ax.grid(axis='x',alpha=.25)
axes[0].legend(); fig.suptitle('Iter010 alpha-40 permutation importance: top 15 features')
for v in VARIANTS: fig.savefig(os.path.join(ROOT,'spinup_surrogate_iter010_'+v,'iter010_a40_feature_importance_rmse_top15.png'),dpi=180)
plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(13,9),constrained_layout=True)
for ax,t in zip(axes,TARGETS):
    mat=np.array([[data[(v,t)].get(f,0.0) for v in VARIANTS] for f in top])
    im=ax.imshow(mat,aspect='auto',cmap='viridis')
    ax.set_yticks(y); ax.set_yticklabels(display); ax.set_xticks(range(3)); ax.set_xticklabels(['full45','corr080','drop32'],rotation=30,ha='right'); ax.set_title(t)
    ax.set_xlabel('Feature policy');
    for i in range(len(top)):
        for j in range(3): ax.text(j,i,f'{mat[i,j]:.0f}',ha='center',va='center',fontsize=7,color='white' if mat[i,j] > np.nanmax(mat)*.45 else 'black')
fig.colorbar(im,ax=axes,label='Median RMSE increase'); fig.suptitle('Iter010 alpha-40 permutation importance heatmap: top 15 features')
for v in VARIANTS: fig.savefig(os.path.join(ROOT,'spinup_surrogate_iter010_'+v,'iter010_a40_feature_importance_heatmap_top15.png'),dpi=180)
plt.close(fig)
print('parameter_labels',labels); print('top15',display)
