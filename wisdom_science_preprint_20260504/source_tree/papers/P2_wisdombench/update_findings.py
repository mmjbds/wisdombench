"""Final update: fill in Claude results to both P1 and P2 cross-model tables."""

# ─── P2 update ───
p2 = r'e:\order-architect-factory\papers\P2_wisdombench\main.tex'
with open(p2, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the cross-model table placeholder
old = r"""DeepSeek-V3 & Reflexion & 2.40 & 0.250 & 0.500 & 0/3 \\
Qwen-Plus   & Reflexion & \textbf{2.75} & \textbf{0.375} & \textbf{0.000} & \textbf{3/3} \\
Claude Opus & \multicolumn{4}{c}{\textit{(experiments in progress)}} & --- \\"""

new = r"""DeepSeek-V3 & Reflexion & 2.40 & 0.250 & 0.500 & 0/3 \\
Qwen-Plus   & Reflexion & \textbf{2.75} & \textbf{0.375} & \textbf{0.000} & \textbf{3/3} \\
Claude Opus & Reflexion & 2.60 & \textbf{0.375} & \textbf{0.000} & 3/3 \\"""

assert old in content, "P2 cross-model target not found!"
content = content.replace(old, new)
with open(p2, 'w', encoding='utf-8') as f:
    f.write(content)
print("P2 cross-model table updated with Claude data.")

# ─── P1 update ───
p1 = r'e:\order-architect-factory\papers\P1_cognitive_immunity\main.tex'
with open(p1, 'r', encoding='utf-8') as f:
    content = f.read()

# Update the note about Claude
old_note = r"\footnotesize{\textit{Note: Claude Opus results are being computed; table will be updated upon completion.}}"
new_note = r"\footnotesize{\textit{Note: All experiments completed. $N{=}1200$ total evaluations (3 models $\times$ 4 strategies $\times$ 20 tasks $\times$ 5 rounds).}}"
assert old_note in content, "P1 note target not found!"
content = content.replace(old_note, new_note)

# Add Claude rows to cross-model table
old_table = r"""DeepSeek & Immunity   & 2.25 & 0.133 & 0.500 & $0{\to}1{\to}1{\to}1{\to}1$ & 0/3 \\
DeepSeek & Reflexion  & 2.40 & 0.250 & 0.500 & $1{\to}2{\to}2{\to}2{\to}2$ & 0/3 \\
Qwen     & Immunity   & 2.45 & 0.143 & 1.000 & $0{\to}0{\to}0{\to}3{\to}0$ & 0/3 \\
Qwen     & Reflexion  & \textbf{2.75} & \textbf{0.375} & \textbf{0.000} & $0{\to}3{\to}3{\to}3{\to}3$ & \textbf{3/3} \\"""

new_table = r"""DeepSeek & Immunity   & 2.25 & 0.133 & 0.500 & $0{\to}1{\to}1{\to}1{\to}1$ & 0/3 \\
DeepSeek & Reflexion  & 2.40 & 0.250 & 0.500 & $1{\to}2{\to}2{\to}2{\to}2$ & 0/3 \\
Qwen     & Immunity   & 2.45 & 0.143 & 1.000 & $0{\to}0{\to}0{\to}3{\to}0$ & 0/3 \\
Qwen     & Reflexion  & \textbf{2.75} & \textbf{0.375} & \textbf{0.000} & $0{\to}3{\to}3{\to}3{\to}3$ & \textbf{3/3} \\
Claude   & Immunity   & 2.40 & 0.306 & \textbf{0.000} & $3{\to}1{\to}0{\to}3{\to}1$ & 1/3 \\
Claude   & Reflexion  & 2.60 & \textbf{0.375} & \textbf{0.000} & $3{\to}1{\to}3{\to}3{\to}3$ & 3/3 \\"""

assert old_table in content, "P1 cross-model table target not found!"
content = content.replace(old_table, new_table)

with open(p1, 'w', encoding='utf-8') as f:
    f.write(content)
print("P1 cross-model table and note updated with Claude data.")
print("All paper updates complete!")
