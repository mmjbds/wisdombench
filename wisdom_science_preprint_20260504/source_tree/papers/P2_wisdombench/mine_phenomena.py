"""Deep phenomenon mining from summary.json — hunting for novel patterns."""
import json, math

with open(r'e:\order-architect-factory\papers\P2_wisdombench\results\summary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("PHENOMENON 1: Strategy x Model Non-Additivity")
print("=" * 70)
# If effects were additive: WQ(model,strategy) = model_effect + strategy_effect
# Non-additivity = interaction_term = observed - predicted_additive
models = ['DeepSeek-V3', 'Qwen-Plus', 'Claude Opus']
strategies = ['no_memory', 'self_refine', 'reflexion', 'cognitive_immunity']
wq_matrix = {}
for key, val in data.items():
    m = val['model']
    s = val['strategy']
    wq_matrix[(m, s)] = val['wq']

# Compute model and strategy main effects
model_means = {}
for m in models:
    vals = [wq_matrix.get((m, s), 0) for s in strategies]
    model_means[m] = sum(vals) / len(vals)

strat_means = {}
for s in strategies:
    vals = [wq_matrix.get((m, s), 0) for m in models]
    strat_means[s] = sum(vals) / len(vals)

grand_mean = sum(wq_matrix.values()) / len(wq_matrix)

print(f"\nGrand mean WQ: {grand_mean:.3f}")
print(f"\nModel effects:")
for m in models:
    print(f"  {m:15s}: mean={model_means[m]:.3f}  effect={model_means[m]-grand_mean:+.3f}")
print(f"\nStrategy effects:")
for s in strategies:
    print(f"  {s:20s}: mean={strat_means[s]:.3f}  effect={strat_means[s]-grand_mean:+.3f}")

print(f"\nInteraction terms (RESIDUALS — non-additive synergy/antagonism):")
for m in models:
    for s in strategies:
        observed = wq_matrix.get((m, s), 0)
        predicted = grand_mean + (model_means[m] - grand_mean) + (strat_means[s] - grand_mean)
        interaction = observed - predicted
        tag = ""
        if abs(interaction) > 0.1:
            tag = " **STRONG"
        if abs(interaction) > 0.15:
            tag = " ***VERY STRONG"
        print(f"  {m:15s} x {s:20s}: obs={observed:+.3f}  pred={predicted:+.3f}  I={interaction:+.3f}{tag}")

print("\n" + "=" * 70)
print("PHENOMENON 2: Per-Task Tier Classification")
print("=" * 70)
# Classify each task across ALL model x strategy combos
tasks = set()
for val in data.values():
    tasks.update(val.get('round_scores', {}).keys())

for task in sorted(tasks):
    scores_across = []
    details = []
    for key, val in data.items():
        rs = val.get('round_scores', {}).get(task, [])
        if rs:
            r1 = rs[0]
            r5 = rs[-1] if len(rs) >= 5 else rs[-1]
            improved = r5 > r1
            scores_across.append((val['model'], val['strategy'], rs, improved))
            details.append(rs)

    if scores_across:
        mean_r1 = sum(d[0] for d in details) / len(details)
        mean_final = sum(d[-1] for d in details) / len(details)
        variance = sum((d[-1] - mean_final)**2 for d in details) / len(details)
        ever_zero = any(d[0] == 0 for d in details)
        ever_perfect = any(d[-1] == 3 for d in details)
        always_perfect = all(d[-1] >= 2 for d in details)

        # Classify
        if always_perfect and mean_r1 >= 2:
            tier = "DARK_MATTER (ceiling)"
        elif mean_final < 1 and not ever_perfect:
            tier = "PARAMETRIC (floor)"
        elif ever_zero and ever_perfect:
            tier = "***LATENT (model-dependent)"
        elif variance > 1.0:
            tier = "VOLATILE"
        else:
            tier = "MIXED"

        print(f"  {task}: R1_mean={mean_r1:.1f} Rfinal_mean={mean_final:.1f} var={variance:.2f} -> {tier}")

print("\n" + "=" * 70)
print("PHENOMENON 3: Pharmacological Metrics")
print("=" * 70)
for key, val in sorted(data.items()):
    m = val['model']
    s = val['strategy']
    wq = val['wq']
    rs = val.get('round_scores', {})
    
    # Compute round means (average across all tasks per round)
    round_count = 5
    round_means = []
    for r in range(round_count):
        scores = []
        for task, task_scores in rs.items():
            if len(task_scores) > r:
                scores.append(task_scores[r])
        if scores:
            round_means.append(sum(scores) / len(scores))
    
    if len(round_means) >= 5:
        r1 = round_means[0]
        r5 = round_means[4]
        peak = max(round_means)
        trough = min(round_means)
        
        # ED50: first round to reach 50% of max improvement
        if peak > r1:
            target = r1 + (peak - r1) * 0.5
            ed50 = next((i+1 for i, v in enumerate(round_means) if v >= target), 'N/A')
        else:
            ed50 = 'N/A'
        
        # Therapeutic index = efficacy / side_effects
        efficacy = max(0, r5 - r1)
        volatility = math.sqrt(sum((x-sum(round_means)/len(round_means))**2 for x in round_means)/len(round_means))
        
        # Decay detection
        if r5 < r1 - 0.1:
            profile = "DETERIORATING"
        elif peak > r5 + 0.15:
            profile = "PEAK-THEN-FADE"
        elif r5 > r1 + 0.1:
            profile = "IMPROVING"
        else:
            profile = "STABLE"
        
        print(f"  {m:15s} x {s:20s}: R1={r1:.2f} R5={r5:.2f} peak={peak:.2f} ED50={ed50} vol={volatility:.3f} [{profile}]")

print("\n" + "=" * 70)
print("PHENOMENON 4: Epistemic Temperature Calculation")
print("=" * 70)
# For each task x model: compute behavioral variance / mean score
# High ratio = behavioral noise dominates = correctable
# Low ratio = parametric error dominates = uncorrectable
for task in sorted(tasks):
    print(f"\n  {task}:")
    for key, val in sorted(data.items()):
        rs = val.get('round_scores', {}).get(task, [])
        if rs and len(rs) >= 5:
            mean_s = sum(rs) / len(rs)
            var_s = sum((x - mean_s)**2 for x in rs) / len(rs)
            if mean_s > 0:
                T_e = var_s / mean_s  # epistemic temperature
            else:
                T_e = var_s / 0.01 if var_s > 0 else 0
            
            tier = "???"
            if mean_s >= 2.5 and var_s < 0.3:
                tier = "DARK_MATTER"
            elif mean_s < 0.5 and var_s < 0.3:
                tier = "PARAMETRIC"
            elif T_e > 0.5:
                tier = "CORRECTABLE"
            elif 0.1 < T_e <= 0.5:
                tier = "LATENT"
            else:
                tier = "STABLE"
            
            m = val['model']
            s = val['strategy']
            print(f"    {m:15s} x {s:20s}: mean={mean_s:.1f} var={var_s:.2f} T_e={T_e:.3f} [{tier}]")
