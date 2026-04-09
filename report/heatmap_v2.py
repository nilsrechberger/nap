import pandas as pd
import ast
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import pdist


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

MIN_ARTICLES = 25  # raised from 5 — below this, percentages are noise
lang_counts = df["language"].value_counts()
valid_langs = lang_counts[lang_counts >= MIN_ARTICLES].index.tolist()

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

# ── 4. Compute deviation from global average ─────────────────────────────────
# This is what we'll actually plot — far more revealing than raw percentages.
global_avg = pivot_pct.mean(axis=0)
pivot_dev = pivot_pct.sub(global_avg, axis=1)

# ── 5. Cluster languages (rows) by coverage pattern ──────────────────────────
# Hierarchical clustering on the deviation matrix so similar languages group up.
if len(pivot_dev) > 2:
    row_linkage = linkage(pdist(pivot_dev.values, metric="euclidean"), method="average")
    row_order = leaves_list(row_linkage)
    pivot_dev = pivot_dev.iloc[row_order]
    pivot_pct = pivot_pct.iloc[row_order]

# ── 6. Reorder columns by variance (most distinctive categories first) ───────
col_variance = pivot_dev.var(axis=0).sort_values(ascending=False)
ordered_cats = col_variance.index.tolist()
pivot_dev = pivot_dev[ordered_cats]
pivot_pct = pivot_pct[ordered_cats]

# ── 7. Figure layout ──────────────────────────────────────────────────────────
N_LANGS = len(pivot_dev)
N_CATS = len(ordered_cats)

fig, ax = plt.subplots(figsize=(16, 10))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ── 8. Diverging colormap — red = over-indexed, blue = under-indexed ─────────
data = pivot_dev.values
# Symmetric limits so zero is always the neutral midpoint
vlim = np.percentile(np.abs(data), 95)
vlim = max(vlim, 10)  # floor so small deviations don't saturate

im = ax.imshow(data, cmap="RdBu_r", aspect="auto", vmin=-vlim, vmax=vlim)

# ── 9. Annotate cells with raw % (not deviation) ─────────────────────────────
raw = pivot_pct.values
for r in range(N_LANGS):
    for c in range(N_CATS):
        raw_val = raw[r, c]
        dev_val = data[r, c]

        if raw_val == 0:
            txt = "·"
            color = "#999999"
            alpha = 0.6
            fontweight = "normal"
        else:
            txt = f"{raw_val:.0f}%"
            # White text only on strongly saturated cells
            if abs(dev_val) > vlim * 0.6:
                color = "#ffffff"
            else:
                color = "#1a1a1a"
            alpha = 1.0
            fontweight = "bold" if abs(dev_val) > vlim * 0.3 else "normal"

        ax.text(c, r, txt, ha="center", va="center",
                fontsize=8, color=color, alpha=alpha, fontweight=fontweight)

# ── 10. Highlight the dominant category per row with a subtle border ─────────
for r in range(N_LANGS):
    max_c = np.argmax(raw[r])
    rect = plt.Rectangle(
        (max_c - 0.48, r - 0.48), 0.96, 0.96,
        fill=False, edgecolor="#1a1a1a", linewidth=1.5, zorder=5
    )
    ax.add_patch(rect)

# ── 11. Axes labels ───────────────────────────────────────────────────────────
ax.set_xticks(range(N_CATS))
ax.set_xticklabels(
    [c.capitalize() for c in ordered_cats],
    color="#333333", fontsize=9, fontweight="semibold"
)
ax.xaxis.set_ticks_position("top")
ax.xaxis.set_label_position("top")

ax.set_yticks(range(N_LANGS))
ax.set_yticklabels(
    pivot_dev.index.str.capitalize(),
    color="#333333", fontsize=9.5
)

# Article-count badge on the right
ax2 = ax.twinx()
ax2.set_facecolor("white")
ax2.set_ylim(ax.get_ylim())
ax2.set_yticks(range(N_LANGS))
ax2.set_yticklabels(
    [f"n={lang_counts[lang]}" for lang in pivot_dev.index],
    color="#888888", fontsize=7.5
)
ax2.tick_params(length=0)
ax2.spines[:].set_visible(False)

# ── 12. Grid lines ────────────────────────────────────────────────────────────
for x in np.arange(-0.5, N_CATS, 1):
    ax.axvline(x, color="#e0e0e0", linewidth=0.7)
for y in np.arange(-0.5, N_LANGS, 1):
    ax.axhline(y, color="#e0e0e0", linewidth=0.7)

ax.tick_params(length=0, colors="#333333")
for spine in ax.spines.values():
    spine.set_visible(False)

# ── 13. Colour bar ────────────────────────────────────────────────────────────
cbar_ax = fig.add_axes([0.95, 0.15, 0.012, 0.50])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.ax.set_facecolor("white")
cbar.ax.yaxis.set_tick_params(color="#666666", labelsize=7.5)
cbar.outline.set_edgecolor("#e0e0e0")
plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#666666")
cbar.set_label("Deviation from global avg (pp)", color="#666666", fontsize=8, labelpad=8)
cbar.set_ticks([-vlim, -vlim/2, 0, vlim/2, vlim])
cbar.set_ticklabels([f"−{vlim:.0f}", f"−{vlim/2:.0f}", "0", f"+{vlim/2:.0f}", f"+{vlim:.0f}"])

# ── 14. Titles & footnote ─────────────────────────────────────────────────────
fig.text(
    0.06, 0.96,
    "What's Distinctive About Each Language's News Coverage?",
    color="#1a1a1a", fontsize=18, fontweight="bold", va="top"
)
fig.text(
    0.06, 0.925,
    "Red = over-indexed vs. global average  ·  Blue = under-indexed  ·  Numbers show raw %  ·  Black box marks each language's top category",
    color="#666666", fontsize=8.5, va="top"
)
fig.text(
    0.06, 0.895,
    "Rows clustered by similarity of coverage pattern  ·  Columns ordered by how much languages differ on that category",
    color="#888888", fontsize=8, va="top", style="italic"
)
fig.text(
    0.06, 0.03,
    f"Source: newsdata.io  ·  {df.shape[0]:,} articles  ·  {len(valid_langs)} languages  ·  Languages with < {MIN_ARTICLES} articles excluded",
    color="#aaaaaa", fontsize=7.5, va="bottom"
)

plt.subplots_adjust(left=0.11, right=0.91, top=0.83, bottom=0.06)

# ── 15. Save & show ───────────────────────────────────────────────────────────
output_path = os.path.join(BASE_DIR, "plots", "language_category_heatmap.png")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved to {output_path}")

plt.show()
