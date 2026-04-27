from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from openpyxl import load_workbook

from legalbenchpro.workbook import clip_text, detect_model_headers, summarize_workbook


def row_dict(header: tuple[object, ...], row: tuple[object, ...]) -> dict[str, object]:
    return {
        str(name): value
        for name, value in zip(header, row)
        if name is not None and str(name).strip()
    }


def extract_cn_rows(workbook, limit: int) -> list[dict[str, str]]:
    ws = workbook["CN_Judgments_Multimodel"]
    rows = ws.iter_rows(values_only=True)
    first_header = next(rows)
    second_header = next(rows)
    model = detect_model_headers(first_header)[0]
    records: list[dict[str, str]] = []
    for row in rows:
        if not any(value is not None for value in row):
            continue
        item = row_dict(second_header, row)
        records.append(
            {
                "split": "real_case_cn",
                "review_id": str(item.get("review_id", "")),
                "document_id": str(item.get("文档编号", "")),
                "issue_id": str(item.get("争点编号", "")),
                "issue_title": clip_text(item.get("争点标题"), 120),
                "jurisdiction_or_source": "China civil judgment, de-identified",
                "law_category": clip_text(item.get("Law Category / 法律类别"), 80),
                "law_category_detail": clip_text(item.get("Law Category Detail / 法律细类"), 80),
                "stance": clip_text(item.get("立场"), 80),
                "prompt_excerpt": clip_text(item.get("Prompt（给AI）"), 260),
                "reference_excerpt": clip_text(item.get("核心问题（脱敏）"), 260),
                "example_model": model,
                "example_answer_excerpt": clip_text(item.get("AI回答（两段）"), 260),
                "score_or_status": "rubric scores present for automated scoring; human validation in progress",
            }
        )
        if len(records) >= limit:
            break
    return records


def extract_bar_rows(workbook, limit: int) -> list[dict[str, str]]:
    ws = workbook["Bar_Exam_Multimodel"]
    rows = ws.iter_rows(values_only=True)
    first_header = next(rows)
    second_header = next(rows)
    model = detect_model_headers(first_header)[0]
    records: list[dict[str, str]] = []
    for row in rows:
        if not any(value is not None for value in row):
            continue
        item = row_dict(second_header, row)
        records.append(
            {
                "split": "public_exam",
                "review_id": str(item.get("Review ID", "")),
                "document_id": str(item.get("Document ID", "")),
                "issue_id": str(item.get("Issue ID", "")),
                "issue_title": clip_text(item.get("Issue Title"), 120),
                "jurisdiction_or_source": clip_text(item.get("Source Legal System"), 120),
                "law_category": clip_text(item.get("Law Category / 法律类别"), 80),
                "law_category_detail": clip_text(item.get("Law Category Detail / 法律细类"), 80),
                "stance": "",
                "prompt_excerpt": clip_text(item.get("Prompt (for AI)"), 260),
                "reference_excerpt": clip_text(item.get("External Reference Answer"), 260),
                "example_model": model,
                "example_answer_excerpt": clip_text(item.get("AI Answer (Two Paragraphs)"), 260),
                "score_or_status": clip_text(item.get("Answer Match Score (0-4)"), 80),
            }
        )
        if len(records) >= limit:
            break
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", required=True, help="Path to the private source workbook.")
    parser.add_argument("--out-dir", default="data", help="Output directory inside the repo.")
    parser.add_argument("--sample-per-split", type=int, default=5)
    args = parser.parse_args()

    workbook_path = Path(args.workbook)
    out_dir = Path(args.out_dir)
    sample_dir = out_dir / "sample"
    metadata_dir = out_dir / "metadata"
    sample_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    sample = extract_cn_rows(workbook, args.sample_per_split) + extract_bar_rows(
        workbook, args.sample_per_split
    )

    sample_path = sample_dir / "legalbenchpro_public_sample.csv"
    with sample_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sample[0].keys()))
        writer.writeheader()
        writer.writerows(sample)

    summaries = summarize_workbook(workbook_path)
    metadata = {
        "source_workbook_name": workbook_path.name,
        "release_status": "public sample only; full workbook is private/local until licensing review",
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
            "cn_real_case_issue_stance_prompts": next(
                item.data_rows for item in summaries if item.title == "CN_Judgments_Multimodel"
            ),
            "public_exam_instances": next(
                item.data_rows for item in summaries if item.title == "Bar_Exam_Multimodel"
            ),
            "human_cn_pilot_rows": next(
                item.data_rows for item in summaries if item.title == "Human_CN_Judgments"
            ),
            "human_bar_pilot_rows": next(
                item.data_rows for item in summaries if item.title == "Human_Bar_Exam"
            ),
        },
    }
    metadata_path = metadata_dir / "dataset_summary.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    print(f"Wrote {sample_path}")
    print(f"Wrote {metadata_path}")


if __name__ == "__main__":
    main()
