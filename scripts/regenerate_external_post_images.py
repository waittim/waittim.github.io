#!/usr/bin/env python3
"""Regenerate migrated post charts with a unified site-aligned visual style."""

from __future__ import annotations

import os
import re
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".venv-img" / "mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from PIL import Image
from scipy import stats
from scipy.optimize import brentq

RNG = np.random.default_rng(20260721)

# Site tokens from css/theme.css
INK = "#404040"
MUTED = "#6b6b6b"
GRID = "#e8e8e8"
SPINE = "#cccccc"
ACCENT = "#00809b"
LINK = "#337ab7"
# Transparent canvas: page color shows through; pairs with `.chart-invert` in dark mode.
PAGE = "none"

# Sequential / categorical palette around accent (no purple/rainbow defaults)
PALETTE = [
    "#00809b",  # accent teal
    "#337ab7",  # link blue
    "#2a9d8f",  # sea green
    "#4a5568",  # slate
    "#c45c26",  # warm rust (accent contrast)
    "#5b8a72",  # muted sage
    "#1d3557",  # deep navy
]
CAPTURE = "#00809b"
MISS = "#c45c26"
MARKER_FACE = "#ffffff"
# Continuous map for quantile coloring on density scatters (site teal/blue family)
QUANTILE_CMAP = matplotlib.colors.LinearSegmentedColormap.from_list(
    "site_quantile",
    ["#1d3557", "#7eb8c4"],
)

FIGSIZE = (8.0, 4.8)
DPI = 160
FONT_DIR = ROOT / ".venv-img" / "fonts"
FAMILY = "Helvetica Neue"
TITLE_FP = None
LABEL_FP = None
BODY_FP = None


def _ensure_site_fonts() -> None:
    """Extract Helvetica Neue faces used by the site stack so bold/medium resolve reliably."""
    global TITLE_FP, LABEL_FP, BODY_FP, FAMILY
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    faces = {
        "HelveticaNeue-Regular.ttf": 0,
        "HelveticaNeue-Bold.ttf": 1,
        "HelveticaNeue-Medium.ttf": 10,
    }
    source = Path("/System/Library/Fonts/HelveticaNeue.ttc")
    if source.exists():
        try:
            from fontTools.ttLib import TTCollection

            coll = TTCollection(str(source))
            for filename, idx in faces.items():
                dest = FONT_DIR / filename
                if not dest.exists():
                    coll.fonts[idx].save(str(dest))
                font_manager.fontManager.addfont(str(dest))
        except Exception:
            pass

    # Prefer System Font (SF) when available for body text — matches -apple-system.
    sf = Path("/System/Library/Fonts/SFNS.ttf")
    if sf.exists():
        try:
            font_manager.fontManager.addfont(str(sf))
            body_family = "System Font"
        except Exception:
            body_family = "Helvetica Neue"
    else:
        body_family = "Helvetica Neue"

    available = {f.name for f in font_manager.fontManager.ttflist}
    preferred = [body_family, "Helvetica Neue", "Arial", "DejaVu Sans"]
    FAMILY = next((name for name in preferred if name in available), "DejaVu Sans")

    # Titles/labels use Helvetica Neue weights when extracted; fall back to family weight.
    bold_path = FONT_DIR / "HelveticaNeue-Bold.ttf"
    medium_path = FONT_DIR / "HelveticaNeue-Medium.ttf"
    regular_path = FONT_DIR / "HelveticaNeue-Regular.ttf"
    if bold_path.exists():
        TITLE_FP = font_manager.FontProperties(fname=str(bold_path), size=13)
    else:
        TITLE_FP = font_manager.FontProperties(family=FAMILY, size=13, weight="bold")
    if medium_path.exists():
        LABEL_FP = font_manager.FontProperties(fname=str(medium_path), size=11)
    else:
        LABEL_FP = font_manager.FontProperties(family=FAMILY, size=11, weight="medium")
    if regular_path.exists() and FAMILY != "System Font":
        BODY_FP = font_manager.FontProperties(fname=str(regular_path), size=10)
    else:
        BODY_FP = font_manager.FontProperties(family=FAMILY, size=10, weight="normal")


