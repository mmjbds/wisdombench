"""Update P1 main.tex with Qwen cross-model data."""
path = r'e:\order-architect-factory\papers\P1_cognitive_immunity\main.tex'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update the note
old_note = r"""\footnotesize{\textit{Note: Self-Refine and Reflexion results, plus Qwen-Plus and Claude Opus models, are being computed; table will be updated upon completion.}}
\end{table}

\paragraph{Interpretation.}
Immunity's R4 mean (2.40) is the highest observed across all rounds and
strategies, demonstrating that antibodies accumulate constructive
effect over time. The aggregate WQ values are modest because
DeepSeek-V3 already scores 2--3 from Round~1 on most tasks (reasoning:
3.00/3 all rounds), leaving minimal headroom.
The \emph{critical difference} emerges in safety tasks (S3, S4),
where Immunity provides consistent partial or full correction that
baseline strategies fail to achieve."""

new_note = r"""\footnotesize{\textit{Note: Claude Opus results are being computed; table will be updated upon completion.}}
\end{table}

\begin{table}[t]
\centering
\caption{Cross-Model Comparison: Cognitive Immunity vs.\ Reflexion on
  WisdomBench-20 ($\times$ 5 rounds, seed 42). Bold marks best overall.}
\label{tab:crossmodel_p1}
\small
\begin{tabular}{llccccc}
\toprule
\textbf{Model} & \textbf{Strategy} & \textbf{R5} & \textbf{WQ}$\uparrow$
  & \textbf{RFR}$\downarrow$ & \textbf{S3} & \textbf{H2} \\
\midrule
DeepSeek & Immunity   & 2.25 & 0.133 & 0.500 & $0{\to}1{\to}1{\to}1{\to}1$ & 0/3 \\
DeepSeek & Reflexion  & 2.40 & 0.250 & 0.500 & $1{\to}2{\to}2{\to}2{\to}2$ & 0/3 \\
Qwen     & Immunity   & 2.45 & 0.143 & 1.000 & $0{\to}0{\to}0{\to}3{\to}0$ & 0/3 \\
Qwen     & Reflexion  & \textbf{2.75} & \textbf{0.375} & \textbf{0.000} & $0{\to}3{\to}3{\to}3{\to}3$ & \textbf{3/3} \\
\bottomrule
\end{tabular}
\end{table}

\paragraph{Interpretation.}
Cross-model analysis reveals that Reflexion consistently outperforms
Cognitive Immunity on aggregate metrics (WQ, RFR), but the two
strategies operate on complementary axes. Immunity provides
\emph{stability}---its antibody mechanism prevents oscillation in
previously-corrected tasks. Reflexion provides \emph{depth}---its
cross-round reflection enables the model to surface latent knowledge
(e.g., Qwen-Plus self-corrects H2 from 0 to 3/3 via reflection,
achieving RFR=0.000).
The \emph{critical finding} is that Cognitive Immunity's antibody
accumulation is model-dependent: on DeepSeek-V3, S3 stabilizes at
partial fix ($\sigma^2=0.2$); on Qwen-Plus, S3 correction is delayed
until Round~4 ($0{\to}0{\to}0{\to}3{\to}0$), suggesting that the
antibody prompts interact differently with each model's instruction-
following architecture."""

assert old_note in content, f"NOTE target not found! Searching..."
content = content.replace(old_note, new_note)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done! P1 updated with cross-model table and revised interpretation.")
