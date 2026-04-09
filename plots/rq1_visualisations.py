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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "merged data.csv"))
FIGURE_PATH = Path("plots")

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
    "North America": {"lon": -100, "lat": 50},
    "Latin America": {"lon":  -60, "lat": -15},
    "Europe":        {"lon":   15, "lat":  52},
    "Africa":        {"lon":   22, "lat":   5},
    "Middle East":   {"lon":   47, "lat":  27},
    "Asia":          {"lon":  100, "lat":  38},
    "Oceania":       {"lon":  145, "lat": -27},
}

# Colour tokens
CMAP_BAR  = mcolors.LinearSegmentedColormap.from_list("b", ["#BFDBFE", "#1E3A8A"])
CMAP_BLUE = mcolors.LinearSegmentedColormap.from_list(
    "blue_scale", ["#BFD7F0", "#3B82F6", "#1D4ED8", "#1E3A8A", "#0D1B4B"])
TEXT  = "#1A1D23"
TDIM  = "#6B7280"
LIGHT = "#9CA3AF"

# Bubble sizing constant — change to resize all bubbles uniformly
MAX_PTS = 8000


# ── HELPERS ───────────────────────────────────────────────────────────────────

def parse_list(val: str) -> list:
    """Parse a stringified list from the API response into a Python list."""
    if pd.isna(val) or str(val).strip() in ("", "nan"):
        return []
    try:
        r = ast.literal_eval(str(val).strip())
        return [str(v).strip().lower() for v in r] if isinstance(r, list) \
               else [str(r).strip().lower()]
    except Exception:
        return [p.strip().lower()
                for p in re.sub(r"[\[\]']", "", str(val)).split(",") if p.strip()]


def is_ascii(s: str) -> bool:
    """Return True if string is ASCII-only (renderable in matplotlib default font)."""
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def art_color(articles: int, art_min: int, art_max: int):
    """Map article count to blue colour scale."""
    t = (articles - art_min) / max(art_max - art_min, 1)
    return CMAP_BLUE(t)


def luminance(rgb: tuple) -> float:
    r, g, b = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
               for x in rgb[:3]]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def label_color(articles: int, art_min: int, art_max: int) -> str:
    """White text on dark bubbles, dark text on light bubbles."""
    return "#FFFFFF" if luminance(art_color(articles, art_min, art_max)) < 0.35 \
           else "#1A1D23"


def s_pts(articles: int, art_max: int) -> float:
    """Scatter marker area in display points² — same on map and legend."""
    return (articles / art_max) * MAX_PTS


def r_pts(articles: int, art_max: int) -> float:
    """Radius in display points — used for label offsets."""
    return np.sqrt(s_pts(articles, art_max) / np.pi)


# ── LOAD & PREPARE ────────────────────────────────────────────────────────────

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, str, str]:
    """Load processed_merged.csv, clean, explode by country, return (df, exploded, date_min, date_max)."""
    df = pd.read_csv(DATA_PATH, header=None, dtype=str)
    df.columns = COLS[:df.shape[1]]
    df = df[df["duplicate"].str.strip().str.lower() == "false"].copy()
    df = df.drop_duplicates(subset="article_id", keep="first")

    date_min = df["source_date"].min()
    date_max = df["source_date"].max()
    print(f"Loaded {len(df):,} articles · {df['source_name'].nunique()} sources")
    print(f"Date range: {date_min} to {date_max}")

    df["countries_list"] = df["country"].apply(parse_list)

    exclude  = {"world", "europe", "european union", ""}
    exploded = df.explode("countries_list")
    exploded = exploded[~exploded["countries_list"].isin(exclude)].copy()
    exploded["region"] = exploded["countries_list"].map(REGION_MAP).fillna("Other")

    return df, exploded, date_min, date_max


# ── FIG 1: TOP 10 PUBLISHER COUNTRIES ────────────────────────────────────────