def configure_style() -> None:
    _ensure_site_fonts()
    plt.rcParams.update(
        {
            "figure.facecolor": PAGE,
            "axes.facecolor": PAGE,
            "savefig.facecolor": PAGE,
            "savefig.transparent": True,
            "font.family": FAMILY,
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlepad": 12,
            "axes.labelsize": 11,
            "axes.labelweight": "medium",
            "axes.labelcolor": INK,
            "axes.edgecolor": SPINE,
            "axes.linewidth": 1.0,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "grid.alpha": 1.0,
            "legend.frameon": False,
            "legend.fontsize": 10,
            "legend.title_fontsize": 10,
            "lines.linewidth": 2.0,
            "lines.markersize": 5.5,
            "axes.prop_cycle": plt.cycler(color=PALETTE),
        }
    )


def finish_axes(ax: plt.Axes, title: str | None = None, xlabel: str | None = None, ylabel: str | None = None) -> None:
    if title:
        ax.set_title(title, loc="left", color=INK, fontproperties=TITLE_FP)
    if xlabel:
        ax.set_xlabel(xlabel, color=INK, fontproperties=LABEL_FP)
    if ylabel:
        ax.set_ylabel(ylabel, color=INK, fontproperties=LABEL_FP)
    ax.grid(True, axis="y")
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    if BODY_FP is not None:
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(BODY_FP)


def style_legend(leg) -> None:
    if leg is None:
        return
    if TITLE_FP is not None and leg.get_title() is not None:
        # Legend title slightly emphasized; entries stay regular.
        medium = LABEL_FP if LABEL_FP is not None else TITLE_FP
        leg.get_title().set_fontproperties(medium)
        leg.get_title().set_color(MUTED)
    if BODY_FP is not None:
        for text in leg.get_texts():
            text.set_fontproperties(BODY_FP)


def new_fig() -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    return fig, ax


