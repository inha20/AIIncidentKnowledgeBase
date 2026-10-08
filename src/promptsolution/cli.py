"""Command line interface: add / list / show / search / status / report / validate."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

from .taxonomy import CATEGORIES, REQUIRED_FIELDS, SEVERITIES, STATUSES

ID_RE = re.compile(r"^INC-(\d{4,})$")
TEXT_FIELDS = ["title", "symptom", "root_cause", "bad_prompt", "fixed_prompt", "mitigation"]


def validate_record(rec: dict) -> list[str]:
    problems = []
    for f in REQUIRED_FIELDS:
        if f not in rec:
            problems.append(f"missing field: {f}")
    if "id" in rec and not ID_RE.match(str(rec["id"])):
        problems.append(f"invalid id: {rec['id']}")
    if rec.get("category") not in CATEGORIES:
        problems.append(f"unknown category: {rec.get('category')}")
    if rec.get("severity") not in SEVERITIES:
        problems.append(f"unknown severity: {rec.get('severity')}")
    if rec.get("status") not in STATUSES:
        problems.append(f"unknown status: {rec.get('status')}")
    try:
        dt.date.fromisoformat(str(rec.get("created")))
    except ValueError:
        problems.append(f"invalid created date: {rec.get('created')}")
    if rec.get("status") == "resolved" and not str(rec.get("fixed_prompt", "")).strip() \
            and not str(rec.get("mitigation", "")).strip():
        problems.append("resolved incident needs fixed_prompt or mitigation")
    return problems


def load_all(folder: Path) -> list[dict]:
    records = []
    for path in sorted(folder.glob("INC-*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def save(folder: Path, rec: dict) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{rec['id']}.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def next_id(folder: Path) -> str:
    nums = [int(m.group(1)) for p in folder.glob("INC-*.json") if (m := ID_RE.match(p.stem))]
    return f"INC-{(max(nums) + 1 if nums else 1):04d}"


def find(folder: Path, inc_id: str) -> dict | None:
    path = folder / f"{inc_id}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def cmd_add(args) -> int:
    folder = Path(args.dir)
    today = dt.date.today().isoformat()
    rec = {
        "id": next_id(folder),
        "title": args.title,
        "created": today,
        "updated": today,
        "category": args.category,
        "severity": args.severity,
        "status": args.status,
        "model": args.model,
        "symptom": args.symptom,
        "root_cause": args.root_cause,
        "bad_prompt": args.bad_prompt,
        "fixed_prompt": args.fixed_prompt,
        "mitigation": args.mitigation,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "reporter": args.reporter,
    }
    problems = validate_record(rec)
    if problems:
        for p in problems:
            print("error:", p, file=sys.stderr)
        return 1
    print(f"created {save(folder, rec)}")
    return 0


def cmd_list(args) -> int:
    rows = load_all(Path(args.dir))
    for key in ("category", "severity", "status"):
        val = getattr(args, key)
        if val:
            rows = [r for r in rows if r.get(key) == val]
    if args.tag:
        rows = [r for r in rows if args.tag in r.get("tags", [])]
    if not rows:
        print("no incidents")
        return 0
    for r in rows:
        print(f"{r['id']}  {r['severity']:<8} {r['status']:<9} {r['category']:<20} {r['title']}")
    return 0


def render(rec: dict) -> str:
    lines = [f"# {rec['id']} {rec['title']}", ""]
    lines.append(f"- 분류: {rec['category']} / 심각도: {rec['severity']} / 상태: {rec['status']}")
    lines.append(f"- 모델: {rec['model']} / 등록: {rec['created']} / 보고자: {rec.get('reporter', '-')}")
    lines.append(f"- 태그: {', '.join(rec.get('tags', [])) or '-'}")
    for label, key in [("증상", "symptom"), ("원인", "root_cause"), ("문제 프롬프트", "bad_prompt"),
                       ("수정된 프롬프트", "fixed_prompt"), ("대응 방법", "mitigation")]:
        lines += ["", f"## {label}", str(rec.get(key, "")).strip() or "(없음)"]
    return "\n".join(lines) + "\n"


def cmd_show(args) -> int:
    rec = find(Path(args.dir), args.id)
    if rec is None:
        print(f"error: {args.id} not found", file=sys.stderr)
        return 1
    print(render(rec))
    return 0


def cmd_search(args) -> int:
    needle = args.keyword.lower()
    hits = []
    for r in load_all(Path(args.dir)):
        blob = " ".join([str(r.get(f, "")) for f in TEXT_FIELDS] + r.get("tags", [])).lower()
        if needle in blob:
            hits.append(r)
    for r in hits:
        print(f"{r['id']}  {r['status']:<9} {r['title']}")
    if not hits:
        print("no matches")
    return 0


def cmd_status(args) -> int:
    folder = Path(args.dir)
    rec = find(folder, args.id)
    if rec is None:
        print(f"error: {args.id} not found", file=sys.stderr)
        return 1
    rec["status"] = args.status
    if args.fixed_prompt:
        rec["fixed_prompt"] = args.fixed_prompt
    if args.mitigation:
        rec["mitigation"] = args.mitigation
    rec["updated"] = dt.date.today().isoformat()
    problems = validate_record(rec)
    if problems:
        for p in problems:
            print("error:", p, file=sys.stderr)
        return 1
    save(folder, rec)
    print(f"{args.id} -> {args.status}")
    return 0


def build_report(records: list[dict]) -> str:
    total = len(records)
    out = ["# AI 오류 현황 리포트", "", f"- 전체: {total}건",
           f"- 미해결(open): {sum(r['status'] == 'open' for r in records)}건", ""]

    def table(title, counter, order=None):
        out.append(f"## {title}")
        out.append("| 항목 | 건수 |\n|---|---|")
        keys = order or [k for k, _ in counter.most_common()]
        for k in keys:
            if counter.get(k):
                out.append(f"| {k} | {counter[k]} |")
        out.append("")

    table("분류별", collections.Counter(r["category"] for r in records))
    table("심각도별", collections.Counter(r["severity"] for r in records), SEVERITIES)
    table("상태별", collections.Counter(r["status"] for r in records), STATUSES)
    tags = collections.Counter(t for r in records for t in r.get("tags", []))
    if tags:
        out.append("## 자주 나온 태그")
        out += [f"- {t} ({n})" for t, n in tags.most_common(5)]
        out.append("")
    urgent = [r for r in records if r["status"] == "open" and r["severity"] in ("high", "critical")]
    if urgent:
        out.append("## 우선 처리 필요 (open, high 이상)")
        out += [f"- {r['id']} [{r['severity']}] {r['title']}" for r in urgent]
        out.append("")
    return "\n".join(out)


def cmd_report(args) -> int:
    report = build_report(load_all(Path(args.dir)))
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(report)
    return 0


def cmd_validate(args) -> int:
    bad = 0
    for rec in load_all(Path(args.dir)):
        for p in validate_record(rec):
            print(f"{rec.get('id', '?')}: {p}")
            bad += 1
    print("OK" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(prog="promptsolution", description=__doc__)
    p.add_argument("--dir", default="incidents", help="incident folder (default: incidents)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("add", help="record a new incident")
    s.add_argument("--title", required=True)
    s.add_argument("--category", required=True, choices=list(CATEGORIES))
    s.add_argument("--severity", default="medium", choices=SEVERITIES)
    s.add_argument("--status", default="open", choices=STATUSES)
    s.add_argument("--model", default="unknown")
    s.add_argument("--symptom", required=True)
    s.add_argument("--root-cause", default="조사 중")
    s.add_argument("--bad-prompt", default="")
    s.add_argument("--fixed-prompt", default="")
    s.add_argument("--mitigation", default="")
    s.add_argument("--tags", default="")
    s.add_argument("--reporter", default="")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("list", help="list incidents")
    s.add_argument("--category", choices=list(CATEGORIES))
    s.add_argument("--severity", choices=SEVERITIES)
    s.add_argument("--status", choices=STATUSES)
    s.add_argument("--tag")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="show one incident")
    s.add_argument("id")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("search", help="keyword search")
    s.add_argument("keyword")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("status", help="change status, optionally recording the fix")
    s.add_argument("id")
    s.add_argument("status", choices=STATUSES)
    s.add_argument("--fixed-prompt", default="")
    s.add_argument("--mitigation", default="")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("report", help="markdown summary for sharing with the team")
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("validate", help="check all records against the schema")
    s.set_defaults(func=cmd_validate)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
