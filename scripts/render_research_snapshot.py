from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
METADATA = ROOT / "data" / "metadata"
OUT = ROOT / "outputs" / "figures"

BLUE = "#2F6B9A"
ORANGE = "#D97935"
GREEN = "#5B8C5A"
GRAY = "#4A5568"
LIGHT = "#EEF2F6"
INK = "#172033"


def set_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 240,
            "font.family": "DejaVu Sans",
            "font.size": 10.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": "#D9DEE7",
            "grid.linewidth": 0.8,
            "grid.alpha": 0.75,
            "legend.frameon": False,
        }
    )


def card(ax: plt.Axes, x: float, y: float, w: float, h: float, title: str, body: str, color: str) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        facecolor="#FFFFFF",
        edgecolor="#CBD5E1",
        linewidth=1.0,
    )
    ax.add_patch(box)
    title_y = y + h - 0.075 if body else y + h / 2
    title_va = "top" if body else "center"
    ax.text(x + 0.035, title_y, title, ha="left", va=title_va, fontsize=10.2, color=color, weight="bold")
    if body:
        ax.text(x + 0.035, y + h - 0.215, body, ha="left", va="top", fontsize=8.45, color=INK, linespacing=1.18)


def load_top_rows(split: str, dimension: str, n: int) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    with open(METADATA / "source_distribution.csv", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row["split"] == split and row["dimension"] == dimension:
                rows.append((row["value"], int(row["count"])))
    return sorted(rows, key=lambda item: item[1], reverse=True)[:n]


def render() -> Path:
    set_style()
    OUT.mkdir(parents=True, exist_ok=True)
    summary = json.loads((METADATA / "dataset_summary.json").read_text(encoding="utf-8-sig"))
    counts = summary["public_snapshot_counts"]

    public_domains = load_top_rows("public_exam", "law_category", 6)
    countries = load_top_rows("public_exam", "source_country", 4)

    fig = plt.figure(figsize=(12.0, 6.2), facecolor="white")
    grid = fig.add_gridspec(2, 3, height_ratios=[0.82, 1.18], width_ratios=[1.15, 1.1, 1.1])

    ax_cards = fig.add_subplot(grid[0, :])
    ax_cards.axis("off")
    ax_cards.set_xlim(0, 1)
    ax_cards.set_ylim(0, 1)
    fig.suptitle("LegalBenchPro public research snapshot", x=0.04, y=0.985, ha="left", fontsize=18, weight="bold", color=INK)
    fig.text(
        0.04,
        0.925,
        "Open-ended legal-reasoning benchmark preview with documented release constraints and reproducible sample extraction.",
        ha="left",
        fontsize=10.5,
        color=GRAY,
    )

    card(
        ax_cards,
        0.015,
        0.06,
        0.30,
        0.72,
        "Task coverage",
        f"{counts['main_task_instances']:,} task instances\n"
        f"{counts['cn_real_case_issue_stance_prompts']} Chinese real-case prompts\n"
        f"{counts['public_exam_instances']} public-exam items",
        BLUE,
    )
    card(
        ax_cards,
        0.35,
        0.06,
        0.30,
        0.72,
        "Model matrix",
        f"{counts['model_configurations']} model configurations\n"
        f"{counts['main_multimodel_response_cells']:,} response cells\n"
        "standard, reasoning, and prompt variants",
        ORANGE,
    )
    card(
        ax_cards,
        0.685,
        0.06,
        0.30,
        0.72,
        "Validation design",
        f"{counts['human_cn_pilot_rows']} real-case pilot rows\n"
        f"{counts['human_bar_pilot_rows']} public-exam pilot rows\n"
        "rubric and audit workflow documented",
        GREEN,
    )

    ax_split = fig.add_subplot(grid[1, 0])
    split_labels = ["CN real-case", "Public exam"]
    split_counts = [counts["cn_real_case_issue_stance_prompts"], counts["public_exam_instances"]]
    ax_split.bar(split_labels, split_counts, color=[BLUE, ORANGE], width=0.55)
    ax_split.set_title("Public preview task splits", weight="bold", loc="left")
    ax_split.set_ylabel("Rows")
    for idx, value in enumerate(split_counts):
        ax_split.text(idx, value + 18, f"{value:,}", ha="center", va="bottom", color=GRAY, fontsize=10)
    ax_split.set_ylim(0, max(split_counts) * 1.22)

    ax_domains = fig.add_subplot(grid[1, 1])
    domain_labels = [name if len(name) <= 23 else name[:21] + "..." for name, _ in public_domains][::-1]
    domain_values = [count for _, count in public_domains][::-1]
    ax_domains.barh(domain_labels, domain_values, color=BLUE)
    ax_domains.set_title("Largest public-exam domains", weight="bold", loc="left")
    ax_domains.set_xlabel("Rows")
    for i, value in enumerate(domain_values):
        ax_domains.text(value + 4, i, str(value), va="center", color=GRAY, fontsize=9)

    ax_countries = fig.add_subplot(grid[1, 2])
    country_labels = [name for name, _ in countries]
    country_values = [count for _, count in countries]
    ax_countries.pie(
        country_values,
        labels=country_labels,
        colors=[BLUE, ORANGE, GREEN, "#7C8DA5"],
        startangle=90,
        counterclock=False,
        textprops={"fontsize": 9},
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax_countries.set_title("Jurisdiction sources", weight="bold", loc="left")

    fig.tight_layout(rect=[0.03, 0.02, 0.99, 0.9])
    output = OUT / "research_snapshot.png"
    fig.savefig(output, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output


if __name__ == "__main__":
    print(render())