def save_chart(path: Path, fig: plt.Figure) -> tuple[int, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(
        path,
        dpi=DPI,
        bbox_inches="tight",
        facecolor="none",
        edgecolor="none",
        transparent=True,
    )
    plt.close(fig)
    with Image.open(path) as im:
        return im.size


def plot_line(
    xs,
    ys,
    path: Path,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    color: str = ACCENT,
    xticks=None,
    marker: str = "o",
) -> tuple[int, int]:
    fig, ax = new_fig()
    ax.plot(xs, ys, marker=marker, color=color, markerfacecolor=MARKER_FACE, markeredgewidth=1.4)
    if xticks is not None:
        ax.set_xticks(list(xticks))
        ax.tick_params(axis="x", labelrotation=45)
    finish_axes(ax, title, xlabel, ylabel)
    return save_chart(path, fig)


def plot_density_scatter(
    dens,
    lengths,
    qs,
    path: Path,
    *,
    title: str,
    xlabel: str = "Density",
    ylabel: str = "Length of middle 95%",
) -> tuple[int, int]:
    """Scatter density vs length; no line — density is not monotone along quantiles for mixtures."""
    dens = np.asarray(dens, dtype=float)
    lengths = np.asarray(lengths, dtype=float)
    qs = np.asarray(qs, dtype=float)
    fig, ax = new_fig()
    sc = ax.scatter(
        dens,
        lengths,
        c=qs,
        cmap=QUANTILE_CMAP,
        s=48,
        edgecolors=INK,
        linewidths=0.6,
        zorder=3,
        vmin=float(qs.min()),
        vmax=float(qs.max()),
    )
    cbar = fig.colorbar(sc, ax=ax, pad=0.02, fraction=0.046)
    cbar.set_label("p-th quantile", color=INK)
    cbar.outline.set_edgecolor(SPINE)
    cbar.ax.yaxis.set_tick_params(color=MUTED, labelcolor=MUTED)
    if LABEL_FP is not None:
        cbar.ax.yaxis.label.set_fontproperties(LABEL_FP)
    if BODY_FP is not None:
        for label in cbar.ax.get_yticklabels():
            label.set_fontproperties(BODY_FP)
    finish_axes(ax, title, xlabel, ylabel)
    return save_chart(path, fig)


def plot_multi_density_scatter(
    series: list[tuple[np.ndarray | list, np.ndarray | list, str]],
    path: Path,
    *,
    title: str,
    xlabel: str = "Density",
    ylabel: str = "Length of middle 95%",
    legend_title: str | None = "Sample size",
) -> tuple[int, int]:
    """For unimodal families, sort by density so each series forms one readable curve."""
    fig, ax = new_fig()
    for i, (xs, ys, label) in enumerate(series):
        xs = np.asarray(xs, dtype=float)
        ys = np.asarray(ys, dtype=float)
        order = np.argsort(xs)
        color = PALETTE[i % len(PALETTE)]
        ax.plot(
            xs[order],
            ys[order],
            marker="o",
            color=color,
            label=label,
            markerfacecolor=MARKER_FACE,
            markeredgewidth=1.2,
        )
    finish_axes(ax, title, xlabel, ylabel)
    style_legend(ax.legend(title=legend_title, loc="best"))
    return save_chart(path, fig)


def plot_multi_lines(
    series: list[tuple[np.ndarray | list, np.ndarray | list, str]],
    path: Path,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    xticks=None,
    legend_title: str | None = None,
) -> tuple[int, int]:
    fig, ax = new_fig()
    for i, (xs, ys, label) in enumerate(series):
        color = PALETTE[i % len(PALETTE)]
        ax.plot(xs, ys, marker="o", color=color, label=label, markerfacecolor=MARKER_FACE, markeredgewidth=1.2)
    if xticks is not None:
        ax.set_xticks(list(xticks))
        ax.tick_params(axis="x", labelrotation=45)
    finish_axes(ax, title, xlabel, ylabel)
    leg = ax.legend(title=legend_title, loc="best")
    style_legend(leg)
    return save_chart(path, fig)


def update_post_image_dims(slug: str, name: str, size: tuple[int, int], alt: str | None = None) -> None:
    """Refresh width/height (and optional alt) on existing local img tags."""
    w, h = size
    needle = f'/img/posts/{slug}/{name}'
    for path in (ROOT / "_posts").glob("*.md"):
        text = path.read_text()
        if needle not in text:
            continue

        def repl(match: re.Match[str]) -> str:
            tag = match.group(0)
            tag = re.sub(r'\bwidth="\d+"', f'width="{w}"', tag)
            tag = re.sub(r'\bheight="\d+"', f'height="{h}"', tag)
            if alt is not None:
                if re.search(r'\balt="[^"]*"', tag):
                    tag = re.sub(r'\balt="[^"]*"', f'alt="{alt}"', tag)
                else:
                    tag = tag.replace("<img", f'<img alt="{alt}"', 1)
            return tag

        new_text = re.sub(rf'<img\b[^>]*{re.escape(needle)}[^>]*>', repl, text)
        if new_text != text:
            path.write_text(new_text)
            print(f"  dims → {path.name} :: {name} ({w}×{h})")


def one_series(B=200, W=300, L=1000, M=100):
    budget = float(B)
    plays = 0
    previous_wager = 0.0
    previous_win = True
    series = []
    for _ in range(L):
        proposed = 1.0 if previous_win else 2.0 * previous_wager
        wager = min(proposed, M, budget)
        red = RNG.random() < 18 / 38
        plays += 1
        previous_wager = wager
        if red:
            budget += wager
            previous_win = True
        else:
            budget -= wager
            previous_win = False
        series.append(budget)
        if budget <= 0 or plays >= L or budget >= W:
            break
    return np.asarray(series)


def mid95_lengths(sampler, sample_size=200, test_num=5000):
    qs = np.arange(0.05, 0.96, 0.05)
    data = sampler(sample_size * test_num).reshape(test_num, sample_size)
    quantiles = np.quantile(data, qs, axis=1).T
    lo, hi = np.quantile(quantiles, [0.025, 0.975], axis=0)
    return qs, hi - lo


def one_sided_corr_lower(x: np.ndarray, y: np.ndarray) -> float:
    r = float(np.clip(np.corrcoef(x, y)[0, 1], -0.999999, 0.999999))
    n = len(x)
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(max(n - 3, 1))
    return float(np.tanh(z - stats.norm.ppf(0.95) * se))


def p_at_least_4(pbh: float, pba: float, hfi_flags: np.ndarray) -> float:
    total = 0.0
    for outcomes in product([0, 1], repeat=7):
        if sum(outcomes) < 4:
            continue
        p = 1.0
        for g, o in enumerate(outcomes):
            p_win = float(np.clip(pbh if hfi_flags[g] else pba, 0.0, 1.0))
            p *= p_win if o else (1 - p_win)
        total += p
    return total


def regenerate_absolute_relative_error() -> None:
    slug = "2019-09-06-absolute&relative-error"
    print(f"{slug}...")
    n = 2 ** np.arange(2, 16)
    p_vals = np.array([0.01, 0.05, 0.10, 0.25, 0.5])
    reps = 10_000
    abs_err = np.empty((len(n), len(p_vals)))
    rel_err = np.empty_like(abs_err)
    for yi, nn in enumerate(n):
        for xi, p in enumerate(p_vals):
            samples = RNG.binomial(int(nn), p, size=reps) / nn
            abs_vals = np.abs(samples - p)
            abs_err[yi, xi] = abs_vals.mean()
            rel_err[yi, xi] = (abs_vals / p).mean()
    abs_err = np.log10(abs_err)
    rel_err = np.log10(rel_err)
    x = np.arange(1, 15)
    xlabels = [str(int(v)) for v in n]

    # Order matches original narrative emphasis
    abs_order = [(4, "p = 0.50"), (3, "p = 0.25"), (2, "p = 0.10"), (1, "p = 0.05"), (0, "p = 0.01")]
    fig, ax = new_fig()
    for i, (idx, label) in enumerate(abs_order):
        ax.plot(x, abs_err[:, idx], "o-", color=PALETTE[i], label=label, markerfacecolor=MARKER_FACE, markeredgewidth=1.2)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=90)
    ax.set_xlim(0.5, 14.5)
    finish_axes(ax, "Absolute error vs sample size", "N (log₂ scale)", "log₁₀(absolute error)")
    style_legend(ax.legend(loc="upper right"))
    size = save_chart(ROOT / f"img/posts/{slug}/absolute-error.png", fig)
    update_post_image_dims(slug, "absolute-error.png", size, "Absolute error versus sample size on a log10 scale")

    rel_order = [(0, "p = 0.01"), (1, "p = 0.05"), (2, "p = 0.10"), (3, "p = 0.25"), (4, "p = 0.50")]
    fig, ax = new_fig()
    for i, (idx, label) in enumerate(rel_order):
        ax.plot(x, rel_err[:, idx], "o-", color=PALETTE[i], label=label, markerfacecolor=MARKER_FACE, markeredgewidth=1.2)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=90)
    ax.set_xlim(0.5, 14.5)
    finish_axes(ax, "Relative error vs sample size", "N (log₂ scale)", "log₁₀(relative error)")
    style_legend(ax.legend(loc="upper right"))
    size = save_chart(ROOT / f"img/posts/{slug}/relative-error.png", fig)
    update_post_image_dims(slug, "relative-error.png", size, "Relative error versus sample size on a log10 scale")


