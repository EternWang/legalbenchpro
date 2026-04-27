from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path
from urllib.parse import urlparse

from openpyxl import load_workbook

from legalbenchpro.workbook import clip_text, detect_model_headers, summarize_workbook


CN = {
    "review_id": 0,
    "document_id": 1,
    "case_theme": 2,
    "issue_id": 3,
    "issue_title": 4,
    "stance": 6,
    "core_issue": 7,
    "prompt": 8,
    "cited_authority": 9,
    "court_level": 12,
    "case_type": 13,
    "law_category": 14,
    "law_category_detail": 15,
}
CN_FIRST_MODEL_ANSWER = 17
CN_FIRST_MODEL_SCORES = (18, 19, 20)

BAR = {
    "review_id": 0,
    "document_id": 1,
    "issue_id": 3,
    "issue_title": 4,
    "prompt": 5,
    "reference_answer": 6,
    "source_country": 8,
    "source_legal_system": 9,
    "law_category": 10,
    "law_category_detail": 11,
    "source_body": 12,
    "source_url": 13,
}
BAR_FIRST_MODEL_ANSWER = 14
BAR_FIRST_MODEL_SCORE = 15

CN_SAMPLE_FIELDS = [
    "review_id",
    "document_id",
    "issue_id",
    "issue_title_en",
    "case_type_en",
    "law_category",
    "stance",
    "task_preview",
    "court_result_preview",
    "example_model",
    "example_answer_preview",
    "score_summary",
]

BAR_SAMPLE_FIELDS = [
    "review_id",
    "document_id",
    "issue_id",
    "issue_title_en",
    "source_country",
    "source_legal_system",
    "law_category",
    "task_preview",
    "reference_answer_preview",
    "example_model",
    "example_answer_preview",
    "answer_match_score",
]

CN_DETAIL_TO_CASE_TYPE_EN = {
    "Medical Malpractice": "Medical malpractice liability dispute",
    "Motor Vehicle Accident": "Motor vehicle accident liability dispute",
    "Nuisance / Removal of Obstruction": "Removal-of-obstruction dispute",
    "Personal Injury": "Life, bodily integrity, and health-rights dispute",
    "Real Estate Sale Contract": "Real-estate sales contract dispute",
    "Sales Contract": "Sales contract dispute",
    "Service / Work Contract": "Work/service and supply-installation contract dispute",
}

CN_ISSUE_EN = {
    "CASE-001-I01": "Whether the buyer's payment obligation was triggered after equipment acceptance",
    "CASE-001-I02": "How the overdue-payment liquidated-damages rate should be evaluated",
    "CASE-001-I03": "Whether liquidated damages should be calculated by payment milestone or by total price",
    "CASE-002-I01": "Whether objections by two hospitals required a renewed expert appraisal",
    "CASE-006-I01": "Whether elevator-installation participants may remove obstruction despite voting defects",
    "CASE-007-I01": "Whether claims for remaining supply-installation payments were time-barred",
    "CASE-011-I01": "Whether the court should order continued property-transfer registration",
}

CN_COURT_RESULT_EN = {
    "CASE-001-I01": "Court result: payment obligations were triggered after delivery, acceptance/use records, and no timely quality objection.",
    "CASE-001-I02": "Court result: the contract's high liquidated-damages rate was reduced rather than applied mechanically.",
    "CASE-001-I03": "Court result: liquidated damages should be calculated by separate payment milestones rather than the total contract price.",
    "CASE-002-I01": "Court result: written objections by hospitals did not require reopening the appraisal procedure.",
    "CASE-006-I01": "Court result: voting defects did not by themselves defeat the elevator plan, and obstruction could be removed.",
    "CASE-007-I01": "Court result: the supplier's remaining-payment and additional-cost claims were time-barred.",
    "CASE-011-I01": "Court result: the seller was ordered to continue performance and assist with property-transfer registration.",
}

HAN_RE = re.compile(r"[\u3400-\u9fff]")


def cell(row: tuple[object, ...], index: int) -> object:
    return row[index] if index < len(row) else None


def text(row: tuple[object, ...], index: int, limit: int) -> str:
    return clip_text(cell(row, index), limit)


def has_han(value: str) -> bool:
    return bool(HAN_RE.search(value))


def english_or_generic(value: str, fallback: str, limit: int) -> str:
    if not value or has_han(value):
        return clip_text(fallback, limit)
    return clip_text(value, limit)


