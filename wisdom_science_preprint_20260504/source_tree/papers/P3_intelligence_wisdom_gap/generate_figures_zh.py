"""Generate Chinese-language academic figures for P3."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import font_manager

# Try to find Chinese font
zh_fonts = [f.name for f in font_manager.fontManager.ttflist 
            if any(k in f.name for k in ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong'])]
zh_font = zh_fonts[0] if zh_fonts else 'SimHei'
print(f"Using Chinese font: {zh_font}")

plt.rcParams.update({
    'figure.facecolor': '#0a0a0f',
    'axes.facecolor': '#0a0a0f',
    'axes.edgecolor': '#c9b06b',
    'axes.labelcolor': '#e8dcc8',
    'text.color': '#e8dcc8',
    'xtick.color': '#c9b06b',
    'ytick.color': '#c9b06b',
    'grid.color': '#1a1a2e',
    'font.family': zh_font,
    'font.size': 11,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.unicode_minus': False,
})

GOLD = '#c9b06b'
CREAM = '#e8dcc8'
DARK = '#0a0a0f'

with open(r'e:\order-architect-factory\papers\P2_wisdombench\results\summary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

models = ['DeepSeek-V3', 'Qwen-Plus', 'Claude Opus']
strategies = ['no_memory', 'self_refine', 'reflexion', 'cognitive_immunity']
model_colors = {'DeepSeek-V3': '#4a90d9', 'Qwen-Plus': '#d4a04a', 'Claude Opus': '#c75050'}
strat_markers = {'no_memory': 'o', 'self_refine': 's', 'reflexion': 'D', 'cognitive_immunity': '^'}
strat_labels_zh = {'no_memory': '无记忆', 'self_refine': '自我精炼', 
                   'reflexion': '反思', 'cognitive_immunity': '认知免疫'}

# Figure 1: I vs W Scatter (Chinese)
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
for key, val in data.items():
    m = val.get('model', '')
    s = val.get('strategy', '')
    if m not in models: continue
    rs = val.get('round_scores', {})
    r1_scores = [scores[0] for scores in rs.values() if scores]
    I = sum(r1_scores) / len(r1_scores) if r1_scores else 0
    W = val['wq']
    ax.scatter(I, W, c=model_colors[m], marker=strat_markers[s], s=120, 
              edgecolors=GOLD, linewidth=0.8, zorder=5, alpha=0.9)
    if m == 'Qwen-Plus' and s == 'self_refine':
        ax.annotate('Qwen × 自我精炼\n（聪明但不智慧）', xy=(I, W),
                    xytext=(I-0.15, W-0.12), fontsize=8, color='#ff6b6b',
                    arrowprops=dict(arrowstyle='->', color='#ff6b6b', lw=1.2),
                    ha='center', fontweight='bold')
    elif m == 'Claude Opus' and s == 'reflexion':
        ax.annotate('Claude × 反思\n（最智慧）', xy=(I, W),
                    xytext=(I+0.12, W+0.06), fontsize=8, color='#6bff6b',
                    arrowprops=dict(arrowstyle='->', color='#6bff6b', lw=1.2),
                    ha='center', fontweight='bold')

ax.text(0.03, 0.97, 'ρ(I, W) = −0.279\nn = 12, p = 0.381', 
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        color=GOLD, fontfamily='monospace',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a2e', edgecolor=GOLD, alpha=0.8))
ax.plot([2.0, 2.7], [-0.3, 0.4], '--', color=GOLD, alpha=0.2, lw=1)
ax.axhline(y=0, color='#8b1a1a', alpha=0.4, lw=1, linestyle=':')
ax.text(2.62, -0.02, 'W = 0（无学习）', fontsize=7, color='#8b1a1a', alpha=0.5)
ax.set_xlabel('智能 I(m, s) — 第一轮平均分', fontsize=12, fontweight='bold')
ax.set_ylabel('智慧 W(m, s) — 智慧商数', fontsize=12, fontweight='bold')
ax.set_title('智能-智慧鸿沟', fontsize=16, fontweight='bold', color=GOLD, pad=15)
model_patches = [mpatches.Patch(color=model_colors[m], label=m) for m in models]
ax.legend(handles=model_patches, loc='lower left', framealpha=0.3, 
          edgecolor=GOLD, facecolor='#1a1a2e', fontsize=9)
ax.set_xlim(2.05, 2.7); ax.set_ylim(-0.3, 0.45)
plt.tight_layout()
plt.savefig(r'e:\order-architect-factory\papers\P3_intelligence_wisdom_gap\fig1_iw_scatter_zh.png', 
            dpi=300, facecolor=DARK, bbox_inches='tight')
plt.close()
print('Figure 1 (ZH) saved.')

# Figure 2: Tier Heatmap (Chinese)
tasks = sorted(set(t for val in data.values() for t in val.get('round_scores', {}).keys()))
def classify_best_tier(task, model):
    best = 0
    for val in data.values():
        if val.get('model') != model: continue
        scores = val.get('round_scores', {}).get(task, [])
        if not scores: continue
        ms = sum(scores)/len(scores)
        vs = sum((x-ms)**2 for x in scores)/len(scores)
        r1, rf = scores[0], scores[-1]
        if ms >= 2.5 and vs < 0.5: ti = 3
        elif r1 <= 1 and rf >= 2: ti = 2
        elif ms < 0.5: ti = 0
        else: ti = 1
        best = max(best, ti)
    return best

from matplotlib.colors import LinearSegmentedColormap
tier_matrix = np.zeros((len(tasks), len(models)))
for i, t in enumerate(tasks):
    for j, m in enumerate(models):
        tier_matrix[i, j] = classify_best_tier(t, m)

fig, ax = plt.subplots(1, 1, figsize=(6, 10))
cmap = LinearSegmentedColormap.from_list('tier', ['#4a1a1a', '#6b4a1a', '#1a4a6b', '#1a6b4a'], N=4)
ax.imshow(tier_matrix, cmap=cmap, aspect='auto', vmin=0, vmax=3)
ax.set_xticks(range(len(models)))
ax.set_xticklabels(['DeepSeek-V3', 'Qwen-Plus', 'Claude Opus'], fontsize=10, fontweight='bold')
ax.set_yticks(range(len(tasks)))
ax.set_yticklabels(tasks, fontsize=9)
tier_names_zh = ['参数级', '稳定', '潜在', '天花板']
for i in range(len(tasks)):
    for j in range(len(models)):
        ti = int(tier_matrix[i, j])
        tc = CREAM if ti < 2 else '#0a0a0f'
        ax.text(j, i, tier_names_zh[ti], ha='center', va='center', fontsize=7, color=tc, fontweight='bold')
for i, t in enumerate(tasks):
    tiers = set(int(tier_matrix[i, j]) for j in range(len(models)))
    if len(tiers) > 1:
        ax.add_patch(plt.Rectangle((-0.5, i-0.5), len(models), 1, lw=2, edgecolor=GOLD, facecolor='none'))
ax.set_title('失败层级基因型图谱\n（金色边框 = 跨模型分歧）', fontsize=13, fontweight='bold', color=GOLD, pad=12)
ax.set_xlabel('模型', fontsize=11, fontweight='bold')
legend_elements = [
    mpatches.Patch(facecolor='#4a1a1a', edgecolor=GOLD, label='参数级'),
    mpatches.Patch(facecolor='#6b4a1a', edgecolor=GOLD, label='稳定'),
    mpatches.Patch(facecolor='#1a4a6b', edgecolor=GOLD, label='潜在'),
    mpatches.Patch(facecolor='#1a6b4a', edgecolor=GOLD, label='天花板'),
]
ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.08),
          ncol=4, framealpha=0.3, edgecolor=GOLD, facecolor='#1a1a2e', fontsize=8)
plt.tight_layout()
plt.savefig(r'e:\order-architect-factory\papers\P3_intelligence_wisdom_gap\fig2_tier_heatmap_zh.png',
            dpi=300, facecolor=DARK, bbox_inches='tight')
plt.close()
print('Figure 2 (ZH) saved.')

# Figure 3: SAI (Chinese)
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
x_pos = np.arange(len(strategies))
width = 0.25
for i, m in enumerate(models):
    wq_vals = []
    for s in strategies:
        for val in data.values():
            if val.get('model') == m and val.get('strategy') == s:
                wq_vals.append(val['wq']); break
    bars = ax.bar(x_pos + i*width - width, wq_vals, width, label=m,
                  color=model_colors[m], edgecolor=GOLD, linewidth=0.5, alpha=0.85)
    for j, v in enumerate(wq_vals):
        if v < 0:
            ax.annotate(f'{v:.3f}', xy=(x_pos[j] + i*width - width, v),
                       xytext=(0, -15), textcoords='offset points',
                       ha='center', fontsize=8, color='#ff4444', fontweight='bold')
ax.axhline(y=0, color='#8b1a1a', alpha=0.5, lw=1.5)
ax.set_xticks(x_pos)
ax.set_xticklabels([strat_labels_zh[s] for s in strategies], fontsize=10)
ax.set_ylabel('智慧商数 (WQ)', fontsize=12, fontweight='bold')
ax.set_title('策略×模型交互效应\n（非可加性：同一策略对不同模型有帮助或有害）', 
             fontsize=13, fontweight='bold', color=GOLD, pad=12)
ax.legend(framealpha=0.3, edgecolor=GOLD, facecolor='#1a1a2e', fontsize=9)
ax.set_ylim(-0.3, 0.45)
plt.tight_layout()
plt.savefig(r'e:\order-architect-factory\papers\P3_intelligence_wisdom_gap\fig3_sai_interaction_zh.png',
            dpi=300, facecolor=DARK, bbox_inches='tight')
plt.close()
print('Figure 3 (ZH) saved.')
print('\nAll Chinese data figures done.')