def regenerate_roulette() -> None:
    slug = "2019-08-26-roulette-simulation"
    print(f"{slug}...")

    fig, ax = new_fig()
    for i in range(7):
        ax.plot(one_series(), color=PALETTE[i], lw=1.4, alpha=0.9)
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 300)
    finish_axes(ax, "Budget trajectories across series", "Play number", "Budget")
    size = save_chart(ROOT / f"img/posts/{slug}/budget-series.png", fig)
    update_post_image_dims(slug, "budget-series.png", size)

    B_vals = list(range(100, 1050, 50))
    earning_rate = [
        (np.mean([one_series(B=B, W=B + 100)[-1] for _ in range(1000)]) - B) / B for B in B_vals
    ]
    size = plot_line(
        B_vals,
        earning_rate,
        ROOT / f"img/posts/{slug}/budget-influence.png",
        title="How budget influences earnings",
        xlabel="Budget",
        ylabel="Mean earnings rate",
    )
    update_post_image_dims(slug, "budget-influence.png", size)

    W_vals = list(range(100, 1050, 50))
    earning = [np.mean([one_series(B=200, W=W)[-1] for _ in range(2000)]) - 200 for W in W_vals]
    size = plot_line(
        W_vals,
        earning,
        ROOT / f"img/posts/{slug}/threshold-influence.png",
        title="How the stopping threshold influences earnings",
        xlabel="Successful stopping threshold",
        ylabel="Mean earnings",
    )
    update_post_image_dims(slug, "threshold-influence.png", size)

    L_vals = list(range(10, 1010, 10))
    earning = [np.mean([one_series(B=200, W=300, L=L)[-1] for _ in range(800)]) - 200 for L in L_vals]
    size = plot_line(
        L_vals,
        earning,
        ROOT / f"img/posts/{slug}/plays-influence.png",
        title="How max plays influence earnings",
        xlabel="Maximum number of plays",
        ylabel="Mean earnings",
        marker="",
    )
    update_post_image_dims(slug, "plays-influence.png", size)

    M_vals = list(range(10, 1010, 10))
    earning = [np.mean([one_series(B=200, W=300, L=500, M=M)[-1] for _ in range(800)]) - 200 for M in M_vals]
    size = plot_line(
        M_vals,
        earning,
        ROOT / f"img/posts/{slug}/wager-limit-influence.png",
        title="How the wager limit influences earnings",
        xlabel="Casino wager limit",
        ylabel="Mean earnings",
        marker="",
    )
    update_post_image_dims(slug, "wager-limit-influence.png", size)

    times = np.array([len(one_series()) for _ in range(5000)])
    fig, ax = new_fig()
    ax.hist(times, bins=80, color=ACCENT, edgecolor=MARKER_FACE, linewidth=0.4)
    finish_axes(ax, "Plays before walking out", "Number of plays", "Frequency")
    size = save_chart(ROOT / f"img/posts/{slug}/play-times-hist.png", fig)
    update_post_image_dims(slug, "play-times-hist.png", size)