def safe_identifier(value: str, fallback: str, limit: int) -> str:
    if not value or has_han(value):
        return clip_text(fallback, limit)
    return clip_text(value, limit)


def cn_case_type_en(row: tuple[object, ...]) -> str:
    detail = text(row, CN["law_category_detail"], 100)
    return CN_DETAIL_TO_CASE_TYPE_EN.get(detail, f"{detail} dispute" if detail else "Chinese civil dispute")


def translate_stance(value: str) -> str:
    if "\u53cd" in value:
        return "Oppose court result"
    if "\u652f\u6301" in value:
        return "Support court result"
    return english_or_generic(value, "Stance not shown", 60)


def stance_action(stance: str) -> str:
    if stance.startswith("Oppose"):
        return "argues against the court result"
    if stance.startswith("Support"):
        return "supports the court result"
    return "addresses the requested stance"


def stance_label(stance: str) -> str:
    if stance.startswith("Oppose"):
        return "opposition stance"
    if stance.startswith("Support"):
        return "support stance"
    return "requested stance"


def translate_cn_issue(issue_id: str, raw_title: str) -> str:
    return CN_ISSUE_EN.get(issue_id, english_or_generic(raw_title, f"Chinese civil case issue {issue_id}", 120))


def public_exam_issue_preview(row: tuple[object, ...], limit: int) -> str:
    raw_title = text(row, BAR["issue_title"], limit)
    if not has_han(raw_title):
        return raw_title
    return clip_text(f"Official public legal-exam item in {text(row, BAR['law_category'], 80)}", limit)


def nonempty(row: tuple[object, ...]) -> bool:
    return any(value is not None and str(value).strip() for value in row)


def source_domain(value: object) -> str:
    if value is None:
        return ""
    return urlparse(str(value)).netloc.lower()


def read_data_rows(workbook, sheet_name: str) -> tuple[tuple[object, ...], tuple[object, ...], list[tuple[object, ...]]]:
    rows = workbook[sheet_name].iter_rows(values_only=True)
    first_header = next(rows)
    second_header = next(rows)
    return first_header, second_header, [row for row in rows if nonempty(row)]


def first_model_name(first_header: tuple[object, ...], second_header: tuple[object, ...]) -> str:
    models = detect_model_headers(first_header, second_header)
    return models[0] if models else ""


def stratified_sample(records: list[dict[str, str]], keys: tuple[str, ...], limit: int) -> list[dict[str, str]]:
    if limit <= 0 or len(records) <= limit:
        return records
    buckets: OrderedDict[tuple[str, ...], list[dict[str, str]]] = OrderedDict()
    for record in records:
        key = tuple(record.get(name, "") for name in keys)
        buckets.setdefault(key, []).append(record)

    selected: list[dict[str, str]] = []
    bucket_keys = sorted(buckets)
    while len(selected) < limit:
        progressed = False
        for key in bucket_keys:
            if buckets[key]:
                selected.append(buckets[key].pop(0))
                progressed = True
                if len(selected) >= limit:
                    break
        if not progressed:
            break
    return selected


def capped(value: str, limit: int) -> str:
    return clip_text(value, limit)


def cap_record(record: dict[str, str], limit: int) -> dict[str, str]:
    return {key: capped(value, limit) for key, value in record.items()}


def cn_score_summary(row: tuple[object, ...], limit: int) -> str:
    scores = [text(row, index, 20) for index in CN_FIRST_MODEL_SCORES]
    if not any(scores):
        return "not shown"
    return capped("A/B/C=" + "/".join(scores), limit)