def plot_fig1(exploded: pd.DataFrame, total: int, date_min: str, date_max: str) -> None:
    pub_counts = exploded["countries_list"].value_counts().head(10).reset_index()
    pub_counts.columns = ["country", "articles"]
    pub_counts["country"] = pub_counts["country"].str.title()
    pub_counts["pct"]     = (pub_counts["articles"] / total * 100).round(1)
    pub_counts = pub_counts.sort_values("articles", ascending=True)

    n    = len(pub_counts)
    xmax = pub_counts["articles"].max()

    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="white", dpi=150)
    ax.set_facecolor("white")

    for i, (_, row) in enumerate(pub_counts.iterrows()):
        color = "#B45309" if i == n - 1 else CMAP_BAR(row["articles"] / xmax)
        ax.barh(i, row["articles"], color=color, height=0.55,
                edgecolor="white", linewidth=0.4)
        ax.text(row["articles"] + xmax * 0.015, i,
                f"{int(row['articles'])}  ({row['pct']:.1f}%)",
                va="center", ha="left", fontsize=9.5, color=TEXT,
                fontweight="bold" if i == n - 1 else "normal")

    ax.set_yticks(range(n))
    ax.set_yticklabels(pub_counts["country"], fontsize=11, color=TEXT)
    ax.set_xlim(0, xmax * 1.30)
    ax.set_xlabel("Number of articles", fontsize=10, color=TDIM, labelpad=8)
    ax.tick_params(axis="x", labelsize=9, colors=TDIM)
    ax.tick_params(axis="y", pad=10)
    ax.xaxis.grid(True, color="#E5E7EB", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color("#E5E7EB")

    fig.text(0.02, 0.97, "Top 10 Publisher Countries by Article Volume",
             fontsize=14, fontweight="bold", color=TEXT, va="top")
    fig.text(0.02, 0.01,
             f"Source: newsdata.io  ·  {total:,} articles  ·  {date_min} to {date_max}",
             fontsize=8, color=LIGHT, va="bottom")

    plt.subplots_adjust(left=0.22, right=0.97, top=0.90, bottom=0.08)
    out = FIGURE_PATH / "fig1_top_countries.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved → {out}")


# ── FIG 2: TOP 10 SOURCES ────────────────────────────────────────────────────

def plot_fig2(df: pd.DataFrame, total: int, date_min: str, date_max: str) -> None:
    src_all   = df.groupby("source_name").agg(articles=("article_id", "count")).reset_index()
    src_ascii = src_all[src_all["source_name"].apply(is_ascii)]

    skipped = src_all[~src_all["source_name"].apply(is_ascii)]
    if len(skipped) > 0:
        print(f"Note: {len(skipped)} sources with non-Latin names excluded from Fig 2 "
              f"(cannot render in matplotlib default font):")
        for _, r in skipped.sort_values("articles", ascending=False).head(5).iterrows():
            print(f"  {r['articles']} articles — {r['source_name']}")

    src_counts = (src_ascii.sort_values("articles", ascending=False)
                  .head(10).reset_index(drop=True))
    src_counts["pct"] = (src_counts["articles"] / total * 100).round(1)
    src_counts = src_counts.sort_values("articles", ascending=True)

    n2    = len(src_counts)
    xmax2 = src_counts["articles"].max()

    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="white", dpi=150)
    ax.set_facecolor("white")

    for i, (_, row) in enumerate(src_counts.iterrows()):
        color = "#B45309" if i == n2 - 1 else CMAP_BAR(row["articles"] / xmax2)
        ax.barh(i, row["articles"], color=color, height=0.55,
                edgecolor="white", linewidth=0.4)
        ax.text(row["articles"] + xmax2 * 0.015, i,
                f"{int(row['articles'])}  ({row['pct']:.1f}%)",
                va="center", ha="left", fontsize=9.5, color=TEXT,
                fontweight="bold" if i == n2 - 1 else "normal")

    ax.set_yticks(range(n2))
    ax.set_yticklabels(src_counts["source_name"], fontsize=11, color=TEXT)
    ax.set_xlim(0, xmax2 * 1.30)
    ax.set_xlabel("Number of articles", fontsize=10, color=TDIM, labelpad=8)
    ax.tick_params(axis="x", labelsize=9, colors=TDIM)
    ax.tick_params(axis="y", pad=10)
    ax.xaxis.grid(True, color="#E5E7EB", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color("#E5E7EB")

    fig.text(0.02, 0.97, "Top 10 News Sources by Article Count",
             fontsize=14, fontweight="bold", color=TEXT, va="top")
    fig.text(0.02, 0.01,
             f"Source: newsdata.io  ·  {total:,} articles  ·  "
             f"{df['source_name'].nunique()} unique sources  ·  "
             f"{date_min} to {date_max}  ·  Sources with non-Latin scripts excluded",
             fontsize=8, color=LIGHT, va="bottom")

    plt.subplots_adjust(left=0.22, right=0.97, top=0.90, bottom=0.08)
    out = FIGURE_PATH / "fig2_top_sources.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved → {out}")


# ── FIG 3: GEOGRAPHIC BIAS BUBBLE MAP ────────────────────────────────────────

