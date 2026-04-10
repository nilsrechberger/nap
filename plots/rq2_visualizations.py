import ast
import re
import warnings
from pathlib import Path

# Data handling
import numpy as np
import pandas as pd

# Visualisation
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")


# ── PATHS ─────────────────────────────────────────────────────────────────────
DATA_PATH = Path("../data/processed/processed_merged.csv")


# ── CONSTANTS ─────────────────────────────────────────────────────────────────
COLS = [
    "article_id", "link", "title", "description", "keywords", "creator",
    "language", "country", "category", "datatype", "pubDate", "pubDateTZ",
    "fetched_at", "image_url", "video_url", "source_id", "source_name",
    "source_priority", "source_url", "source_icon", "duplicate", "source_date",
]

TEXT     = "#1A1D23"
TDIM     = "#6B7280"
LIGHT    = "#9CA3AF"
COL_ORIG = "#3B82F6"   # blue  → original articles
COL_DUP  = "#B45309"   # orange → duplicate articles (matches RQ1)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def parse_list(val):
    if pd.isna(val) or str(val).strip() in ("", "nan"):
        return []
    try:
        r = ast.literal_eval(str(val).strip())
        return [str(v).strip().lower() for v in r] if isinstance(r, list) \
               else [str(r).strip().lower()]
    except Exception:
        return [p.strip().lower()
                for p in re.sub(r"[\[\]']", "", str(val)).split(",") if p.strip()]


def is_ascii(s):
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


# ── SHARED DIVERGING BAR HELPER ───────────────────────────────────────────────
def draw_diverging(ax, labels, orig_rates, dup_rates):
    """Draw a diverging bar chart on ax.
    orig_rates go left (negative), dup_rates go right (positive).
    % labels sit just outside each bar end.
    """
    n = len(labels)
    for i, (orig_pct, dup_pct) in enumerate(zip(orig_rates, dup_rates)):
        ax.barh(i, -orig_pct, color=COL_ORIG, height=0.60,
                edgecolor="white", linewidth=0.4)
        ax.barh(i,  dup_pct,  color=COL_DUP,  height=0.60,
                edgecolor="white", linewidth=0.4)
        # Labels outside bars
        ax.text(-orig_pct - 1.5, i, f"{orig_pct:.0f}%",
                va="center", ha="right", fontsize=10,
                color=COL_ORIG, fontweight="bold")
        ax.text(dup_pct + 1.5, i, f"{dup_pct:.0f}%",
                va="center", ha="left", fontsize=10,
                color=COL_DUP, fontweight="bold")

    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=12, color=TEXT)
    ax.axvline(0, color="#CBD5E1", linewidth=1.2)
    ax.set_xlim(-115, 115)
    ax.tick_params(axis="x", labelsize=10, colors=TDIM)
    ax.tick_params(axis="y", pad=8)
    ax.set_xticks([-100, -75, -50, -25, 0, 25, 50, 75, 100])
    ax.set_xticklabels(["100%","75%","50%","25%","0","25%","50%","75%","100%"])
    ax.xaxis.grid(True, color="#E5E7EB", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    # Column headers above each half
    ax.text(0.25, 1.01, "Original",
            transform=ax.transAxes,
            ha="center", va="bottom", fontsize=13,
            color=COL_ORIG, fontweight="bold")
    ax.text(0.75, 1.01, "Duplicate",
            transform=ax.transAxes,
            ha="center", va="bottom", fontsize=13,
            color=COL_DUP, fontweight="bold")


# ── LOAD & PREPARE ────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH, header=None, dtype=str)
df.columns = COLS[:df.shape[1]]
df = df.drop_duplicates(subset="article_id", keep="first")

df["category_list"] = df["category"].apply(parse_list)
df["category_list"] = df["category_list"].apply(lambda x: [c for c in x if c != "top"])
df["is_dup"] = df["duplicate"].str.strip().str.lower() == "true"

total    = len(df)
n_dup    = int(df["is_dup"].sum())
date_min = df["source_date"].min()
date_max = df["source_date"].max()

df_cat = df.explode("category_list")
df_cat = df_cat[df_cat["category_list"].notna() & (df_cat["category_list"] != "")].copy()

cat_stats = (df_cat.groupby("category_list")
             .agg(total=("article_id", "count"), dups=("is_dup", "sum"))
             .reset_index())
cat_stats["dup_rate"]  = (cat_stats["dups"] / cat_stats["total"] * 100).round(1)
cat_stats["orig_rate"] = 100 - cat_stats["dup_rate"]
cat_stats = (cat_stats[cat_stats["total"] >= 10]
             .sort_values("dup_rate", ascending=True)
             .reset_index(drop=True))
cat_stats["category_list"] = cat_stats["category_list"].str.title()


# ══════════════════════════════════════════════════════════════════════════════
# FIG 4 & FIG 5 — SIDE BY SIDE, EACH WITH OWN CAPTION
# ══════════════════════════════════════════════════════════════════════════════
src_all = (df.groupby("source_name")
           .agg(total=("article_id", "count"), dups=("is_dup", "sum"))
           .reset_index())
src_all["dup_rate"]  = (src_all["dups"] / src_all["total"] * 100).round(1)
src_all["orig_rate"] = 100 - src_all["dup_rate"]

src_top = (src_all[src_all["source_name"].apply(is_ascii) & (src_all["total"] >= 5)]
           .sort_values("dups", ascending=False)
           .head(10)
           .sort_values("dup_rate", ascending=True)
           .reset_index(drop=True))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), facecolor="white", dpi=150)

# ── Left: By topic category ──────────────────────────────────────────────────
ax1.set_facecolor("white")
draw_diverging(ax1,
               labels=cat_stats["category_list"].tolist(),
               orig_rates=cat_stats["orig_rate"].tolist(),
               dup_rates=cat_stats["dup_rate"].tolist())
ax1.set_title("Original vs Duplicate Share by Topic Category",
              fontsize=14, fontweight="bold", color=TEXT,
              loc="left", pad=36)

# ── Right: By source ─────────────────────────────────────────────────────────
ax2.set_facecolor("white")
draw_diverging(ax2,
               labels=src_top["source_name"].tolist(),
               orig_rates=src_top["orig_rate"].tolist(),
               dup_rates=src_top["dup_rate"].tolist())
ax2.set_title("Original vs Duplicate Share by Source",
              fontsize=14, fontweight="bold", color=TEXT,
              loc="left", pad=36)

fig.text(0.02, 0.01,
         f"Source: newsdata.io  ·  {total:,} articles incl. duplicates  ·  "
         f"{date_min} to {date_max}  ·  Top 10 sources by duplicate count  ·  "
         f"Sources with non-Latin scripts excluded",
         fontsize=9, color=LIGHT, va="bottom")

# Individual captions under each subplot
fig.text(0.27, -0.02,
         "Figure 4: Original vs duplicate share by topic category.\n"
         "Diverging bars split each category into original (left) and duplicate (right) percentages.",
         fontsize=16, color=TEXT, va="top", ha="center",
         fontstyle="italic", transform=fig.transFigure)

fig.text(0.73, -0.02,
         "Figure 5: Original vs duplicate share by source.\n"
         "Same diverging layout as Figure 4, showing the top 10 sources by duplicate count.",
         fontsize=16, color=TEXT, va="top", ha="center",
         fontstyle="italic", transform=fig.transFigure)

plt.subplots_adjust(left=0.06, right=0.97, top=0.88, bottom=0.08, wspace=0.35)
plt.show()