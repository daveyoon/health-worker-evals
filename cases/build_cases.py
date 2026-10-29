"""Build cases/en.jsonl and cases/sw.jsonl from source_cases.py."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from source_cases import CASES  # noqa: E402

REQUIRED = {"id", "category", "critical", "refer", "en", "sw", "must", "must_not", "source"}
CATEGORIES = {"diagnosis", "treatment", "dosing", "emergency", "pregnancy",
              "monitoring", "referral", "counselling", "safety"}


def validate(cases):
    ids = [c["id"] for c in cases]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    assert not dupes, f"duplicate ids: {dupes}"
    for c in cases:
        missing = REQUIRED - c.keys()
        assert not missing, f"{c.get('id')}: missing {missing}"
        assert c["category"] in CATEGORIES, f"{c['id']}: bad category {c['category']}"
        assert c["must"], f"{c['id']}: no must items"


def main():
    validate(CASES)
    for lang in ("en", "sw"):
        with open(HERE / f"{lang}.jsonl", "w") as f:
            for c in CASES:
                row = {k: v for k, v in c.items() if k not in ("en", "sw")}
                row["case_id"] = f"{c['id']}-{lang.upper()}"
                row["lang"] = lang
                row["prompt"] = c[lang]
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    cats = Counter(c["category"] for c in CASES)
    print(f"{len(CASES)} cases x 2 languages = {2 * len(CASES)} prompts")
    print(f"critical: {sum(c['critical'] for c in CASES)}  needs referral: {sum(c['refer'] for c in CASES)}")
    print("by category:", dict(sorted(cats.items())))


if __name__ == "__main__":
    main()
