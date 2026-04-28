from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data" / "metadata" / "dataset_summary.json"
DISTRIBUTION_PATH = ROOT / "data" / "metadata" / "source_distribution.csv"
OUT_PATH = ROOT / "outputs" / "figures" / "benchmark_overview.png"


COLORS = {
    "navy": "#1f2a44",
    "blue": "#2f6f9f",
    "orange": "#d8792f",
    "green": "#5f8f5f",
    "gray": "#5f6b7a",
    "light_gray": "#edf1f5",
    "grid": "#c9d2df",
}


def load_distribution() -> list[dict[str, str]]:
    with DISTRIBUTION_PATH.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def get_distribution(rows: list[dict[str, str]], split: str, dimension: str) -> list[tuple[str, int]]:
    out = []
    for row in rows:
        if row["split"] == split and row["dimension"] == dimension:
            out.append((row["value"], int(row["count"])))
    return out


def draw_kpi(ax, x: float, y: float, w: float, h: float, value: str, label: str, color: str) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.018,rounding_size=0.02",
        linewidth=1.0,
        edgecolor="#d5dde8",
        facecolor="#f8fafc",
        transform=ax.transAxes,
    )
    ax.add_patch(box)
    ax.text(x + 0.04, y + h * 0.60, value, transform=ax.transAxes, fontsize=21,
            fontweight="bold", color=color, va="center")
    ax.text(x + 0.04, y + h * 0.30, label, transform=ax.transAxes, fontsize=10.5,
            color=COLORS["gray"], va="center")


def style_axis(ax) -> None:
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(COLORS["grid"])
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", colors=COLORS["gray"], labelsize=9)
    ax.grid(axis="x", color=COLORS["grid"], alpha=0.55, linewidth=0.8)


def main() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8-sig"))
    counts = summary["public_snapshot_counts"]
    rows = load_distribution()

    country_rows = get_distribution(rows, "public_exam", "source_country")
    cn_law_rows = get_distribution(rows, "real_case_cn", "law_category")
    stance_rows = get_distribution(rows, "real_case_cn", "stance")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "figure.dpi": 120,
        "savefig.dpi": 180,
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
    })

    fig = plt.figure(figsize=(13.5, 8.0), facecolor="white", constrained_layout=True)
    grid = fig.add_gridspec(3, 2, height_ratios=[0.92, 1.45, 1.25], width_ratios=[1, 1])

    title_ax = fig.add_subplot(grid[0, :])
    title_ax.axis("off")
    title_ax.text(
        0.0,
        0.94,
        "LegalBenchPro public preview overview",
        transform=title_ax.transAxes,
        fontsize=23,
        fontweight="bold",
        color=COLORS["navy"],
        va="top",
    )
    title_ax.text(
        0.0,
        0.70,
        "Benchmark-in-progress for LLM legal reasoning across public exams and de-identified Chinese civil cases.",
        transform=title_ax.transAxes,
        fontsize=11.5,
        color=COLORS["gray"],
        va="top",
    )

    kpis = [
        (f"{counts['main_task_instances']:,}", "task instances", COLORS["blue"]),
        (f"{counts['main_multimodel_response_cells']:,}", "LLM response cells", COLORS["orange"]),
        (f"{counts['model_configurations']}", "model configurations", COLORS["green"]),
        (
            f"{counts['human_cn_pilot_rows'] + counts['human_bar_pilot_rows']}",
            "human-validation pilot rows",
            COLORS["navy"],
        ),
    ]
    for idx, (value, label, color) in enumerate(kpis):
        draw_kpi(title_ax, 0.01 + idx * 0.245, 0.05, 0.22, 0.42, value, label, color)

    split_ax = fig.add_subplot(grid[1, 0])
    split_labels = ["Public legal exams", "Chinese real-case prompts"]
    split_values = [counts["public_exam_instances"], counts["cn_real_case_issue_stance_prompts"]]
    split_colors = [COLORS["blue"], COLORS["green"]]
    split_ax.barh(split_labels[::-1], split_values[::-1], color=split_colors[::-1], height=0.52)
    for y, value in enumerate(split_values[::-1]):
        split_ax.text(value + 18, y, f"{value:,}", va="center", fontsize=11, color=COLORS["navy"])
    split_ax.set_title("Task-instance split", loc="left", color=COLORS["navy"])
    split_ax.set_xlim(0, max(split_values) * 1.24)
    style_axis(split_ax)

    country_ax = fig.add_subplot(grid[1, 1])
    countries = [name for name, _ in country_rows]
    country_counts = [count for _, count in country_rows]
    country_ax.barh(countries[::-1], country_counts[::-1], color=COLORS["blue"], height=0.52)
    for y, value in enumerate(country_counts[::-1]):
        country_ax.text(value + 10, y, f"{value:,}", va="center", fontsize=10.5, color=COLORS["navy"])
    country_ax.set_title("Public-exam source coverage", loc="left", color=COLORS["navy"])
    country_ax.set_xlim(0, max(country_counts) * 1.22)
    style_axis(country_ax)

    law_ax = fig.add_subplot(grid[2, 0])
    law_labels = [name for name, _ in cn_law_rows]
    law_counts = [count for _, count in cn_law_rows]
    law_ax.barh(law_labels[::-1], law_counts[::-1], color=[COLORS["green"], COLORS["orange"], COLORS["blue"]][::-1], height=0.52)
    for y, value in enumerate(law_counts[::-1]):
        law_ax.text(value + 1.2, y, f"{value}", va="center", fontsize=10.5, color=COLORS["navy"])
    law_ax.set_title("Chinese real-case legal domains", loc="left", color=COLORS["navy"])
    law_ax.set_xlim(0, max(law_counts) * 1.28)
    style_axis(law_ax)

    stance_ax = fig.add_subplot(grid[2, 1])
    stance_labels = [name.replace(" court result", "") for name, _ in stance_rows]
    stance_counts = [count for _, count in stance_rows]
    stance_ax.barh(stance_labels[::-1], stance_counts[::-1], color=[COLORS["orange"], COLORS["green"]][::-1], height=0.52)
    for y, value in enumerate(stance_counts[::-1]):
        stance_ax.text(value + 0.8, y, f"{value}", va="center", fontsize=10.5, color=COLORS["navy"])
    stance_ax.set_title("Paired stance design", loc="left", color=COLORS["navy"])
    stance_ax.set_xlim(0, max(stance_counts) * 1.32)
    style_axis(stance_ax)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
