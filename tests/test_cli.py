import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from promptsolution import cli  # noqa: E402


class IncidentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "inc"

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, title="환각 사례", category="hallucination", **extra):
        argv = ["--dir", str(self.dir), "add", "--title", title, "--category", category,
                "--symptom", "존재하지 않는 규정을 인용함"]
        for k, v in extra.items():
            argv += [f"--{k.replace('_', '-')}", v]
        return cli.main(argv)

    def test_add_assigns_sequential_ids(self):
        self.assertEqual(self.add(), 0)
        self.assertEqual(self.add("두번째"), 0)
        self.assertTrue((self.dir / "INC-0001.json").exists())
        self.assertTrue((self.dir / "INC-0002.json").exists())

    def test_invalid_category_rejected(self):
        with self.assertRaises(SystemExit):
            self.add(category="nonsense")

    def test_resolved_requires_fix(self):
        self.add()
        self.assertEqual(cli.main(["--dir", str(self.dir), "status", "INC-0001", "resolved"]), 1)
        self.assertEqual(cli.main(["--dir", str(self.dir), "status", "INC-0001", "resolved",
                                   "--fixed-prompt", "근거 문서 없으면 모른다고 답하세요"]), 0)
        rec = json.loads((self.dir / "INC-0001.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["status"], "resolved")

    def test_search_matches_text_and_tags(self):
        self.add(tags="환불,정책")
        recs = cli.load_all(self.dir)
        self.assertIn("정책", recs[0]["tags"])

    def test_report_counts(self):
        self.add(severity="high")
        self.add("b", category="outdated-info", severity="low")
        report = cli.build_report(cli.load_all(self.dir))
        self.assertIn("전체: 2건", report)
        self.assertIn("| hallucination | 1 |", report)
        self.assertIn("우선 처리 필요", report)

    def test_validate_catches_bad_record(self):
        self.add()
        path = self.dir / "INC-0001.json"
        rec = json.loads(path.read_text(encoding="utf-8"))
        rec["severity"] = "huge"
        path.write_text(json.dumps(rec), encoding="utf-8")
        self.assertEqual(cli.main(["--dir", str(self.dir), "validate"]), 1)

    def test_bundled_examples_are_valid(self):
        records = cli.load_all(ROOT / "examples" / "incidents")
        self.assertGreaterEqual(len(records), 3)
        for rec in records:
            self.assertEqual(cli.validate_record(rec), [], rec["id"])


if __name__ == "__main__":
    unittest.main()