def regenerate_world_series() -> None:
    slug = "2019-09-09-world-series"
    print(f"{slug}...")
    pb = np.arange(0.5, 1.001, 0.01)
    win_prob = stats.nbinom.cdf(3, 4, pb)
    fig, ax = new_fig()
    ax.plot(pb, win_prob, color=ACCENT, lw=2.2)
    ax.fill_between(pb, win_prob, alpha=0.12, color=ACCENT)
    ax.set_xlim(0.5, 1)
    ax.set_ylim(0, 1)
    finish_axes(
        ax,
        "Probability of winning the World Series",
        "Per-game win probability (P_B)",
        "P(Braves win World Series)",
    )
    size = save_chart(ROOT / f"img/posts/{slug}/win-probability.png", fig)
    update_post_image_dims(slug, "win-probability.png", size)

    pb2 = np.arange(0.51, 1.001, 0.01)
    series_lengths = np.arange(1, 10000, 2)
    length_record = []
    for p in pb2:
        shortest = int(series_lengths[-1])
        for sl in series_lengths:
            win_threshold = int(np.ceil(sl / 2))
            if stats.nbinom.cdf(win_threshold - 1, win_threshold, p) >= 0.8:
                shortest = int(sl)
                break
        length_record.append(shortest)
    fig, ax = new_fig()
    ax.plot(pb2, length_record, color=LINK, lw=2.2)
    ax.fill_between(pb2, length_record, alpha=0.10, color=LINK)
    ax.set_xlim(0.5, 1)
    finish_axes(
        ax,
        "Shortest series for ≥80% win probability",
        "Per-game win probability (P_B)",
        "Series length",
    )
    size = save_chart(ROOT / f"img/posts/{slug}/shortest-series.png", fig)
    update_post_image_dims(slug, "shortest-series.png", size)


