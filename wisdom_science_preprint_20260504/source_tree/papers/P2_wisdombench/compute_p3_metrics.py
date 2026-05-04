"""
P3 Design: Compute all metrics for the unified paper.
Core thesis: Failure is a property of (task, model, strategy) triple, not task alone.
"""
import json, math

with open(r'e:\order-architect-factory\papers\P2_wisdombench\results\summary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

models = ['DeepSeek-V3', 'Qwen-Plus', 'Claude Opus']
strategies = ['no_memory', 'self_refine', 'reflexion', 'cognitive_immunity']

# ══════════════════════════════════════════════════════════════
# 1. BUILD THE FULL TASK × MODEL × STRATEGY TENSOR
# ══════════════════════════════════════════════════════════════
tasks = set()
for val in data.values():
    tasks.update(val.get('round_scores', {}).keys())
tasks = sorted(tasks)

# tensor[task][model][strategy] = [r1, r2, r3, r4, r5]
tensor = {}
for task in tasks:
    tensor[task] = {}
    for val in data.values():
        m = val['model']
        s = val['strategy']
        scores = val.get('round_scores', {}).get(task, [])
        if m not in tensor[task]:
            tensor[task][m] = {}
        tensor[task][m][s] = scores

# ══════════════════════════════════════════════════════════════
# 2. FAILURE GENOTYPE CLASSIFICATION
# ══════════════════════════════════════════════════════════════
print("=" * 70)
print("FAILURE GENOTYPE MAP (task × model → tier)")
print("=" * 70)

def classify_tier(scores):
    """Classify a score trajectory into a failure tier."""
    if not scores:
        return "UNKNOWN", {}
    mean_s = sum(scores) / len(scores)
    var_s = sum((x - mean_s)**2 for x in scores) / len(scores)
    r1 = scores[0]
    r_final = scores[-1]
    improved = r_final > r1
    
    # Tier classification
    if mean_s >= 2.5 and var_s < 0.5:
        return "CEILING", {"mean": mean_s, "var": var_s}
    elif mean_s < 0.5 and var_s < 0.5:
        return "PARAMETRIC", {"mean": mean_s, "var": var_s}
    elif r1 <= 1 and r_final >= 2:
        return "LATENT", {"mean": mean_s, "var": var_s, "recovery": f"{r1}->{r_final}"}
    elif r1 >= 2 and r_final <= 1:
        return "DEGRADING", {"mean": mean_s, "var": var_s, "degradation": f"{r1}->{r_final}"}
    elif var_s >= 0.8:
        return "OSCILLATING", {"mean": mean_s, "var": var_s}
    else:
        return "STABLE", {"mean": mean_s, "var": var_s}

# Genotype map: for each task, what tier does it have on each model (best strategy)
print("\nTask-Level Genotype (using BEST strategy per model):\n")
genotype_map = {}
for task in tasks:
    genotype_map[task] = {}
    row = f"  {task}: "
    for m in models:
        best_tier = "PARAMETRIC"
        best_mean = 0
        for s in strategies:
            scores = tensor[task].get(m, {}).get(s, [])
            if scores:
                tier, info = classify_tier(scores)
                mean_s = info.get("mean", 0)
                # Hierarchy: CEILING > LATENT > STABLE > OSCILLATING > DEGRADING > PARAMETRIC
                tier_order = {"CEILING": 6, "LATENT": 5, "STABLE": 4, "OSCILLATING": 3, "DEGRADING": 2, "PARAMETRIC": 1, "UNKNOWN": 0}
                if tier_order.get(tier, 0) > tier_order.get(best_tier, 0):
                    best_tier = tier
                    best_mean = mean_s
                elif tier_order.get(tier, 0) == tier_order.get(best_tier, 0) and mean_s > best_mean:
                    best_mean = mean_s
        genotype_map[task][m] = best_tier
        row += f"  {m[:8]:>8s}={best_tier:>11s}"
    print(row)

# ══════════════════════════════════════════════════════════════
# 3. CROSS-MODEL DIVERGENCE SCORE  
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CROSS-MODEL DIVERGENCE (tasks where tier differs across models)")
print("=" * 70 + "\n")

divergent_tasks = []
for task in tasks:
    tiers = set(genotype_map[task].values())
    if len(tiers) > 1:
        divergent_tasks.append(task)
        print(f"  {task}: {dict((m[:8], genotype_map[task][m]) for m in models)}")

print(f"\n  Divergent tasks: {len(divergent_tasks)}/{len(tasks)} ({100*len(divergent_tasks)/len(tasks):.0f}%)")
print(f"  Uniform tasks: {len(tasks)-len(divergent_tasks)}/{len(tasks)}")

# ══════════════════════════════════════════════════════════════
# 4. STRATEGY EFFICACY CONDITIONED ON TIER
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STRATEGY EFFICACY BY FAILURE TIER")
print("=" * 70 + "\n")

# For each (task, model) pair classified by tier, what's the best strategy?
tier_strategy_wins = {}  # tier -> {strategy: count}
for task in tasks:
    for m in models:
        # Get baseline tier (no_memory)
        baseline_scores = tensor[task].get(m, {}).get('no_memory', [])
        if not baseline_scores:
            continue
        baseline_tier, _ = classify_tier(baseline_scores)
        
        # Find best strategy
        best_wq = -999
        best_strat = 'no_memory'
        for s in strategies:
            scores = tensor[task].get(m, {}).get(s, [])
            if scores and len(scores) >= 2:
                wq = (scores[-1] - scores[0]) / (3 * (len(scores) - 1)) if scores[0] < 3 else 0
                if wq > best_wq:
                    best_wq = wq
                    best_strat = s
        
        if baseline_tier not in tier_strategy_wins:
            tier_strategy_wins[baseline_tier] = {}
        if best_strat not in tier_strategy_wins[baseline_tier]:
            tier_strategy_wins[baseline_tier][best_strat] = 0
        tier_strategy_wins[baseline_tier][best_strat] += 1

for tier in sorted(tier_strategy_wins.keys()):
    total = sum(tier_strategy_wins[tier].values())
    print(f"  {tier}:")
    for s in sorted(tier_strategy_wins[tier].keys(), key=lambda x: -tier_strategy_wins[tier][x]):
        count = tier_strategy_wins[tier][s]
        print(f"    {s:20s}: {count:2d}/{total} ({100*count/total:.0f}%)")

# ══════════════════════════════════════════════════════════════
# 5. PROBE PROTOCOL DESIGN  
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PROBE PROTOCOL: Minimum diagnostic task set")
print("=" * 70 + "\n")

# Find tasks with MAXIMUM cross-model divergence AND cross-strategy divergence
for task in tasks:
    model_tiers = set()
    strategy_spread = 0
    for m in models:
        tiers_per_model = set()
        for s in strategies:
            scores = tensor[task].get(m, {}).get(s, [])
            if scores:
                tier, _ = classify_tier(scores)
                tiers_per_model.add(tier)
                model_tiers.add(tier)
        strategy_spread += len(tiers_per_model)
    
    model_divergence = len(model_tiers)
    diagnostic_power = model_divergence * strategy_spread
    
    if model_divergence >= 3:
        print(f"  {task}: model_div={model_divergence} strat_spread={strategy_spread} DIAG_POWER={diagnostic_power} *** EXCELLENT PROBE")
    elif model_divergence >= 2:
        print(f"  {task}: model_div={model_divergence} strat_spread={strategy_spread} DIAG_POWER={diagnostic_power}")

# ══════════════════════════════════════════════════════════════
# 6. KEY NUMBERS FOR THE PAPER
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("KEY NUMBERS FOR PAPER")
print("=" * 70 + "\n")

# Total unique (task, model, strategy) triples
total_triples = sum(1 for t in tasks for m in models for s in strategies 
                    if tensor[t].get(m, {}).get(s))
print(f"  Total (task, model, strategy) triples: {total_triples}")
print(f"  Total individual judgments: {total_triples * 5} (x5 rounds)")
print(f"  Tasks: {len(tasks)}")
print(f"  Models: {len(models)}")
print(f"  Strategies: {len(strategies)}")
print(f"  Cross-model divergent tasks: {len(divergent_tasks)}/{len(tasks)}")

# Strategy x Model interaction non-additivity
wq_matrix = {}
for val in data.values():
    wq_matrix[(val['model'], val['strategy'])] = val['wq']

total_interaction = 0
count_interaction = 0
max_interaction = 0
max_pair = ""
for m in models:
    for s in strategies:
        wq = wq_matrix.get((m, s), 0)
        grand = sum(wq_matrix.values()) / len(wq_matrix)
        m_mean = sum(wq_matrix.get((m, ss), 0) for ss in strategies) / len(strategies)
        s_mean = sum(wq_matrix.get((mm, s), 0) for mm in models) / len(models)
        predicted = grand + (m_mean - grand) + (s_mean - grand)
        interaction = abs(wq - predicted)
        total_interaction += interaction
        count_interaction += 1
        if interaction > max_interaction:
            max_interaction = interaction
            max_pair = f"{m} x {s}"

print(f"  Mean |interaction|: {total_interaction/count_interaction:.3f}")
print(f"  Max |interaction|: {max_interaction:.3f} ({max_pair})")
print(f"  Qwen x Self-Refine WQ: {wq_matrix.get(('Qwen-Plus', 'self_refine'), 'N/A')}")
print(f"  Reflexion universal best: WQ={wq_matrix.get(('Qwen-Plus', 'reflexion'), 0):.3f} (Qwen) / {wq_matrix.get(('Claude Opus', 'reflexion'), 0):.3f} (Claude)")
