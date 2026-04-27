from __future__ import annotations

import argparse
import csv
import json
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
    "supported_proposition": 10,
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
    "case_theme": 2,
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

COMMON_SAMPLE_FIELDS = [
    "split",
    "review_id",
    "document_id",
    "issue_id",
    "issue_title",
    "jurisdiction_or_source",
    "law_category",
    "law_category_detail",
    "stance",
    "prompt_excerpt",
    "reference_excerpt",
    "example_model",
    "example_answer_excerpt",
    "score_or_status",
]

CN_SAMPLE_FIELDS = [
    "split",
    "review_id",
    "document_id",
    "issue_id",
    "issue_title",
    "case_theme",
    "court_level",
    "case_type",
    "law_category",
    "law_category_detail",
    "stance",
    "prompt_excerpt",
    "core_issue_excerpt",
    "cited_authority_excerpt",
    "supported_proposition_excerpt",
    "example_model",
    "example_answer_excerpt",
    "automated_score_summary",
    "release_note",
]

BAR_SAMPLE_FIELDS = [
    "split",
    "review_id",
    "document_id",
    "issue_id",
    "issue_title",
    "source_country",
    "source_legal_system",
    "source_body",
    "source_url_domain",
    "law_category",
    "law_category_detail",
    "prompt_excerpt",
    "reference_answer_excerpt",
    "example_model",
    "example_answer_excerpt",
    "answer_match_score",
    "release_note",
]

INDEX_FIELDS = [
    "split",
    "review_id",
    "document_id",
    "issue_id",
    "issue_title",
    "source_or_case_theme",
    "jurisdiction_or_source",
    "law_category",
    "law_category_detail",
    "stance",
    "public_content_status",
]


def cell(row: tuple[object, ...], index: int) -> object:
    return row[index] if index < len(row) else None


def text(row: tuple[object, ...], index: int, limit: int | None = None) -> str:
    value = cell(row, index)
    return clip_text(value, limit) if limit else clip_text(value, 10_000)


def nonempty(row: tuple[object, ...]) -> bool:
    return any(value is not None and str(value).strip() for value in row)


def source_domain(value: object) -> str:
    if value is None:
        return ""
    parsed = urlparse(str(value))
    return parsed.netloc.lower()


def first_model_name(first_header: tuple[object, ...], second_header: tuple[object, ...]) -> str:
    models = detect_model_headers(first_header, second_header)
    return models[0] if models else ""


def read_data_rows(workbook, sheet_name: str) -> tuple[tuple[object, ...], tuple[object, ...], list[tuple[object, ...]]]:
    ws = workbook[sheet_name]
    rows = ws.iter_rows(values_only=True)
    first_header = next(rows)
    second_header = next(rows)
    data_rows = [row for row in rows if nonempty(row)]
    return first_header, second_header, data_rows


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
        made_progress = False
        for key in bucket_keys:
            if buckets[key]:
                selected.append(buckets[key].pop(0))
                made_progress = True
                if len(selected) >= limit:
                    break
        if not made_progress:
            break
    return selected


def cn_score_summary(row: tuple[object, ...]) -> str:
    scores = [text(row, index) for index in CN_FIRST_MODEL_SCORES]
    if not any(scores):
        return "automated rubric scores not shown in public index"
    return "A/B/C=" + "/".join(scores)


def cn_sample_record(row: tuple[object, ...], model: str) -> dict[str, str]:
    return {
        "split": "real_case_cn",
        "review_id": text(row, CN["review_id"]),
        "document_id": text(row, CN["document_id"]),
        "issue_id": text(row, CN["issue_id"]),
        "issue_title": text(row, CN["issue_title"], 140),
        "case_theme": text(row, CN["case_theme"], 160),
        "court_level": text(row, CN["court_level"], 80),
        "case_type": text(row, CN["case_type"], 100),
        "law_category": text(row, CN["law_category"], 80),
        "law_category_detail": text(row, CN["law_category_detail"], 100),
        "stance": text(row, CN["stance"], 80),
        "prompt_excerpt": text(row, CN["prompt"], 420),
        "core_issue_excerpt": text(row, CN["core_issue"], 260),
        "cited_authority_excerpt": text(row, CN["cited_authority"], 220),
        "supported_proposition_excerpt": text(row, CN["supported_proposition"], 220),
        "example_model": model,
        "example_answer_excerpt": text(row, CN_FIRST_MODEL_ANSWER, 320),
        "automated_score_summary": cn_score_summary(row),
        "release_note": "excerpted sample only; full prompt and model matrix are not included",
    }