def regenerate_home_advantage() -> None:
    slug = "2019-09-12-home-advantage"
    print(f"{slug}...")
    hfi = np.array([0, 0, 1, 1, 1, 0, 0], dtype=bool)

    pb_list = np.arange(0, 1.001, 0.01)
    diff_list = []
    for pb in pb_list:
        adv = 1.1
        pnh = 1 - stats.binom.cdf(3, 7, pb)
        ph = p_at_least_4(pb * adv, 1 - (1 - pb) * adv, hfi)
        diff_list.append(pnh - ph)
    fig, ax = new_fig()
    ax.plot(pb_list, diff_list, color=ACCENT, lw=2.2)
    ax.axhline(0, color=SPINE, lw=1)
    ax.fill_between(pb_list, diff_list, 0, where=np.array(diff_list) >= 0, color=ACCENT, alpha=0.12)
    ax.fill_between(pb_list, diff_list, 0, where=np.array(diff_list) < 0, color=MISS, alpha=0.12)
    finish_axes(ax, "Home-field effect vs P_B", "P_B", "Δ win probability (no HA − with HA)")
    size = save_chart(ROOT / f"img/posts/{slug}/diff-vs-pb.png", fig)
    update_post_image_dims(slug, "diff-vs-pb.png", size)

    ha_list = np.arange(1.0, 2.001, 0.01)
    diff_list2 = []
    pb = 0.55
    for adv in ha_list:
        pnh = 1 - stats.binom.cdf(3, 7, pb)
        ph = p_at_least_4(pb * adv, 1 - (1 - pb) * adv, hfi)
        diff_list2.append(pnh - ph)
    fig, ax = new_fig()
    ax.plot(ha_list, diff_list2, color=LINK, lw=2.2)
    ax.fill_between(ha_list, diff_list2, alpha=0.10, color=LINK)
    finish_axes(
        ax,
        "Home-field effect vs advantage factor",
        "Home-field advantage factor",
        "Δ win probability (no HA − with HA)",
    )
    size = save_chart(ROOT / f"img/posts/{slug}/diff-vs-advantage.png", fig)
    update_post_image_dims(slug, "diff-vs-advantage.png", size)


def regenerate_quantile_precision() -> None:
    slug = "2019-09-18-quantile-precision"
    print(f"{slug}...")
    sample_size = 200
    test_num = 5000

    def save_pair(qs, lengths, dens, stem_q, stem_d, title_q, title_d, alt_q, alt_d):
        size = plot_line(
            qs,
            lengths,
            ROOT / f"img/posts/{slug}/{stem_q}",
            title=title_q,
            xlabel="p-th quantile",
            ylabel="Length of middle 95%",
            xticks=qs,
        )
        update_post_image_dims(slug, stem_q, size, alt_q)
        size = plot_density_scatter(
            dens,
            lengths,
            qs,
            ROOT / f"img/posts/{slug}/{stem_d}",
            title=title_d,
        )
        update_post_image_dims(slug, stem_d, size, alt_d)

    qs, lengths = mid95_lengths(lambda n: RNG.normal(size=n), sample_size, test_num)
    save_pair(
        qs,
        lengths,
        stats.norm.pdf(stats.norm.ppf(qs)),
        "prob5-s1.png",
        "prob5-s2.png",
        "Normal distribution: middle-95% length by quantile",
        "Normal distribution: middle-95% length by density",
        "Middle 95 percent length by quantile for the normal distribution",
        "Middle 95 percent length versus normal density",
    )

    qs, lengths = mid95_lengths(lambda n: RNG.exponential(size=n), sample_size, test_num)
    save_pair(
        qs,
        lengths,
        stats.expon.pdf(stats.expon.ppf(qs)),
        "prob5-e1.png",
        "prob5-e2.png",
        "Exponential distribution: middle-95% length by quantile",
        "Exponential distribution: middle-95% length by density",
        "Middle 95 percent length by quantile for the exponential distribution",
        "Middle 95 percent length versus exponential density",
    )

    def rf3(n):
        g = RNG.choice([0, 1, 2], size=n, p=[0.5, 0.3, 0.2])
        out = np.empty(n)
        out[g == 0] = RNG.normal(size=int((g == 0).sum()))
        out[g == 1] = RNG.normal(loc=4, size=int((g == 1).sum()))
        out[g == 2] = RNG.normal(loc=-4, scale=2, size=int((g == 2).sum()))
        return out

    def pf3(x):
        return 0.5 * stats.norm.cdf(x) + 0.3 * stats.norm.cdf(x, loc=4) + 0.2 * stats.norm.cdf(x, loc=-4, scale=2)

    def df3(x):
        return 0.5 * stats.norm.pdf(x) + 0.3 * stats.norm.pdf(x, loc=4) + 0.2 * stats.norm.pdf(x, loc=-4, scale=2)

    qs, lengths = mid95_lengths(rf3, sample_size, test_num)
    qf3 = np.array([brentq(lambda x, q=q: pf3(x) - q, -20, 20) for q in qs])
    save_pair(
        qs,
        lengths,
        df3(qf3),
        "prob5-m31.png",
        "prob5-m32.png",
        "Mixture 3: middle-95% length by quantile",
        "Mixture 3: middle-95% length by density",
        "Middle 95 percent length by quantile for mixture distribution 3",
        "Middle 95 percent length versus density for mixture distribution 3",
    )

    def rf4(n):
        g = RNG.integers(0, 2, size=n)
        out = np.empty(n)
        out[g == 0] = RNG.beta(5, 1, size=int((g == 0).sum()))
        out[g == 1] = RNG.beta(1, 5, size=int((g == 1).sum()))
        return out

    def pf4(x):
        return 0.5 * stats.beta.cdf(x, 5, 1) + 0.5 * stats.beta.cdf(x, 1, 5)

    def df4(x):
        return 0.5 * stats.beta.pdf(x, 5, 1) + 0.5 * stats.beta.pdf(x, 1, 5)

    qs, lengths = mid95_lengths(rf4, sample_size, test_num)
    qf4 = np.array([brentq(lambda x, q=q: pf4(x) - q, 1e-6, 1 - 1e-6) for q in qs])
    save_pair(
        qs,
        lengths,
        df4(qf4),
        "prob5-m41.png",
        "prob5-m42.png",
        "Mixture 4: middle-95% length by quantile",
        "Mixture 4: middle-95% length by density",
        "Middle 95 percent length by quantile for mixture distribution 4",
        "Middle 95 percent length versus density for mixture distribution 4",
    )

    qs = np.arange(0.05, 0.96, 0.05)
    series = []
    dens_series = []
    dens = stats.norm.pdf(stats.norm.ppf(qs))
    for n in (400, 800, 1600):
        _, lengths = mid95_lengths(lambda m, nn=n: RNG.normal(size=m), n, test_num)
        series.append((qs, lengths, f"n = {n}"))
        dens_series.append((dens, lengths, f"n = {n}"))
    size = plot_multi_lines(
        series,
        ROOT / f"img/posts/{slug}/prob5-o1.png",
        title="Normal middle-95% length across sample sizes",
        xlabel="p-th quantile",
        ylabel="Length of middle 95%",
        xticks=qs,
        legend_title="Sample size",
    )
    update_post_image_dims(slug, "prob5-o1.png", size)
    size = plot_multi_density_scatter(
        dens_series,
        ROOT / f"img/posts/{slug}/prob5-o2.png",
        title="Normal middle-95% length by density across sample sizes",
        legend_title="Sample size",
    )
    update_post_image_dims(slug, "prob5-o2.png", size)


