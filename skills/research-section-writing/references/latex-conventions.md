# LaTeX conventions

## Tables

```latex
\begin{table}[t]
\centering
\caption{Main results on both datasets. Best values in bold.}
\label{tab:main}
\small
\begin{tabular}{lcc}
\toprule
Method & Dataset A & Dataset B \\
\midrule
Baseline & 71.2 & 68.9 \\
Ours & \textbf{74.8} & \textbf{72.1} \\
\bottomrule
\end{tabular}
\end{table}
```

- One table per concept. Do not cram unrelated results into one grid.
- Units in the header, not in every cell.
- Bold the best value only when the comparison is fair and the log supports it.
- Use `\small` or `\footnotesize` before switching to `tabularx`; try the simpler fix first.
- Reference the table in the text: `Table~\ref{tab:main}`.

## Figures

```latex
\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{figures/fig_main_results.pdf}
\caption{Comparison on both datasets. Error bars show one standard deviation over three seeds.}
\label{fig:main}
\end{figure}
```

- Wide figure in a two-column venue:

```latex
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/fig_architecture.pdf}
\caption{Overview of the pipeline.}
\label{fig:arch}
\end{figure*}
```

- Do not set both `width` and `height` unless preserving an exact size is required.
- Do not use `\subfloat` to merge figures the authors intended as separate.
- Put the caption below figures and above tables (standard in ML venues).

## Citations

- Numeric venues: `\cite{key}`.
- `natbib` venues: `\citep{key}` for parenthetical, `\citet{key}` for narrative.
- Multiple keys: `\cite{a,b,c}`.
- Never cite a key that is absent from `citation_map.json`.
- Never cite a paper as a baseline unless it appears in `experimental_log.md`.

## Math

- Define every symbol at first use.
- Use `\begin{equation}` with `\label{eq:...}` for numbered equations and `\eqref{eq:...}` to refer to them.
- Use `\mathbb{E}` for expectation, `\mathcal{L}` for losses, and keep notation consistent across sections.
- Do not introduce a theorem environment the template does not define.

## Sections and references

- Use `\section`, `\subsection`, `\subsubsection` in that order; do not skip levels.
- Labels: `sec:method`, `fig:main`, `tab:main`, `eq:loss`, `app:details`.
- Refer with `Section~\ref{sec:method}` (or `\Cref` when `cleveref` is loaded).
- Do not create orphan subsections: a single `\subsection` under a section usually means it should be body text.

## Appendix

```latex
\appendix
\section{Additional Results}
\label{app:results}
```

- Place after `\bibliography{...}` when the venue requires it.
- Use the same table and figure conventions.
- Do not put new claims in the appendix that the main text does not support.
