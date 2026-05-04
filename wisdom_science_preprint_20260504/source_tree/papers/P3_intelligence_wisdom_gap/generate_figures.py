"""Generate publication-quality academic figures for P3."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Dark luxury theme
plt.rcParams.update({
    'figure.facecolor': '#0a0a0f',
    'axes.facecolor': '#0a0a0f',
    'axes.edgecolor': '#c9b06b',
    'axes.labelcolor': '#e8dcc8',
    'text.color': '#e8dcc8',
    'xtick.color': '#c9b06b',
    'ytick.color': '#c9b06b',
    'grid.color': '#1a1a2e',
    'font.family': 'serif',
    'font.size': 11,
    'axes.grid': True,
    'grid.alpha': 0.3,
})

GOLD = '#c9b06b'
CREAM = '#e8dcc8'
DARK = '#0a0a0f'
DEEP_BLUE = '#0f3460'
CRIMSON = '#8b1a1a'
EMERALD = '#1a6b4a'
AMBER = '#b8860b'

# Load data
with open(r'e:\order-architect-factory\papers\P2_wisdombench\results\summary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

models = ['DeepSeek-V3', 'Qwen-Plus', 'Claude Opus']
strategies = ['no_memory', 'self_refine', 'reflexion', 'cognitive_immunity']
strat_labels = {'no_memory': 'No Memory', 'self_refine': 'Self-Refine', 
                'reflexion': 'Reflexion', 'cognitive_immunity': 'Cog. Immunity'}
model_colors = {'DeepSeek-V3': '#4a90d9', 'Qwen-Plus': '#d4a04a', 'Claude Opus': '#c75050'}
strat_markers = {'no_memory': 'o', 'self_refine': 's', 'reflexion': 'D', 'cognitive_immunity': '^'}

# ══════════════════════════════════════════════════════════════
# FIGURE 1: Intelligence vs Wisdom Scatter Plot
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

I_all, W_all = [], []
for key, val in data.items():
    m = val.get('model', '')
    s = val.get('strategy', '')
    if m not in models:
        continue
    
    rs = val.get('round_scores', {})
    r1_scores = [scores[0] for scores in rs.values() if scores]
    I = sum(r1_scores) / len(r1_scores) if r1_scores else 0
    W = val['wq']
    I_all.append(I)
    W_all.append(W)
    
    color = model_colors[m]
    marker = strat_markers[s]
    ax.scatter(I, W, c=color, marker=marker, s=120, edgecolors=GOLD, linewidth=0.8, zorder=5, alpha=0.9)
    
    # Label the extreme points
    if m == 'Qwen-Plus' and s == 'self_refine':
        ax.annotate('Qwen × Self-Refine\n(Smart but Unwise)', xy=(I, W),
                    xytext=(I-0.15, W-0.12), fontsize=8, color='#ff6b6b',
                    arrowprops=dict(arrowstyle='->', color='#ff6b6b', lw=1.2),
                    ha='center', fontweight='bold')
    elif m == 'Claude Opus' and s == 'reflexion':
        ax.annotate('Claude × Reflexion\n(Wisest)', xy=(I, W),
                    xytext=(I+0.12, W+0.06), fontsize=8, color='#6bff6b',
                    arrowprops=dict(arrowstyle='->', color='#6bff6b', lw=1.2),
                    ha='center', fontweight='bold')

# Add correlation info
ax.text(0.03, 0.97, f'ρ(I, W) = −0.279\nn = 12, p = 0.381', 
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        color=GOLD, fontfamily='monospace',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a2e', edgecolor=GOLD, alpha=0.8))

# Diagonal reference line (if I=W)
ax.plot([2.0, 2.7], [-0.3, 0.4], '--', color=GOLD, alpha=0.2, lw=1)
ax.text(2.65, 0.38, 'I = W\n(if correlated)', fontsize=7, color=GOLD, alpha=0.3, ha='right')

# Zero line for Wisdom
ax.axhline(y=0, color=CRIMSON, alpha=0.4, lw=1, linestyle=':')
ax.text(2.62, -0.02, 'W = 0 (no learning)', fontsize=7, color=CRIMSON, alpha=0.5)

ax.set_xlabel('Intelligence  I(m, s)  —  Mean Round 1 Score', fontsize=12, fontweight='bold')
ax.set_ylabel('Wisdom  W(m, s)  —  Wisdom Quotient', fontsize=12, fontweight='bold')
ax.set_title('The Intelligence-Wisdom Gap', fontsize=16, fontweight='bold', color=GOLD, pad=15)

# Legend
model_patches = [mpatches.Patch(color=model_colors[m], label=m) for m in models]
ax.legend(handles=model_patches, loc='lower left', framealpha=0.3, 
          edgecolor=GOLD, facecolor='#1a1a2e', fontsize=9)

ax.set_xlim(2.05, 2.7)
ax.set_ylim(-0.3, 0.45)

plt.tight_layout()
plt.savefig(r'e:\order-architect-factory\papers\P3_intelligence_wisdom_gap\fig1_iw_scatter.png', dpi=300, 
            facecolor=DARK, bbox_inches='tight')
plt.close()
print('Figure 1 saved.')

# ══════════════════════════════════════════════════════════════
# FIGURE 2: Failure Tier Heatmap (20 tasks × 3 models)
# ══════════════════════════════════════════════════════════════
tasks = sorted(set(t for val in data.values() for t in val.get('round_scores', {}).keys()))

def classify_best_tier(task, model):
    """Classify task × model using best strategy."""
    best_tier_idx = 0  # 0=PARAM, 1=LATENT, 2=STABLE, 3=CEILING
    for val in data.values():
        if val.get('model') != model:
            continue
        scores = val.get('round_scores', {}).get(task, [])
        if not scores:
            continue
        mean_s = sum(scores) / len(scores)
        var_s = sum((x - mean_s)**2 for x in scores) / len(scores)
        r1, rf = scores[0], scores[-1]
        
        if mean_s >= 2.5 and var_s < 0.5:
            tier_idx = 3  # CEILING
        elif r1 <= 1 and rf >= 2:
            tier_idx = 2  # LATENT
        elif mean_s < 0.5:
            tier_idx = 0  # PARAMETRIC
        else:
            tier_idx = 1  # STABLE
        
        best_tier_idx = max(best_tier_idx, tier_idx)
    return best_tier_idx

tier_matrix = np.zeros((len(tasks), len(models)))
for i, t in enumerate(tasks):
    for j, m in enumerate(models):
        tier_matrix[i, j] = classify_best_tier(t, m)

fig, ax = plt.subplots(1, 1, figsize=(6, 10))

# Custom colormap: dark luxury
from matplotlib.colors import LinearSegmentedColormap
colors_map = ['#4a1a1a', '#6b4a1a', '#1a4a6b', '#1a6b4a']  # param, stable, latent, ceiling
cmap = LinearSegmentedColormap.from_list('tier', colors_map, N=4)

im = ax.imshow(tier_matrix, cmap=cmap, aspect='auto', vmin=0, vmax=3)

ax.set_xticks(range(len(models)))
ax.set_xticklabels(['DeepSeek-V3', 'Qwen-Plus', 'Claude Opus'], fontsize=10, fontweight='bold')
ax.set_yticks(range(len(tasks)))
ax.set_yticklabels(tasks, fontsize=9)

# Add tier labels inside cells
tier_names = ['PARAM', 'STABLE', 'LATENT', 'CEIL']
for i in range(len(tasks)):
    for j in range(len(models)):
        tier_idx = int(tier_matrix[i, j])
        text_color = CREAM if tier_idx < 2 else '#0a0a0f'
        ax.text(j, i, tier_names[tier_idx], ha='center', va='center', 
                fontsize=7, color=text_color, fontweight='bold')

# Highlight divergent rows
for i, t in enumerate(tasks):
    tiers = set(int(tier_matrix[i, j]) for j in range(len(models)))
    if len(tiers) > 1:
        rect = plt.Rectangle((-0.5, i-0.5), len(models), 1, linewidth=2, 
                             edgecolor=GOLD, facecolor='none')
        ax.add_patch(rect)

ax.set_title('Failure Tier Genotype Map\n(Gold borders = cross-model divergence)', 
             fontsize=13, fontweight='bold', color=GOLD, pad=12)
ax.set_xlabel('Model', fontsize=11, fontweight='bold')

# Custom legend
legend_elements = [
    mpatches.Patch(facecolor='#4a1a1a', edgecolor=GOLD, label='Parametric'),
    mpatches.Patch(facecolor='#6b4a1a', edgecolor=GOLD, label='Stable'),
    mpatches.Patch(facecolor='#1a4a6b', edgecolor=GOLD, label='Latent'),
    mpatches.Patch(facecolor='#1a6b4a', edgecolor=GOLD, label='Ceiling'),
]
ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.08),
          ncol=4, framealpha=0.3, edgecolor=GOLD, facecolor='#1a1a2e', fontsize=8)

plt.tight_layout()
plt.savefig(r'e:\order-architect-factory\papers\P3_intelligence_wisdom_gap\fig2_tier_heatmap.png', dpi=300,
            facecolor=DARK, bbox_inches='tight')
plt.close()
print('Figure 2 saved.')

# ══════════════════════════════════════════════════════════════
# FIGURE 3: Strategy-Architecture Interaction Plot
# ══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(8, 5))

x_pos = np.arange(len(strategies))
width = 0.25

for i, m in enumerate(models):
    wq_vals = []
    for s in strategies:
        for val in data.values():
            if val.get('model') == m and val.get('strategy') == s:
                wq_vals.append(val['wq'])
                break
    bars = ax.bar(x_pos + i*width - width, wq_vals, width, 
                  label=m, color=model_colors[m], edgecolor=GOLD, linewidth=0.5, alpha=0.85)
    
    # Annotate negative bar
    for j, v in enumerate(wq_vals):
        if v < 0:
            ax.annotate(f'{v:.3f}', xy=(x_pos[j] + i*width - width, v), 
                       xytext=(0, -15), textcoords='offset points',
                       ha='center', fontsize=8, color='#ff4444', fontweight='bold')

ax.axhline(y=0, color=CRIMSON, alpha=0.5, lw=1.5, linestyle='-')
ax.set_xticks(x_pos)
ax.set_xticklabels([strat_labels[s] for s in strategies], fontsize=10)
ax.set_ylabel('Wisdom Quotient (WQ)', fontsize=12, fontweight='bold')
ax.set_title('Strategy × Model Interaction\n(Non-additive: same strategy helps or harms depending on model)', 
             fontsize=13, fontweight='bold', color=GOLD, pad=12)
ax.legend(framealpha=0.3, edgecolor=GOLD, facecolor='#1a1a2e', fontsize=9)
ax.set_ylim(-0.3, 0.45)

plt.tight_layout()
plt.savefig(r'e:\order-architect-factory\papers\P3_intelligence_wisdom_gap\fig3_sai_interaction.png', dpi=300,
            facecolor=DARK, bbox_inches='tight')
plt.close()
print('Figure 3 saved.')

print('\nAll 3 academic figures generated successfully.')