def cn_sample_record(row: tuple[object, ...], model: str, cell_limit: int) -> dict[str, str]:
    issue_id = text(row, CN["issue_id"], 50)
    stance = text(row, CN["stance"], 60)
    issue_en = translate_cn_issue(issue_id, text(row, CN["issue_title"], 120))
    case_type_en = cn_case_type_en(row)
    stance_en = translate_stance(stance)
    record = {
        "review_id": text(row, CN["review_id"], 40),
        "document_id": text(row, CN["document_id"], 40),
        "issue_id": issue_id,
        "issue_title_en": issue_en,
        "case_type_en": case_type_en,
        "law_category": text(row, CN["law_category"], 60),
        "stance": stance_en,
        "task_preview": (
            "You are a legal expert. Answer this de-identified Chinese civil-case "
            "reasoning task using only the provided case facts. Write a concise, "
            f"statute-grounded analysis that {stance_action(stance_en)} for the issue: {issue_en}."
        ),
        "court_result_preview": CN_COURT_RESULT_EN.get(
            issue_id,
            f"Court-result preview withheld for de-identification review; issue category: {case_type_en}.",
        ),
        "example_model": model,
        "example_answer_preview": (
            "The model answer is a two-paragraph legal analysis grounded in Chinese legal "
            f"authorities and written for the {stance_label(stance_en)}."
        ),
        "score_summary": cn_score_summary(row, 40),
    }
    return cap_record(record, cell_limit)


def bar_sample_record(row: tuple[object, ...], model: str, cell_limit: int) -> dict[str, str]:
    source_country = text(row, BAR["source_country"], 50)
    issue_title = public_exam_issue_preview(row, 100)
    raw_prompt = text(row, BAR["prompt"], cell_limit)
    raw_reference = text(row, BAR["reference_answer"], cell_limit)
    raw_answer = text(row, BAR_FIRST_MODEL_ANSWER, cell_limit)
    if source_country == "China" or has_han(raw_prompt + raw_reference + raw_answer):
        source_system = text(row, BAR["source_legal_system"], 100)
        legal_domain = text(row, BAR["law_category"], 70)
        task_preview = (
            "You are a legal expert. Answer the official public legal-exam item below "
            "using only the facts and materials reproduced in this prompt. "
            f"[Exam Source] {source_system}. [Legal Domain] {legal_domain}. "
            "Provide the applicable rule, reasoning, and conclusion."
        )
        reference_preview = (
            "Official reference answer evaluates the governing rule, legally relevant facts, "
            "application, and final conclusion for this public legal-exam item."
        )
        answer_preview = (
            "The model answer gives a rule-application-conclusion response for the same "
            "public legal-exam item."
        )
    else:
        source_prefix = "You are a legal " + "analyst."
        task_preview = raw_prompt.replace(source_prefix, "You are a legal expert.", 1)
        reference_preview = raw_reference
        answer_preview = raw_answer
    record = {
        "review_id": text(row, BAR["review_id"], 40),
        "document_id": safe_identifier(
            text(row, BAR["document_id"], 80),
            f"CN-public-exam-{text(row, BAR['review_id'], 40)}",
            80,
        ),
        "issue_id": text(row, BAR["issue_id"], 50),
        "issue_title_en": issue_title,
        "source_country": source_country,
        "source_legal_system": text(row, BAR["source_legal_system"], 100),
        "law_category": text(row, BAR["law_category"], 70),
        "task_preview": task_preview,
        "reference_answer_preview": reference_preview,
        "example_model": model,
        "example_answer_preview": answer_preview,
        "answer_match_score": text(row, BAR_FIRST_MODEL_SCORE, 30),
    }
    return cap_record(record, cell_limit)