def cn_common_record(record: dict[str, str]) -> dict[str, str]:
    return {
        "split": record["split"],
        "review_id": record["review_id"],
        "document_id": record["document_id"],
        "issue_id": record["issue_id"],
        "issue_title": record["issue_title"],
        "jurisdiction_or_source": "China civil judgment, de-identified",
        "law_category": record["law_category"],
        "law_category_detail": record["law_category_detail"],
        "stance": record["stance"],
        "prompt_excerpt": record["prompt_excerpt"],
        "reference_excerpt": record["core_issue_excerpt"],
        "example_model": record["example_model"],
        "example_answer_excerpt": record["example_answer_excerpt"],
        "score_or_status": record["automated_score_summary"],
    }


def cn_index_record(row: tuple[object, ...]) -> dict[str, str]:
    return {
        "split": "real_case_cn",
        "review_id": text(row, CN["review_id"]),
        "document_id": text(row, CN["document_id"]),
        "issue_id": text(row, CN["issue_id"]),
        "issue_title": text(row, CN["issue_title"], 180),
        "source_or_case_theme": text(row, CN["case_theme"], 180),
        "jurisdiction_or_source": "China civil judgment, de-identified",
        "law_category": text(row, CN["law_category"], 80),
        "law_category_detail": text(row, CN["law_category_detail"], 100),
        "stance": text(row, CN["stance"], 80),
        "public_content_status": "metadata only; content appears only in excerpted sample rows",
    }


def bar_sample_record(row: tuple[object, ...], model: str) -> dict[str, str]:
    return {
        "split": "public_exam",
        "review_id": text(row, BAR["review_id"]),
        "document_id": text(row, BAR["document_id"]),
        "issue_id": text(row, BAR["issue_id"]),
        "issue_title": text(row, BAR["issue_title"], 140),
        "source_country": text(row, BAR["source_country"], 80),
        "source_legal_system": text(row, BAR["source_legal_system"], 140),
        "source_body": text(row, BAR["source_body"], 140),
        "source_url_domain": source_domain(cell(row, BAR["source_url"])),
        "law_category": text(row, BAR["law_category"], 80),
        "law_category_detail": text(row, BAR["law_category_detail"], 100),
        "prompt_excerpt": text(row, BAR["prompt"], 360),
        "reference_answer_excerpt": text(row, BAR["reference_answer"], 280),
        "example_model": model,
        "example_answer_excerpt": text(row, BAR_FIRST_MODEL_ANSWER, 300),
        "answer_match_score": text(row, BAR_FIRST_MODEL_SCORE, 80),
        "release_note": "excerpted sample only; full reference answer and model matrix are not included",
    }


def bar_common_record(record: dict[str, str]) -> dict[str, str]:
    return {
        "split": record["split"],
        "review_id": record["review_id"],
        "document_id": record["document_id"],
        "issue_id": record["issue_id"],
        "issue_title": record["issue_title"],
        "jurisdiction_or_source": record["source_legal_system"],
        "law_category": record["law_category"],
        "law_category_detail": record["law_category_detail"],
        "stance": "",
        "prompt_excerpt": record["prompt_excerpt"],
        "reference_excerpt": record["reference_answer_excerpt"],
        "example_model": record["example_model"],
        "example_answer_excerpt": record["example_answer_excerpt"],
        "score_or_status": record["answer_match_score"],
    }


def bar_index_record(row: tuple[object, ...]) -> dict[str, str]:
    return {
        "split": "public_exam",
        "review_id": text(row, BAR["review_id"]),
        "document_id": text(row, BAR["document_id"]),
        "issue_id": text(row, BAR["issue_id"]),
        "issue_title": text(row, BAR["issue_title"], 180),
        "source_or_case_theme": text(row, BAR["source_body"], 140),
        "jurisdiction_or_source": text(row, BAR["source_legal_system"], 160),
        "law_category": text(row, BAR["law_category"], 80),
        "law_category_detail": text(row, BAR["law_category_detail"], 100),
        "stance": "",
        "public_content_status": "metadata only; content appears only in excerpted sample rows",
    }


