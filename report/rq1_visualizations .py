# Built-in
import ast
import os
import re
import warnings
from pathlib import Path

# Data handling
import numpy as np
import pandas as pd

# Visualisation
import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

# Geospatial
import geopandas as gpd
import pyogrio

warnings.filterwarnings("ignore")


# ── PATHS ─────────────────────────────────────────────────────────────────────
DATA_PATH = Path("../data/processed/merged data.csv")

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
COLS = [
    "article_id", "link", "title", "description", "keywords", "creator",
    "language", "country", "category", "datatype", "pubDate", "pubDateTZ",
    "fetched_at", "image_url", "video_url", "source_id", "source_name",
    "source_priority", "source_url", "source_icon", "duplicate", "source_date",
]

REGION_MAP = {
    "austria": "Europe", "germany": "Europe", "france": "Europe",
    "united kingdom": "Europe", "spain": "Europe", "italy": "Europe",
    "netherlands": "Europe", "netherland": "Europe", "switzerland": "Europe",
    "belgium": "Europe", "sweden": "Europe", "poland": "Europe",
    "portugal": "Europe", "norway": "Europe", "denmark": "Europe",
    "finland": "Europe", "ireland": "Europe", "czech republic": "Europe",
    "hungary": "Europe", "romania": "Europe", "greece": "Europe",
    "croatia": "Europe", "slovakia": "Europe", "bulgaria": "Europe",
    "serbia": "Europe", "ukraine": "Europe", "russia": "Europe",
    "luxembourg": "Europe", "lithuania": "Europe", "latvia": "Europe",
    "estonia": "Europe", "slovenia": "Europe", "albania": "Europe",
    "macedonia": "Europe", "montenegro": "Europe", "kosovo": "Europe",
    "moldova": "Europe", "belarus": "Europe", "iceland": "Europe",
    "monaco": "Europe", "malta": "Europe", "cyprus": "Europe",
    "bosnia and herzegovina": "Europe", "jersey": "Europe", "guernsey": "Europe",
    "united states of america": "North America", "canada": "North America",
    "mexico": "North America",
    "brazil": "Latin America", "argentina": "Latin America",
    "colombia": "Latin America", "chile": "Latin America",
    "peru": "Latin America", "venezuela": "Latin America",
    "cuba": "Latin America", "dominican republic": "Latin America",
    "ecuador": "Latin America",
    "china": "Asia", "japan": "Asia", "india": "Asia",
    "south korea": "Asia", "singapore": "Asia", "taiwan": "Asia",
    "indonesia": "Asia", "malaysia": "Asia", "thailand": "Asia",
    "philippines": "Asia", "vietnam": "Asia", "pakistan": "Asia",
    "bangladesh": "Asia", "hong kong": "Asia", "cambodia": "Asia",
    "myanmar": "Asia", "sri lanka": "Asia",
    "israel": "Middle East", "iran": "Middle East",
    "saudi arabia": "Middle East", "united arab emirates": "Middle East",
    "turkey": "Middle East", "iraq": "Middle East", "jordan": "Middle East",
    "lebanon": "Middle East", "egypt": "Middle East", "qatar": "Middle East",
    "kuwait": "Middle East", "bahrain": "Middle East",
    "palestine": "Middle East", "syria": "Middle East", "oman": "Middle East",
    "nigeria": "Africa", "south africa": "Africa", "kenya": "Africa",
    "ethiopia": "Africa", "ghana": "Africa", "tanzania": "Africa",
    "morocco": "Africa", "algeria": "Africa", "angola": "Africa",
    "cameroon": "Africa", "uganda": "Africa", "dr congo": "Africa",
    "cape verde": "Africa", "ivory coast": "Africa",
    "australia": "Oceania", "new zealand": "Oceania",
    "fiji": "Oceania", "cook islands": "Oceania",
}

REGION_POS = {
    "North America": {"lon": -100, "lat":  50},
    "Latin America": {"lon":  -60, "lat": -15},
    "Europe":        {"lon":   15, "lat":  52},
    "Africa":        {"lon":   22, "lat":   5},
    "Middle East":   {"lon":   47, "lat":  27},
    "Asia":          {"lon":  100, "lat":  38},
    "Oceania":       {"lon":  145, "lat": -27},
}

CMAP_BAR  = mcolors.LinearSegmentedColormap.from_list("b", ["#BFDBFE", "#1E3A8A"])
CMAP_BLUE = mcolors.LinearSegmentedColormap.from_list(
    "blue_scale", ["#BFD7F0", "#3B82F6", "#1D4ED8", "#1E3A8A", "#0D1B4B"])
TEXT    = "#1A1D23"
TDIM    = "#6B7280"
LIGHT   = "#9CA3AF"
MAX_PTS = 8000   # bubble size — increase to enlarge all bubbles


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


# ── LOAD & PREPARE ────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH, header=None, dtype=str)
df.columns = COLS[:df.shape[1]]
df = df[df["duplicate"].str.strip().str.lower() == "false"].copy()
df = df.drop_duplicates(subset="article_id", keep="first")

total    = len(df)
date_min = df["source_date"].min()
date_max = df["source_date"].max()
df["countries_list"] = df["country"].apply(parse_list)