def write_csv(path: Path, records: list[dict[str, str]], fieldnames: list[str], cell_limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(cap_record(record, cell_limit))


def write_case_cards(path: Path, cn_sample: list[dict[str, str]], bar_sample: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Preview Cases",
        "",
        "This page presents the public sample in a wider, human-readable format. The CSV",
        "files remain the machine-readable preview; this page gives each case a full-width",
        "collapsible card so task, answer, and scoring fields can be read without a wide",
        "spreadsheet layout.",
        "",
        "## Chinese Real-Case Split",
        "",
    ]
    for record in cn_sample:
        title = f"{record['review_id']} - {record['issue_title_en']} - {record['stance']}"
        lines.extend(
            [
                f"<details><summary>{title}</summary>",
                "",
                f"- **Document / Issue:** `{record['document_id']}` / `{record['issue_id']}`",
                f"- **Case Type:** {record['case_type_en']}",
                f"- **Law Category:** {record['law_category']}",
                f"- **Example Model:** {record['example_model']}",
                f"- **Score Summary:** {record['score_summary']}",
                "",
                "**Task**",
                "",
                f"{record['task_preview']}",
                "",
                "**Court Result**",
                "",
                f"{record['court_result_preview']}",
                "",
                "**Example Answer**",
                "",
                f"{record['example_answer_preview']}",
                "",
                "</details>",
                "",
            ]
        )

    lines.extend(["## Public-Exam Split", ""])
    for record in bar_sample:
        title = f"{record['review_id']} - {record['source_country']} - {record['law_category']}"
        lines.extend(
            [
                f"<details><summary>{title}</summary>",
                "",
                f"- **Document / Issue:** `{record['document_id']}` / `{record['issue_id']}`",
                f"- **Issue:** {record['issue_title_en']}",
                f"- **Source Legal System:** {record['source_legal_system']}",
                f"- **Example Model:** {record['example_model']}",
                f"- **Answer-Match Score:** {record['answer_match_score']}",
                "",
                "**Task**",
                "",
                f"{record['task_preview']}",
                "",
                "**Reference Answer**",
                "",
                f"{record['reference_answer_preview']}",
                "",
                "**Example Answer**",
                "",
                f"{record['example_answer_preview']}",
                "",
                "</details>",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def top_counts(
    split: str,
    dimension: str,
    rows: list[tuple[object, ...]],
    index: int,
    *,
    top_k: int,
    cell_limit: int,
) -> list[dict[str, str]]:
    def normalized_value(row: tuple[object, ...]) -> str:
        value = text(row, index, cell_limit) or "Unknown"
        if split == "real_case_cn" and dimension == "case_type":
            return CN_DETAIL_TO_CASE_TYPE_EN.get(value, f"{value} dispute")
        if split == "real_case_cn" and dimension == "stance":
            return translate_stance(value)
        return value

    counts = Counter(normalized_value(row) for row in rows)
    return [
        {
            "split": split,
            "dimension": dimension,
            "value": value,
            "count": str(count),
        }
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:top_k]
    ]


def source_domain_counts(rows: list[tuple[object, ...]], top_k: int) -> list[dict[str, str]]:
    counts = Counter(source_domain(cell(row, BAR["source_url"])) or "Unknown" for row in rows)
    return [
        {
            "split": "public_exam",
            "dimension": "source_url_domain",
            "value": value,
            "count": str(count),
        }
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:top_k]
    ]


def model_configuration_records(workbook) -> list[dict[str, str]]:
    appearances: OrderedDict[str, list[str]] = OrderedDict()
    for sheet_name in workbook.sheetnames:
        first_header, second_header, _rows = read_data_rows(workbook, sheet_name)
        for model in detect_model_headers(first_header, second_header):
            appearances.setdefault(model, []).append(sheet_name)
    return [
        {
            "model_index": str(index),
            "model_name": model,
            "appears_in_sheets": "; ".join(sheets),
        }
        for index, (model, sheets) in enumerate(appearances.items(), start=1)
    ]


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        escaped = [value.replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(escaped) + " |")
    return "\n".join(lines)


def write_data_readme(
    path: Path,
    *,
    cn_rows: list[tuple[object, ...]],
    bar_rows: list[tuple[object, ...]],
    cn_sample_count: int,
    bar_sample_count: int,
    model_count: int,
    cell_limit: int,
    distribution_rows: list[dict[str, str]],
) -> None:
    country_rows = [
        [item["value"], item["count"]]
        for item in distribution_rows
        if item["split"] == "public_exam" and item["dimension"] == "source_country"
    ]
    cn_case_rows = [
        [item["value"], item["count"]]
        for item in distribution_rows
        if item["split"] == "real_case_cn" and item["dimension"] == "case_type"
    ]
    bar_law_rows = [
        [item["value"], item["count"]]
        for item in distribution_rows
        if item["split"] == "public_exam" and item["dimension"] == "law_category"
    ]
    top_bar_law_sum = sum(int(count) for _value, count in bar_law_rows)
    bar_law_summary_rows = [
        ["Top legal domains listed in source_distribution.csv", str(top_bar_law_sum)],
        ["Other legal domains", str(len(bar_rows) - top_bar_law_sum)],
        ["Total public-exam instances", str(len(bar_rows))],
    ]
    bar_law_preview_rows = bar_law_rows[:4]

    content = f"""# Data Preview

This folder contains a compact public preview of LegalBenchPro. The full workbook is
not included in the repository while licensing, privacy, redistribution, and human
validation review are still in progress.

## Content Preview Files

{markdown_table(
    ["File", "Rows", "Purpose"],
    [
        ["sample/preview_cases.md", str(cn_sample_count + bar_sample_count), "Wide Markdown case cards for human review"],
        ["sample/legalbenchpro_cn_judgments_sample.csv", str(cn_sample_count), "Machine-readable preview of the Chinese civil judgment split"],
        ["sample/legalbenchpro_public_exam_sample.csv", str(bar_sample_count), "Machine-readable preview of the public legal-exam split"],
    ],
)}

## Summary Metadata Files

{markdown_table(
    ["File", "Rows", "Purpose"],
    [
        ["metadata/model_configurations.csv", str(model_count), "Model names and workbook sheet coverage"],
        ["metadata/source_distribution.csv", str(len(distribution_rows)), "Top source, law-category, and case-type counts"],
        ["metadata/dataset_summary.json", "1", "Machine-readable snapshot summary"],
    ],
)}

Preview CSV cells are capped at {cell_limit} characters. For a wider display, use
`sample/preview_cases.md`, which shows each sample row as a collapsible case card. The
preview does not include full prompts, full reference answers, full model-output
matrices, or human review sheets.

## Snapshot Counts

{markdown_table(
    ["Component", "Count"],
    [
        ["Chinese real-case issue-stance prompts", str(len(cn_rows))],
        ["Public legal-exam instances", str(len(bar_rows))],
        ["Model configurations", str(model_count)],
        ["Human validation pilot rows", "10 Chinese real-case rows; 80 public-exam rows"],
    ],
)}

## Public-Exam Country Coverage

{markdown_table(["Source country", "Rows"], country_rows)}

## Chinese Real-Case Coverage

{markdown_table(["Case type", "Rows"], cn_case_rows)}

## Public-Exam Legal Domain Summary

The repository preview intentionally shows only the top legal-domain counts. The
summary below explains why the visible top-domain rows do not add up to 868.

{markdown_table(["Group", "Rows"], bar_law_summary_rows)}

Top examples:

{markdown_table(["Law category", "Rows"], bar_law_preview_rows)}

## Release Note

This is a research preview for manuscript and application review. The complete dataset
is available only after final source-distribution, privacy, and human-validation checks.
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", required=True, help="Path to the private source workbook.")
    parser.add_argument("--out-dir", default="data", help="Output directory inside the repo.")
    parser.add_argument("--sample-per-split", type=int, default=None)
    parser.add_argument("--cn-sample-size", type=int, default=10)
    parser.add_argument("--bar-sample-size", type=int, default=20)
    parser.add_argument("--max-cell-chars", type=int, default=420)
    parser.add_argument("--distribution-top-k", type=int, default=8)
    args = parser.parse_args()

    if args.sample_per_split is not None:
        args.cn_sample_size = args.sample_per_split
        args.bar_sample_size = args.sample_per_split

    workbook_path = Path(args.workbook)
    out_dir = Path(args.out_dir)
    sample_dir = out_dir / "sample"
    metadata_dir = out_dir / "metadata"
    sample_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    cn_first, cn_second, cn_rows = read_data_rows(workbook, "CN_Judgments_Multimodel")
    bar_first, bar_second, bar_rows = read_data_rows(workbook, "Bar_Exam_Multimodel")

    cn_model = first_model_name(cn_first, cn_second)
    bar_model = first_model_name(bar_first, bar_second)
    model_records = model_configuration_records(workbook)

    cn_full_sample = [cn_sample_record(row, cn_model, args.max_cell_chars) for row in cn_rows]
    bar_full_sample = [bar_sample_record(row, bar_model, args.max_cell_chars) for row in bar_rows]
    cn_sample = stratified_sample(
        cn_full_sample,
        ("law_category", "case_type", "stance"),
        args.cn_sample_size,
    )
    bar_sample = stratified_sample(
        bar_full_sample,
        ("source_country", "law_category"),
        args.bar_sample_size,
    )

    write_csv(
        sample_dir / "legalbenchpro_cn_judgments_sample.csv",
        cn_sample,
        CN_SAMPLE_FIELDS,
        args.max_cell_chars,
    )
    write_csv(
        sample_dir / "legalbenchpro_public_exam_sample.csv",
        bar_sample,
        BAR_SAMPLE_FIELDS,
        args.max_cell_chars,
    )
    write_case_cards(sample_dir / "preview_cases.md", cn_sample, bar_sample)
    write_csv(
        metadata_dir / "model_configurations.csv",
        model_records,
        ["model_index", "model_name", "appears_in_sheets"],
        args.max_cell_chars,
    )

    distributions = (
        top_counts("real_case_cn", "case_type", cn_rows, CN["law_category_detail"], top_k=args.distribution_top_k, cell_limit=args.max_cell_chars)
        + top_counts("real_case_cn", "law_category", cn_rows, CN["law_category"], top_k=args.distribution_top_k, cell_limit=args.max_cell_chars)
        + top_counts("real_case_cn", "law_category_detail", cn_rows, CN["law_category_detail"], top_k=args.distribution_top_k, cell_limit=args.max_cell_chars)
        + top_counts("real_case_cn", "stance", cn_rows, CN["stance"], top_k=args.distribution_top_k, cell_limit=args.max_cell_chars)
        + top_counts("public_exam", "source_country", bar_rows, BAR["source_country"], top_k=args.distribution_top_k, cell_limit=args.max_cell_chars)
        + top_counts("public_exam", "source_legal_system", bar_rows, BAR["source_legal_system"], top_k=args.distribution_top_k, cell_limit=args.max_cell_chars)
        + top_counts("public_exam", "law_category", bar_rows, BAR["law_category"], top_k=args.distribution_top_k, cell_limit=args.max_cell_chars)
        + top_counts("public_exam", "law_category_detail", bar_rows, BAR["law_category_detail"], top_k=args.distribution_top_k, cell_limit=args.max_cell_chars)
        + source_domain_counts(bar_rows, args.distribution_top_k)
    )
    write_csv(
        metadata_dir / "source_distribution.csv",
        distributions,
        ["split", "dimension", "value", "count"],
        args.max_cell_chars,
    )

    summaries = summarize_workbook(workbook_path)
    metadata = {
        "source_workbook_name": workbook_path.name,
        "release_status": "compact public preview; full workbook is private/local until licensing review",
        "preview_policy": {
            "cn_sample_rows": len(cn_sample),
            "public_exam_sample_rows": len(bar_sample),
            "max_csv_cell_characters": args.max_cell_chars,
            "full_prompt_matrix_public": False,
            "full_reference_answers_public": False,
            "full_model_outputs_public": False,
            "human_review_sheets_public": False,
        },
        "sheets": [
            {
                "title": item.title,
                "data_rows_after_two_header_rows": item.data_rows,
                "model_count_detected": item.model_count,
                "model_names_detected": item.model_names,
            }
            for item in summaries
        ],
        "public_snapshot_counts": {
            "cn_real_case_issue_stance_prompts": len(cn_rows),
            "public_exam_instances": len(bar_rows),
            "model_configurations": len(model_records),
            "human_cn_pilot_rows": next(
                item.data_rows for item in summaries if item.title == "Human_CN_Judgments"
            ),
            "human_bar_pilot_rows": next(
                item.data_rows for item in summaries if item.title == "Human_Bar_Exam"
            ),
        },
        "public_files": {
            "readme": "data/README.md",
            "content_samples": [
                "data/sample/preview_cases.md",
                "data/sample/legalbenchpro_cn_judgments_sample.csv",
                "data/sample/legalbenchpro_public_exam_sample.csv",
            ],
            "metadata": [
                "data/metadata/dataset_summary.json",
                "data/metadata/model_configurations.csv",
                "data/metadata/source_distribution.csv",
            ],
        },
    }
    metadata_path = metadata_dir / "dataset_summary.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )

    write_data_readme(
        out_dir / "README.md",
        cn_rows=cn_rows,
        bar_rows=bar_rows,
        cn_sample_count=len(cn_sample),
        bar_sample_count=len(bar_sample),
        model_count=len(model_records),
        cell_limit=args.max_cell_chars,
        distribution_rows=distributions,
    )

    print(f"Wrote {out_dir / 'README.md'}")
    print(f"Wrote {sample_dir / 'preview_cases.md'}")
    print(f"Wrote {sample_dir / 'legalbenchpro_cn_judgments_sample.csv'}")
    print(f"Wrote {sample_dir / 'legalbenchpro_public_exam_sample.csv'}")
    print(f"Wrote {metadata_dir / 'model_configurations.csv'}")
    print(f"Wrote {metadata_dir / 'source_distribution.csv'}")
    print(f"Wrote {metadata_path}")


if __name__ == "__main__":
    main()
