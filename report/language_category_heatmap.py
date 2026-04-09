import pandas as pd
import ast
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.colors import LinearSegmentedColormap


# ── 1. Load & parse ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "merged data.csv"))

df["category_list"] = df["category"].apply(
    lambda x: ast.literal_eval(x) if pd.notna(x) else []
)
df_exp = df.explode("category_list")
df_exp["cat"] = df_exp["category_list"].str.strip().str.lower()
df_exp = df_exp[df_exp["cat"].notna() & (df_exp["cat"] != "")]

# ── 2. Filter ─────────────────────────────────────────────────────────────────
ALL_CATS = [
    "lifestyle", "business", "sports", "entertainment",
    "politics", "world", "technology"
]

lang_counts = df["language"].value_counts()
valid_langs = lang_counts[lang_counts >= 5].index.tolist()

df_filt = df_exp[
    df_exp["language"].isin(valid_langs) &
    df_exp["cat"].isin(ALL_CATS)
]

# ── 3. Build normalized pivot (% per language) ────────────────────────────────
pivot = df_filt.groupby(["language", "cat"]).size().unstack(fill_value=0)
for c in ALL_CATS:
    if c not in pivot.columns:
        pivot[c] = 0
pivot = pivot[ALL_CATS]

pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

# Sort languages by total article count (descending)
lang_order = lang_counts[lang_counts >= 5].index.tolist()
pivot_pct = pivot_pct.reindex([l for l in lang_order if l in pivot_pct.index])

# ── 4. Figure layout ──────────────────────────────────────────────────────────
N_LANGS = len(pivot_pct)
N_CATS = len(ALL_CATS)

fig, ax = plt.subplots(figsize=(16, 10))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ── 5. Colour scale ───────────────────────────────────────────────────────────
cmap = LinearSegmentedColormap.from_list(
    "news",
    ["#f0f4ff", "#c8ddf5", "#85b7eb", "#3a8fd4", "#1e5799", "#0d2f5e"],
    N=256,
)

data = pivot_pct.values
im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=0, vmax=65)

# ── 6. Annotate cells ─────────────────────────────────────────────────────────
for r in range(N_LANGS):
    for c in range(N_CATS):
        val = data[r, c]
        if val == 0:
            txt = "·"
            color = "#999999"
            alpha = 0.6
            fontweight = "normal"
        else:
            txt = f"{val:.0f}%"
            # High contrast: white on dark cells, dark navy on light cells
            if val > 35:
                color = "#ffffff"
            else:
                color = "#0a1f3d"
            alpha = 1.0
            fontweight = "bold" if val > 10 else "normal"
        ax.text(c, r, txt, ha="center", va="center",
                fontsize=8, color=color, alpha=alpha, fontweight=fontweight)

# ── 7. Axes labels ────────────────────────────────────────────────────────────
ax.set_xticks(range(N_CATS))
ax.set_xticklabels(
    [c.capitalize() for c in ALL_CATS],
    color="#333333", fontsize=9, fontweight="semibold"
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
    color="#888888", fontsize=7.5
)
ax2.tick_params(length=0)
ax2.spines[:].set_visible(False)

# ── 8. Grid lines ─────────────────────────────────────────────────────────────
for x in np.arange(-0.5, N_CATS, 1):
    ax.axvline(x, color="#e0e0e0", linewidth=0.7)
for y in np.arange(-0.5, N_LANGS, 1):
    ax.axhline(y, color="#e0e0e0", linewidth=0.7)

ax.tick_params(length=0, colors="#333333")
for spine in ax.spines.values():
    spine.set_visible(False)

# ── 9. Colour bar ─────────────────────────────────────────────────────────────
cbar_ax = fig.add_axes([0.95, 0.15, 0.012, 0.50])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.ax.set_facecolor("white")
cbar.ax.yaxis.set_tick_params(color="#666666", labelsize=7.5)
cbar.outline.set_edgecolor("#e0e0e0")
plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#666666")
cbar.set_label("% of language's articles", color="#666666", fontsize=8, labelpad=8)
cbar.set_ticks([0, 15, 30, 45, 60])
cbar.set_ticklabels(["0%", "15%", "30%", "45%", "60%+"])

# ── 10. Titles & footnote ─────────────────────────────────────────────────────
fig.text(
    0.06, 0.97,
    "CROSS-LANGUAGE NEWS ANALYSIS",
    color="#3a8fd4", fontsize=9, fontweight="bold", va="top"
)
fig.text(
    0.06, 0.94,
    "Topic Coverage by Language",
    color="#1a1a1a", fontsize=18, fontweight="bold", va="top"
)
fig.text(
    0.06, 0.91,
    "Each cell shows what percentage of a language's articles fall into a given category  ·  Sorted by total article count",
    color="#666666", fontsize=8.5, va="top"
)
fig.text(
    0.06, 0.03,
    f"Source: newsdata.io  ·  {df.shape[0]} articles  ·  {len(valid_langs)} languages  ·  Languages with < 5 articles excluded",
    color="#aaaaaa", fontsize=7.5, va="bottom"
)

plt.subplots_adjust(left=0.11, right=0.91, top=0.85, bottom=0.06)

# ── 11. Save & show ───────────────────────────────────────────────────────────
output_path = os.path.join(BASE_DIR, "plots", "language_category_heatmap.png")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved to {output_path}")

plt.show()