EXCLUDE  = {"world", "europe", "european union", ""}
exploded = df.explode("countries_list")
exploded = exploded[~exploded["countries_list"].isin(EXCLUDE)].copy()
exploded["region"] = exploded["countries_list"].map(REGION_MAP).fillna("Other")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 1 — TOP 10 PUBLISHER COUNTRIES + TOP 10 SOURCES (side by side)
# ══════════════════════════════════════════════════════════════════════════════
pub_counts = exploded["countries_list"].value_counts().head(10).reset_index()
pub_counts.columns = ["country", "articles"]
pub_counts["country"] = pub_counts["country"].str.title()
pub_counts["pct"]     = (pub_counts["articles"] / total * 100).round(1)
pub_counts = pub_counts.sort_values("articles", ascending=True)

src_all   = df.groupby("source_name").agg(articles=("article_id", "count")).reset_index()
src_ascii = src_all[src_all["source_name"].apply(is_ascii)]

skipped = src_all[~src_all["source_name"].apply(is_ascii)]

src_counts = src_ascii.sort_values("articles", ascending=False).head(10).reset_index(drop=True)
src_counts["pct"] = (src_counts["articles"] / total * 100).round(1)
src_counts = src_counts.sort_values("articles", ascending=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 8), facecolor="white", dpi=150)

# ── Left: Publisher countries ─────────────────────────────────────────────────
ax1.set_facecolor("white")
n    = len(pub_counts)
xmax = pub_counts["articles"].max()

for i, (_, row) in enumerate(pub_counts.iterrows()):
    color = "#B45309" if i == n - 1 else CMAP_BAR(row["articles"] / xmax)
    ax1.barh(i, row["articles"], color=color, height=0.55,
             edgecolor="white", linewidth=0.4)
    ax1.text(row["articles"] + xmax * 0.015, i,
             f"{int(row['articles'])}  ({row['pct']:.1f}%)",
             va="center", ha="left", fontsize=9.5, color=TEXT,
             fontweight="bold" if i == n - 1 else "normal")

ax1.set_yticks(range(n))
ax1.set_yticklabels(pub_counts["country"], fontsize=11, color=TEXT)
ax1.set_xlim(0, xmax * 1.30)
ax1.set_xlabel("Number of articles", fontsize=10, color=TDIM, labelpad=8)
ax1.tick_params(axis="x", labelsize=9, colors=TDIM)
ax1.tick_params(axis="y", pad=10)
ax1.xaxis.grid(True, color="#E5E7EB", linewidth=0.6, zorder=0)
ax1.set_axisbelow(True)
for sp in ax1.spines.values():
    sp.set_visible(False)
ax1.spines["bottom"].set_visible(True)
ax1.spines["bottom"].set_color("#E5E7EB")
ax1.set_title("Top 10 Publisher Countries by Article Volume",
              fontsize=13, fontweight="bold", color=TEXT,
              loc="left", pad=12)

# ── Right: News sources ───────────────────────────────────────────────────────
ax2.set_facecolor("white")
n2    = len(src_counts)
xmax2 = src_counts["articles"].max()

for i, (_, row) in enumerate(src_counts.iterrows()):
    color = "#B45309" if i == n2 - 1 else CMAP_BAR(row["articles"] / xmax2)
    ax2.barh(i, row["articles"], color=color, height=0.55,
             edgecolor="white", linewidth=0.4)
    ax2.text(row["articles"] + xmax2 * 0.015, i,
             f"{int(row['articles'])}  ({row['pct']:.1f}%)",
             va="center", ha="left", fontsize=9.5, color=TEXT,
             fontweight="bold" if i == n2 - 1 else "normal")

ax2.set_yticks(range(n2))
ax2.set_yticklabels(src_counts["source_name"], fontsize=11, color=TEXT)
ax2.set_xlim(0, xmax2 * 1.30)
ax2.set_xlabel("Number of articles", fontsize=10, color=TDIM, labelpad=8)
ax2.tick_params(axis="x", labelsize=9, colors=TDIM)
ax2.tick_params(axis="y", pad=10)
ax2.xaxis.grid(True, color="#E5E7EB", linewidth=0.6, zorder=0)
ax2.set_axisbelow(True)
for sp in ax2.spines.values():
    sp.set_visible(False)
ax2.spines["bottom"].set_visible(True)
ax2.spines["bottom"].set_color("#E5E7EB")
ax2.set_title("Top 10 News Sources by Article Count",
              fontsize=13, fontweight="bold", color=TEXT,
              loc="left", pad=12)

fig.text(0.02, 0.01,
         f"Source: newsdata.io  ·  {total:,} articles  ·  "
         f"{df['source_name'].nunique()} unique sources  ·  "
         f"{date_min} to {date_max}  ·  Sources with non-Latin scripts excluded",
         fontsize=8, color=LIGHT, va="bottom")

fig.text(0.27, -0.04,
         "Figure 1: Top 10 publisher countries by article volume.",
         fontsize=16, color=TEXT, va="top", ha="center",
         fontstyle="italic", transform=fig.transFigure)

fig.text(0.73, -0.04,
         "Figure 2: Top 10 news sources by article count.",
         fontsize=16, color=TEXT, va="top", ha="center",
         fontstyle="italic", transform=fig.transFigure)

plt.subplots_adjust(left=0.08, right=0.97, top=0.90, bottom=0.12, wspace=0.35)
plt.show()