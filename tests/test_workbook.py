from __future__ import annotations

import unittest

from legalbenchpro.workbook import clip_text, detect_model_headers


class WorkbookHelperTests(unittest.TestCase):
    def test_clip_text_normalizes_whitespace_and_truncates(self) -> None:
        text = clip_text("alpha\n beta   gamma", limit=12)
        self.assertEqual(text, "alpha bet...")

    def test_detect_model_headers_excludes_sheet_group_labels(self) -> None:
        headers = [
            "External Sample Basic Info",
            None,
            "Grok 4.20",
            None,
            "DeepSeek R1",
            "Case Basic Info",
            "Codex 5.4",
        ]
        subheaders = [
            "Review ID",
            "Document ID",
            "AI Answer (Two Paragraphs)",
            "Answer Match Score (0-4)",
            "AI Answer (Two Paragraphs)",
            "review_id",
            "AI Answer (Two Paragraphs)",
        ]
        self.assertEqual(
            detect_model_headers(headers, subheaders),
            ["Grok 4.20", "DeepSeek R1", "Codex 5.4"],
        )


if __name__ == "__main__":
    unittest.main()
