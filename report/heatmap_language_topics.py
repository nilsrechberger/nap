import pandas as pd
import ast
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os


# ── 1. Load & parse ──────────────────────────────────────────────────────────
try:
    BASE_DIR = BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    BASE_DIR = os.getcwd()

df = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "merged data.csv"))

df["category_list"] = df["category"].apply(
    lambda x: ast.literal_eval(x) if pd.notna(x) else []
)
df_exp = df.explode("category_list")
df_exp = df_exp[df_exp["category_list"] != "top"]          # 'top' is a flag, not a topic
df_exp["cat"] = df_exp["category_list"].str.strip().str.lower()

# ── 2. Filter ─────────────────────────────────────────────────────────────────
MAIN_CATS = ["lifestyle", "sports", "business", "entertainment",
             "technology", "world", "politics","crime"]

lang_counts = df["language"].value_counts()
valid_langs = lang_counts[lang_counts >= 5].index.tolist()

df_filt = df_exp[
    df_exp["language"].isin(valid_langs) &
    df_exp["cat"].isin(MAIN_CATS)
]

# ── 3. Build normalized pivot (% per language) ────────────────────────────────
pivot = df_filt.groupby(["language", "cat"]).size().unstack(fill_value=0)
for c in MAIN_CATS:                                        # ensure column order
    if c not in pivot.columns:
        pivot[c] = 0
pivot = pivot[MAIN_CATS]

pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

# Sort languages by dominant category (lifestyle share, ascending)
pivot_pct = pivot_pct.sort_values("lifestyle", ascending=True)

# ── 4. Figure layout ──────────────────────────────────────────────────────────
N_LANGS = len(pivot_pct)
N_CATS  = len(MAIN_CATS)

fig, ax = plt.subplots(figsize=(13, 9))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ── 5. Colour scale ───────────────────────────────────────────────────────────
from matplotlib.colors import LinearSegmentedColormap

cmap = LinearSegmentedColormap.from_list(
    "news",
    ["#f0f4ff", "#c8ddf5", "#85b7eb", "#3a8fd4", "#1e5799", "#0d2f5e"],
    N=256,
)

data = pivot_pct.values
im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=0, vmax=100)

# ── 6. Annotate cells ─────────────────────────────────────────────────────────
for r in range(N_LANGS):
    for c in range(N_CATS):
        val = data[r, c]
        if val == 0:
            txt, alpha = "·", 0.4
        else:
            txt, alpha = f"{val:.0f}%", 1.0
        color = "#ffffff" if val > 45 else ("#1e3a6e" if val > 15 else "#8aaac8")
        ax.text(c, r, txt, ha="center", va="center",
                fontsize=8.5, color=color, alpha=alpha, fontweight="normal")

# ── 7. Axes labels ────────────────────────────────────────────────────────────
ax.set_xticks(range(N_CATS))
ax.set_xticklabels(
    [c.capitalize() for c in MAIN_CATS],
    color="#333333", fontsize=10, fontweight="normal"
)
ax.xaxis.set_ticks_position("top")
ax.xaxis.set_label_position("top")

ax.set_yticks(range(N_LANGS))
ax.set_yticklabels(
    pivot_pct.index.str.capitalize(),
    color="#333333", fontsize=9.5
)

# Article-count badge on the right
ax2 = ax.twinx()
ax2.set_facecolor("white")
ax2.set_ylim(ax.get_ylim())
ax2.set_yticks(range(N_LANGS))
ax2.set_yticklabels(
    [f"n={lang_counts[lang]}" for lang in pivot_pct.index],
    color="#888888", fontsize=8
)
ax2.tick_params(length=0)
ax2.spines[:].set_visible(False)

# ── 8. Grid lines ─────────────────────────────────────────────────────────────
for x in np.arange(-0.5, N_CATS, 1):
    ax.axvline(x, color="#e0e0e0", linewidth=0.7)
for y in np.arange(-0.5, N_LANGS, 1):
    ax.axhline(y, color="#e0e0e0", linewidth=0.7)

ax.tick_params(length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

# ── 9. Colour bar ─────────────────────────────────────────────────────────────
cbar_ax = fig.add_axes([0.97, 0.15, 0.015, 0.55])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.ax.set_facecolor("white")
cbar.ax.yaxis.set_tick_params(color="#666666", labelsize=8)
cbar.outline.set_edgecolor("#e0e0e0")
plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#666666")
cbar.set_label("% of language's articles", color="#666666", fontsize=8, labelpad=8)
cbar.set_ticks([0, 25, 50, 75, 100])
cbar.set_ticklabels(["0%", "25%", "50%", "75%", "100%"])

# ── 10. Titles & footnote ─────────────────────────────────────────────────────
fig.text(
    0.06, 0.97,
    "Topic Coverage by Language",
    color="#1a1a1a", fontsize=16, fontweight="normal", va="top"
)
fig.text(
    0.06, 0.93,
    "Share of each language's articles per topic category  ·  Sorted by Lifestyle share (ascending)",
    color="#666666", fontsize=9, va="top"
)
fig.text(
    0.06, 0.03,
    f"Source: newsdata.io  ·  {df.shape[0]} articles  ·  {len(valid_langs)} languages  ·  2026-04-02  ·  Languages with < 5 articles excluded",
    color="#aaaaaa", fontsize=7.5, va="bottom"
)

plt.subplots_adjust(left=0.12, right=0.93, top=0.88, bottom=0.06)

# ── 11. Show plot ──────────────────────────────────────────────────────────────
plt.show()
