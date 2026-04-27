from __future__ import annotations

import unittest

from legalbenchpro.workbook import clip_text, detect_model_headers


class WorkbookHelperTests(unittest.TestCase):
    def test_clip_text_normalizes_whitespace_and_truncates(self) -> None:
        text = clip_text("alpha\n beta   gamma", limit=12)
        self.assertEqual(text, "alpha bet...")

    def test_detect_model_headers_excludes_sheet_group_labels(self) -> None:
        headers = [
            "External Sample 基础信息",
            None,
            "Grok 4.20",
            None,
            "DeepSeek R1",
            "案件基础信息",
            "Codex 5.4",
        ]
        self.assertEqual(
            detect_model_headers(headers),
            ["Grok 4.20", "DeepSeek R1", "Codex 5.4"],
        )


if __name__ == "__main__":
    unittest.main()