def regenerate_coverage() -> None:
    slug = "2019-10-15-coverage-probability"
    print(f"{slug}...")
    n = 201
    n_samples = 1000
    samples = RNG.normal(size=(n, n_samples))
    means = samples.mean(axis=0)
    sds = samples.std(axis=0, ddof=1)
    lo = np.empty(n_samples)
    hi = np.empty(n_samples)
    for j in range(n_samples):
        meds = np.median(RNG.normal(loc=means[j], scale=sds[j], size=(n, n)), axis=1)
        lo[j], hi[j] = np.quantile(meds, [0.025, 0.975])
    captured = (lo <= 0) & (hi >= 0)

    # Sort for readability: misses first, then captures
    order = np.argsort(~captured)
    lo, hi, captured = lo[order], hi[order], captured[order]
    y = np.arange(n_samples)

    fig, ax = plt.subplots(figsize=(7.2, 9.0))
    for i in range(n_samples):
        color = CAPTURE if captured[i] else MISS
        ax.hlines(y[i], lo[i], hi[i], colors=color, lw=0.7, alpha=0.85)
    ax.axvline(0, color=INK, lw=1.0, alpha=0.55)
    finish_axes(ax, "95% median intervals", "Estimated median", "Simulation index")
    ax.set_yticks([])
    # Custom legend proxies
    ax.plot([], [], color=CAPTURE, lw=2, label="Covers 0")
    ax.plot([], [], color=MISS, lw=2, label="Misses 0")
    style_legend(ax.legend(loc="upper right"))
    size = save_chart(ROOT / f"img/posts/{slug}/coverage-intervals.png", fig)
    update_post_image_dims(
        slug,
        "coverage-intervals.png",
        size,
        "Ninety-five percent confidence intervals for the median; rust intervals miss zero",
    )


