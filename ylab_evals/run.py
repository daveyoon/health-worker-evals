"""Collect answers: for each model and case, ask the question once and store the reply.
Resumable: rows already in the output file are skipped."""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .prompts import SUBJECT_SYSTEM
from .providers import complete

ROOT = Path(__file__).resolve().parent.parent


def load_cases(langs, limit=None):
    cases = []
    for lang in langs:
        with open(ROOT / "cases" / f"{lang}.jsonl") as f:
            rows = [json.loads(l) for l in f]
        cases += rows[:limit] if limit else rows
    return cases


def slug(spec):
    return spec.replace(":", "__").replace("/", "_")


def _done(path):
    if not path.exists():
        return set()
    with open(path) as f:
        return {json.loads(l)["case_id"] for l in f if l.strip()}


def collect(model, cases, out_dir, workers=4):
    path = Path(out_dir) / f"answers__{slug(model)}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    todo = [c for c in cases if c["case_id"] not in _done(path)]

    def one(c):
        try:
            return c, complete(model, SUBJECT_SYSTEM, c["prompt"]), None
        except Exception as e:  # keep going; failed rows are retried on the next run
            return c, None, str(e)

    errors = 0
    with ThreadPoolExecutor(workers) as pool, open(path, "a") as out:
        for fut in as_completed([pool.submit(one, c) for c in todo]):
            c, answer, err = fut.result()
            if err:
                errors += 1
                print(f"  {model} {c['case_id']}: {err[:200]}")
                continue
            out.write(json.dumps({"model": model, "case_id": c["case_id"], "answer": answer}, ensure_ascii=False) + "\n")
            out.flush()
    print(f"{model}: {len(todo) - errors} new answers, {errors} errors -> {path}")
    return path
