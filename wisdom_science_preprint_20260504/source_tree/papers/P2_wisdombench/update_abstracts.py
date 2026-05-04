"""Update P2 abstract with final 3-model findings."""
p2 = r'e:\order-architect-factory\papers\P2_wisdombench\main.tex'
with open(p2, 'r', encoding='utf-8') as f:
    c = f.read()

old = """Baseline evaluation across \\textbf{three frontier models}
(DeepSeek-V3, Qwen-Plus, Claude Opus) with 4 learning strategies
reveals that standard LLMs exhibit \\emph{systematic blind spots}:
DeepSeek-V3 provides an incorrect Nvidia founding date across all 5
rounds ($0\\to0\\to0\\to0\\to0$) regardless of strategy, and
oscillates on PII redaction ($0\\to1\\to1\\to0\\to1$) under
No Memory. Cognitive Immunity---a bio-inspired failure learning
mechanism---stabilizes the PII trajectory ($0\\to1\\to1\\to1\\to1$)
and achieves $3\\times$ Safety WQ improvement ($0.111 \\to 0.333$),
while reasoning scores remain at ceiling ($3.00/3$ all rounds).
This confirms that \\emph{intelligence and wisdom are orthogonal capabilities}."""

new = """Large-scale evaluation across \\textbf{three frontier models}
(DeepSeek-V3, Qwen-Plus, Claude Opus) with 4 learning strategies
($N{=}1{,}200$ evaluations) reveals that standard LLMs exhibit
\\emph{systematic blind spots}: DeepSeek-V3 provides an incorrect
Nvidia founding date across all 5 rounds regardless of strategy
(parametric failure), while Qwen-Plus self-corrects the same error
via Reflexion ($0{\\to}3{\\to}3{\\to}3{\\to}3$, latent knowledge
surfacing). Reflexion achieves the best Wisdom Quotient
(WQ$=$0.375) with zero failure recurrence (RFR$=$0.000) on both
Qwen-Plus and Claude Opus, establishing a \\emph{three-tier failure
taxonomy}: correctable, latent, and parametric.
This confirms that \\emph{intelligence and wisdom are orthogonal
capabilities}, and that intervention strategy choice critically
depends on failure tier."""

assert old in c, "P2 abstract target not found!"
c = c.replace(old, new)
with open(p2, 'w', encoding='utf-8') as f:
    f.write(c)
print("P2 abstract updated with final 3-model findings!")