def regenerate_clt() -> None:
    slug = "2019-11-12-clt"
    print(f"{slug}...")
    r_reps = 5000
    location = 0
    scale = 1
    slants = [0, 2, 10, 100]
    ns = [5, 10, 20, 40]
    x = np.arange(-2, 2.01, 0.01)

    def qq_pair(alpha, n):
        delta = alpha / np.sqrt(1 + alpha**2)
        pop_mean = location + scale * delta * np.sqrt(2 / np.pi)
        pop_sd = np.sqrt(scale**2 * (1 - (2 * delta**2) / np.pi))
        sample_dist_clt = RNG.normal(size=r_reps) * (pop_sd / np.sqrt(n)) + pop_mean
        data = stats.skewnorm.rvs(alpha, loc=location, scale=scale, size=(r_reps, n), random_state=RNG)
        return sample_dist_clt, data.mean(axis=1)

    fig, axes = plt.subplots(4, 5, figsize=(11.5, 9.0))
    for i, alpha in enumerate(slants):
        ax0 = axes[i, 0]
        ax0.plot(x, stats.skewnorm.pdf(x, alpha, loc=location, scale=scale), color=ACCENT, lw=1.8)
        ax0.fill_between(x, stats.skewnorm.pdf(x, alpha, loc=location, scale=scale), color=ACCENT, alpha=0.12)
        ax0.set_xticks([])
        ax0.set_yticks([])
        for spine in ax0.spines.values():
            spine.set_color(SPINE)
        ax0.set_ylabel(f"slant = {alpha}", color=INK, fontproperties=LABEL_FP)
        if i == 0:
            ax0.set_title("Distribution", color=INK, loc="left", fontproperties=LABEL_FP)

        for j, n in enumerate(ns):
            ax = axes[i, j + 1]
            clt, sim = qq_pair(alpha, n)
            qx = np.quantile(clt, np.linspace(0.01, 0.99, 180))
            qy = np.quantile(sim, np.linspace(0.01, 0.99, 180))
            ax.scatter(qx, qy, s=6, color=LINK, alpha=0.55, linewidths=0)
            lims = [min(qx.min(), qy.min()), max(qx.max(), qy.max())]
            ax.plot(lims, lims, color=INK, lw=1.0, alpha=0.7)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_color(SPINE)
            if i == 0:
                ax.set_title(f"N = {n}", color=INK, loc="left", fontproperties=LABEL_FP)

    fig.suptitle(
        "CLT vs simulation QQ-plots under skew-normal slant",
        color=INK,
        x=0.01,
        ha="left",
        fontproperties=TITLE_FP,
    )
    fig.tight_layout(rect=[0.02, 0.02, 1, 0.96])
    size = save_chart(ROOT / f"img/posts/{slug}/qqplot-grid.png", fig)
    update_post_image_dims(
        slug,
        "qqplot-grid.png",
        size,
        "QQ-plot grid comparing CLT and simulation approximations across slant and sample size",
    )


def regenerate_power_correlation() -> None:
    slug = "2019-11-22-power-correlation"
    print(f"{slug}...")
    corr_list = np.arange(0.8, 0.951, 0.01)
    n_list = [25, 50, 75, 100]
    null_correlation = 0.8
    r_reps = 2000
    series = []
    for n in n_list:
        powers = []
        for rho in corr_list:
            sigma = np.array([[1.0, rho], [rho, 1.0]])
            detect = 0
            for _ in range(r_reps):
                data = RNG.multivariate_normal([0.0, 0.0], sigma, size=n)
                if one_sided_corr_lower(data[:, 0], data[:, 1]) > null_correlation:
                    detect += 1
            powers.append(detect / r_reps)
        series.append((corr_list, powers, str(n)))
    size = plot_multi_lines(
        series,
        ROOT / f"img/posts/{slug}/power-vs-correlation.png",
        title="Power versus true correlation",
        xlabel="True correlation",
        ylabel="Power",
        legend_title="N",
    )
    update_post_image_dims(slug, "power-vs-correlation.png", size)


def main() -> None:
    configure_style()
    regenerate_absolute_relative_error()
    regenerate_world_series()
    regenerate_home_advantage()
    regenerate_quantile_precision()
    regenerate_coverage()
    regenerate_clt()
    regenerate_power_correlation()
    regenerate_roulette()
    print("done")


if __name__ == "__main__":
    main()