def write_csv(path: Path, records: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def distribution_records(
    split: str,
    rows: list[tuple[object, ...]],
    dimensions: dict[str, int],
) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for dimension, index in dimensions.items():
        counts = Counter(text(row, index) or "Unknown" for row in rows)
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            records.append(
                {
                    "split": split,
                    "dimension": dimension,
                    "value": value,
                    "count": str(count),
                }
            )
    return records


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", required=True, help="Path to the private source workbook.")
    parser.add_argument("--out-dir", default="data", help="Output directory inside the repo.")
    parser.add_argument("--sample-per-split", type=int, default=None)
    parser.add_argument("--cn-sample-size", type=int, default=24)
    parser.add_argument("--bar-sample-size", type=int, default=80)
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

    cn_full_sample = [cn_sample_record(row, cn_model) for row in cn_rows]
    bar_full_sample = [bar_sample_record(row, bar_model) for row in bar_rows]
    cn_sample = stratified_sample(
        cn_full_sample,
        ("law_category", "law_category_detail", "stance"),
        args.cn_sample_size,
    )
    bar_sample = stratified_sample(
        bar_full_sample,
        ("source_country", "law_category"),
        args.bar_sample_size,
    )

    write_csv(sample_dir / "legalbenchpro_cn_judgments_sample.csv", cn_sample, CN_SAMPLE_FIELDS)
    write_csv(sample_dir / "legalbenchpro_public_exam_sample.csv", bar_sample, BAR_SAMPLE_FIELDS)
    write_csv(
        sample_dir / "legalbenchpro_public_sample.csv",
        [cn_common_record(record) for record in cn_sample]
        + [bar_common_record(record) for record in bar_sample],
        COMMON_SAMPLE_FIELDS,
    )

    cn_index = [cn_index_record(row) for row in cn_rows]
    bar_index = [bar_index_record(row) for row in bar_rows]
    write_csv(metadata_dir / "cn_judgments_index.csv", cn_index, INDEX_FIELDS)
    write_csv(metadata_dir / "public_exam_index.csv", bar_index, INDEX_FIELDS)
    write_csv(
        metadata_dir / "model_configurations.csv",
        model_configuration_records(workbook),
        ["model_index", "model_name", "appears_in_sheets"],
    )

    distributions = distribution_records(
        "real_case_cn",
        cn_rows,
        {
            "case_type": CN["case_type"],
            "law_category": CN["law_category"],
            "law_category_detail": CN["law_category_detail"],
            "stance": CN["stance"],
        },
    ) + distribution_records(
        "public_exam",
        bar_rows,
        {
            "source_country": BAR["source_country"],
            "source_legal_system": BAR["source_legal_system"],
            "law_category": BAR["law_category"],
            "law_category_detail": BAR["law_category_detail"],
        },
    )
    write_csv(
        metadata_dir / "source_distribution.csv",
        distributions,
        ["split", "dimension", "value", "count"],
    )

    summaries = summarize_workbook(workbook_path)
    metadata = {
        "source_workbook_name": workbook_path.name,
        "release_status": "expanded public sample plus metadata indexes; full workbook is private/local until licensing review",
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
            "cn_public_sample_rows": len(cn_sample),
            "public_exam_sample_rows": len(bar_sample),
            "cn_public_index_rows": len(cn_index),
            "public_exam_index_rows": len(bar_index),
            "human_cn_pilot_rows": next(
                item.data_rows for item in summaries if item.title == "Human_CN_Judgments"
            ),
            "human_bar_pilot_rows": next(
                item.data_rows for item in summaries if item.title == "Human_Bar_Exam"
            ),
        },
        "public_files": {
            "content_samples": [
                "data/sample/legalbenchpro_cn_judgments_sample.csv",
                "data/sample/legalbenchpro_public_exam_sample.csv",
                "data/sample/legalbenchpro_public_sample.csv",
            ],
            "metadata_indexes": [
                "data/metadata/cn_judgments_index.csv",
                "data/metadata/public_exam_index.csv",
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

    print(f"Wrote {sample_dir / 'legalbenchpro_cn_judgments_sample.csv'}")
    print(f"Wrote {sample_dir / 'legalbenchpro_public_exam_sample.csv'}")
    print(f"Wrote {sample_dir / 'legalbenchpro_public_sample.csv'}")
    print(f"Wrote {metadata_dir / 'cn_judgments_index.csv'}")
    print(f"Wrote {metadata_dir / 'public_exam_index.csv'}")
    print(f"Wrote {metadata_dir / 'model_configurations.csv'}")
    print(f"Wrote {metadata_dir / 'source_distribution.csv'}")
    print(f"Wrote {metadata_path}")


if __name__ == "__main__":
    main()