def plot_fig3(exploded: pd.DataFrame, total: int, date_min: str, date_max: str) -> None:
    region_totals = (exploded.groupby("region")["article_id"]
                     .nunique().reset_index(name="articles")
                     .sort_values("articles", ascending=False))
    region_totals["pct"] = (region_totals["articles"] / total * 100).round(1)
    named   = region_totals[region_totals["region"] != "Other"].copy()
    art_min = int(named["articles"].min())
    art_max = int(named["articles"].max())

    # World map — bundled naturalearth_lowres shapefile
    pyogrio_path = os.path.dirname(pyogrio.__file__)
    shp_path = os.path.join(pyogrio_path, "tests", "fixtures",
                             "naturalearth_lowres", "naturalearth_lowres.shp")
    world = gpd.read_file(shp_path)

    fig = plt.figure(figsize=(15, 9.5), facecolor="white", dpi=150)

    # Map
    ax = fig.add_axes([0.0, 0.20, 0.76, 0.76])
    world.plot(ax=ax, color="#E8EDF5", edgecolor="#C4CDD8", linewidth=0.4)
    ax.set_facecolor("#D4E3F0")
    ax.set_xlim(-175, 180)
    ax.set_ylim(-65, 85)
    ax.set_aspect("equal")
    ax.axis("off")

    for _, row in named.iterrows():
        region   = row["region"]
        articles = int(row["articles"])
        pct      = row["pct"]
        lon      = REGION_POS[region]["lon"]
        lat      = REGION_POS[region]["lat"]
        color    = art_color(articles, art_min, art_max)
        sz       = s_pts(articles, art_max)
        r_p      = r_pts(articles, art_max)
        lc       = label_color(articles, art_min, art_max)

        ax.scatter(lon, lat, s=sz * 1.5, color=color, alpha=0.12,
                   zorder=4, linewidths=0, marker="o")
        ax.scatter(lon, lat, s=sz, color=color, alpha=0.90,
                   edgecolors="white", linewidths=1.2, zorder=5, marker="o")
        ax.annotate(region, xy=(lon, lat),
                    xytext=(0, r_p * 0.30), textcoords="offset points",
                    ha="center", va="center", fontsize=7.5, fontweight="500",
                    color=lc, zorder=6)
        ax.annotate(f"{articles} ({pct}%)", xy=(lon, lat),
                    xytext=(0, -r_p * 0.38), textcoords="offset points",
                    ha="center", va="center", fontsize=7,
                    color=(*mcolors.to_rgb(lc), 0.88), zorder=6)

    # Colourbar
    fig.text(0.810, 0.940, "Articles",
             fontsize=9, fontweight="500", color=TEXT, ha="center", va="bottom")
    cbar_ax = fig.add_axes([0.795, 0.30, 0.030, 0.62])
    sm = plt.cm.ScalarMappable(cmap=CMAP_BLUE,
                                norm=mcolors.Normalize(art_min, art_max))
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.set_ticks(np.linspace(art_min, art_max, 5).astype(int))
    cbar.ax.tick_params(labelsize=9, colors=TDIM)
    cbar.outline.set_edgecolor("#DDE3EC")

    # Size legend (horizontal strip below map)
    size_ax = fig.add_axes([0.0, 0.01, 0.76, 0.17])
    size_ax.set_facecolor("white")
    size_ax.set_xlim(0, 100)
    size_ax.set_ylim(0, 10)
    size_ax.axis("off")
    size_ax.text(1, 9.5, "Bubble size = article count",
                 fontsize=9, fontweight="500", color=TEXT, va="top")

    ref_vals    = np.linspace(art_min, art_max, 5).astype(int)
    x_positions = np.linspace(12, 88, len(ref_vals))
    cy          = 5.0

    for x_pos, val in zip(x_positions, ref_vals):
        sz_ref = s_pts(int(val), art_max)
        r_ref  = r_pts(int(val), art_max)
        size_ax.scatter(x_pos, cy, s=sz_ref,
                        facecolors="none", edgecolors="#888888",
                        linewidths=1.2, marker="o", zorder=3, alpha=0.9)
        size_ax.annotate(str(int(val)), xy=(x_pos, cy),
                         xytext=(0, -r_ref - 4), textcoords="offset points",
                         ha="center", va="top", fontsize=8.5, color=TDIM)

    fig.text(0.01, 0.97,
             "Geographic Bias — Article Volume by World Region",
             fontsize=14, fontweight="500", color=TEXT, va="top")
    fig.text(0.01, 0.002,
             f"Source: newsdata.io  ·  {total:,} articles  ·  "
             f"{date_min} to {date_max}  ·  'Other' excluded",
             fontsize=8, color=LIGHT, va="bottom")

    out = FIGURE_PATH / "fig3_regional_bias_bubbles.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved → {out}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main() -> None:
    FIGURE_PATH.mkdir(parents=True, exist_ok=True)

    df, exploded, date_min, date_max = load_data()
    total = len(df)

    print("\nGenerating Fig 1 — Top 10 Publisher Countries...")
    plot_fig1(exploded, total, date_min, date_max)

    print("\nGenerating Fig 2 — Top 10 Sources...")
    plot_fig2(df, total, date_min, date_max)

    print("\nGenerating Fig 3 — Geographic Bias Bubble Map...")
    plot_fig3(exploded, total, date_min, date_max)

    print("\nAll figures saved to", FIGURE_PATH)


#if __name__ == "__main__":
#   main()
