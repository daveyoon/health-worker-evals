"""Command line.

  python -m ylab_evals run    --models anthropic:claude-opus-5-5 openai:gpt-5 google:gemini-2.5-pro
  python -m ylab_evals grade  --judge anthropic:claude-opus-5-5
  python -m ylab_evals report
  python -m ylab_evals spot-check
  python -m ylab_evals agreement results/spot_check.csv
"""
import argparse
from pathlib import Path

from . import grade as grade_mod
from . import report as report_mod
from .run import collect, load_cases


def main():
    ap = argparse.ArgumentParser(prog="ylab_evals")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "grade", "report", "spot-check"):
        p = sub.add_parser(name)
        p.add_argument("--langs", nargs="+", default=["en", "sw"])
        p.add_argument("--limit", type=int, help="first N cases per language (for smoke tests)")
        p.add_argument("--out", default="results")
        p.add_argument("--workers", type=int, default=4)
        if name == "run":
            p.add_argument("--models", nargs="+", required=True)
        if name == "grade":
            p.add_argument("--judge", required=True)
        if name == "spot-check":
            p.add_argument("--per-model", type=int, default=20)
    p = sub.add_parser("agreement")
    p.add_argument("csv")
    a = ap.parse_args()

    if a.cmd == "agreement":
        return report_mod.agreement(a.csv)
    cases = load_cases(a.langs, a.limit)
    if a.cmd == "run":
        for m in a.models:
            collect(m, cases, a.out, a.workers)
    elif a.cmd == "grade":
        for p in sorted(Path(a.out).glob("answers__*.jsonl")):
            grade_mod.grade(p, cases, a.judge, a.out, a.workers)
    elif a.cmd == "report":
        report_mod.write_report(a.out)
    elif a.cmd == "spot-check":
        report_mod.spot_check(a.out, cases, a.per_model)


if __name__ == "__main__":
    main()
