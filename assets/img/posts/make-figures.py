"""
Rebuild blog-post thumbnails as abstract, on-brand visuals.

All figures share the same language: dark background, dense purple pattern,
sparse orange accents, no axes, no labels.

Output: 1200x1200 PNGs in this directory.
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
from scipy.interpolate import make_smoothing_spline

# ── Brand palette ─────────────────────────────────────────────────────
BG         = "#191B23"   # near-black background
PURPLE     = "#8B4FA6"  # primary line color on dark
ORANGE     = "#FF8E2C"   # sparse accent

OUT = Path(__file__).parent
NOTO_PATH = "/Users/quentin/Documents/FLAIR/brand/assets/fonts/NotoSans-VariableFont_wdth,wght.ttf"
font_manager.fontManager.addfont(NOTO_PATH)
mpl.rcParams["font.family"] = "Noto Sans"
mpl.rcParams["axes.unicode_minus"] = False


def _canvas():
    fig = plt.figure(figsize=(12, 9))
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes((0, 0, 1, 1))     # axes fills the entire 12x9 figure
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def _save(fig, name: str) -> Path:
    path = OUT / name
    # No bbox_inches="tight" — keeps the full 12x9 output even when
    # set_aspect("equal") shrinks the axes (leaving brand-dark padding L/R).
    fig.savefig(path, facecolor=BG, dpi=100, pad_inches=0.0)
    plt.close(fig)
    return path


# ──────────────────────────────────────────────────────────────────────
# umap.png — Two-cluster wave field (the reference design)
# ──────────────────────────────────────────────────────────────────────
def make_umap() -> Path:
    fig, ax = _canvas()
    x = np.linspace(0.05, 0.95, 600)
    N = 70

    def line(t: float) -> np.ndarray:
        base = 0.05 + 0.9 * t
        amp = 0.32 * (4 * t * (1 - t)) ** 1.2
        bump_a = np.exp(-((x - 0.42) / 0.10) ** 2) * 0.55
        bump_b = np.exp(-((x - 0.74) / 0.13) ** 2) * 0.45
        return base + amp * (bump_a + bump_b) * (0.5 + 0.5 * np.sin(3.2 * t * np.pi))

    for i in range(N):
        t = (i + 0.5) / N
        alpha = 0.55 + 0.40 * (1 - abs(t - 0.5) * 2)
        ax.plot(x, line(t), color=PURPLE, linewidth=1.6, alpha=alpha)

    for t_hl in (0.32, 0.68):
        ax.plot(x, line(t_hl), color=ORANGE, linewidth=3.2, alpha=0.95)

    return _save(fig, "umap.png")


# ──────────────────────────────────────────────────────────────────────
# stats.png — Ridge-plot fan: many Gaussians stacked vertically,
# centered at 0, with amplitude/width that swells through the middle.
# ──────────────────────────────────────────────────────────────────────
def make_stats() -> Path:
    """Sample paths around a wandering trend, with a shaded confidence band
    bounded by orange lines.
    """
    fig, ax = _canvas()

    rng = np.random.default_rng(5)
    N = 80
    T = 400
    x = np.linspace(0.04, 0.96, T)

    # Wandering trend — cumulative random walk, smoothed with a moving average
    # so it evolves visibly but stays smoother than the individual paths.
    window = 35
    drift_raw = np.cumsum(rng.normal(0, 1, T + window)) * 0.0055
    drift_smooth = np.convolve(drift_raw, np.ones(window) / window, mode="valid")
    trend = drift_smooth[:T]
    trend = trend - trend[0] + 0.5

    # Sample paths = trend + individual random-walk noise
    paths = np.empty((N, T))
    for i in range(N):
        noise = np.cumsum(rng.normal(0, 1, T)) * 0.01
        paths[i] = trend + (noise - noise[0])

    # Empirical 95% confidence band
    lo_band = np.percentile(paths, 20, axis=0)
    hi_band = np.percentile(paths, 80, axis=0)

    # Shaded band
    ax.fill_between(x, lo_band, hi_band, color=ORANGE, alpha=0.18, linewidth=0)

    # Sample paths
    for i in range(N):
        ax.plot(x, paths[i], color=PURPLE, linewidth=1.4, alpha=0.55)

    # CI boundary lines on top of the paths
    ax.plot(x, lo_band, color=ORANGE, linewidth=1.6, alpha=0.85)
    ax.plot(x, hi_band, color=ORANGE, linewidth=1.6, alpha=0.85)

    # Smoothing spline of the empirical mean — the orange "average".
    # Bands stay noisy (empirical percentiles); only the central tendency
    # is smoothed.
    mean_path = paths.mean(axis=0)
    spline = make_smoothing_spline(x, mean_path)
    ax.plot(x, spline(x), color=ORANGE, linewidth=3.0, alpha=0.95)

    return _save(fig, "stats.png")


# ──────────────────────────────────────────────────────────────────────
# visualization.png — Phyllotaxis (sunflower) spiral of dots.
# Golden-angle placement; mostly purple, three orange radial "arms".
# ──────────────────────────────────────────────────────────────────────
def make_visualization() -> Path:
    fig, ax = _canvas()
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal")

    N = 800
    golden_angle = np.pi * (3 - np.sqrt(5))
    idx = np.arange(N)
    r = np.sqrt(idx / N) * 0.96
    theta = idx * golden_angle
    xs = r * np.cos(theta)
    ys = r * np.sin(theta)

    sizes = 14 + 70 * (idx / N) ** 1.5

    rng = np.random.default_rng(11)
    orange_mask = np.zeros(N, dtype=bool)
    for arm_theta in (0.6, 0.6 + 2 * np.pi / 3, 0.6 + 4 * np.pi / 3):
        delta = ((theta - arm_theta + np.pi) % (2 * np.pi)) - np.pi
        orange_mask |= (np.abs(delta) < 0.10) & (r > 0.25)
    orange_mask |= rng.random(N) < 0.1

    ax.scatter(
        xs[~orange_mask], ys[~orange_mask],
        s=sizes[~orange_mask], color=PURPLE,
        alpha=0.78, edgecolors="none",
    )
    ax.scatter(
        xs[orange_mask], ys[orange_mask],
        s=sizes[orange_mask] * 1.15, color=ORANGE,
        alpha=0.95, edgecolors="none",
    )

    return _save(fig, "visualization.png")


# ──────────────────────────────────────────────────────────────────────
# xgboost.png — Organic tree with curved branches and a blossoming
# orange canopy. Purple trunk and limbs, orange tendrils and dots at
# the leaves. No labels — pure structure.
# ──────────────────────────────────────────────────────────────────────
def make_xgboost() -> Path:
    fig, ax = _canvas()
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1, 1.3)
    ax.set_aspect("equal")

    rng = np.random.default_rng(2)

    def curved_segment(x1, y1, x2, y2, curvature):
        """Quadratic Bezier from (x1,y1) to (x2,y2), bent perpendicular by curvature."""
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        length = float(np.hypot(dx, dy)) or 1.0
        px, py = -dy / length, dx / length
        cx, cy = mx + px * curvature, my + py * curvature
        t = np.linspace(0, 1, 40)
        bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
        by = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
        return bx, by

    def blossom(x: float, y: float, parent_angle: float, parent_length: float) -> None:
        """A spray of fine orange tendrils ending in dots — replaces the single leaf."""
        n = rng.integers(5, 9)
        for _ in range(n):
            ang = parent_angle + rng.uniform(-0.85, 0.85)
            length = parent_length * rng.uniform(0.35, 0.75)
            curv = rng.uniform(-0.04, 0.04)
            x2 = x + length * np.cos(ang)
            y2 = y + length * np.sin(ang)
            bx, by = curved_segment(x, y, x2, y2, curv)
            ax.plot(bx, by, color=ORANGE, linewidth=rng.uniform(1.4, 2.6),
                    alpha=rng.uniform(0.75, 0.95), solid_capstyle="round")
            ax.scatter([x2], [y2], s=rng.uniform(50, 110), color=ORANGE,
                       alpha=0.95, edgecolors="none", zorder=3)

    def branch(x: float, y: float, angle: float, length: float,
               depth: int, max_depth: int) -> None:
        x2 = x + length * np.cos(angle)
        y2 = y + length * np.sin(angle)
        lw = max(6.0, 16 - depth * 2)   # medium trunk, leaves stay at 6
        is_leaf = depth == max_depth

        # Curvature grows with depth — trunk straight, twigs wandering
        curv = rng.uniform(-0.025 - 0.012 * depth, 0.025 + 0.012 * depth)
        bx, by = curved_segment(x, y, x2, y2, curv)
        ax.plot(bx, by, color=PURPLE, linewidth=lw,
                alpha=0.92 - depth * 0.04, solid_capstyle="round")

        if is_leaf:
            blossom(x2, y2, angle, length)
            return

        spread = 0.55 - 0.05 * depth + rng.uniform(-0.12, 0.12)
        new_length = length * (0.74 + rng.uniform(-0.08, 0.08))
        if rng.uniform() > 0.02:
            branch(x2, y2, angle - spread, new_length, depth + 1, max_depth)
        if rng.uniform() > 0.02:
            branch(x2, y2, angle + spread, new_length, depth + 1, max_depth)

    branch(0.0, -0.85, np.pi / 2, 0.55, 0, 7)

    return _save(fig, "xgboost.png")


# ──────────────────────────────────────────────────────────────────────
# writing.png — Dense field of wavy "text" lines with occasional
# struck-through orange revisions. Like a manuscript seen from afar.
# ──────────────────────────────────────────────────────────────────────
def make_writing() -> Path:
    fig, ax = _canvas()

    rng = np.random.default_rng(4)
    x_dense = np.linspace(0, 1, 600)
    N = 40
    top, bot = 0.94, 0.06
    spacing = (top - bot) / (N - 1)

    lengths = rng.uniform(0.55, 0.95, N)
    for i in rng.choice(N, size=N // 6, replace=False):
        lengths[i] *= rng.uniform(0.35, 0.55)
    starts = np.full(N, 0.10)

    highlights = set(rng.choice(N, size=4, replace=False))

    for i in range(N):
        y = top - i * spacing
        length = lengths[i]
        x = x_dense[(x_dense >= starts[i]) & (x_dense <= starts[i] + length * 0.78)]
        jitter = 0.002 * np.sin(x * 30 + i * 0.9) + 0.0008 * np.cos(x * 90 + i * 2.1)
        y_arr = np.full_like(x, y) + jitter

        if i in highlights:
            ax.plot(x, y_arr, color=ORANGE, linewidth=3.2,
                    alpha=0.95, solid_capstyle="round")
            x_strike = x[len(x) // 5 : -len(x) // 5]
            ax.plot(x_strike, np.full_like(x_strike, y),
                    color=ORANGE, linewidth=1.0, alpha=0.55,
                    solid_capstyle="round")
        else:
            ax.plot(x, y_arr, color=PURPLE, linewidth=2.4,
                    alpha=0.72, solid_capstyle="round")

    return _save(fig, "writing.png")


if __name__ == "__main__":
    print(make_umap())
    print(make_stats())
    print(make_visualization())
    print(make_xgboost())
    print(make_writing())
