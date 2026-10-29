# Ylab Health-Worker Evals: Kenya hypertension and diabetes

**Can AI assistants give a nurse in a Kenyan health centre a safe, guideline-correct answer, in English and in Swahili?**

This is an open evaluation of frontier models on the questions primary-care health workers actually ask about the two chronic diseases that fill Kenyan outpatient clinics: hypertension and diabetes. Every case is grounded in the Kenya Ministry of Health's national guidelines, and every case is asked twice, once in English and once in Swahili.

It is a [Ylab](https://ylab.co) project. Ylab helps public institutions deploy and evaluate AI.

## Why this exists

Ministries, NGOs and funders are putting AI assistants in front of health workers. The usual benchmarks (medical licensing exams, English multiple choice) don't tell a ministry what it needs to know before it deploys:

- Does the model follow **our** national guideline, or a US or UK one?
- Does it stay safe in the cases where a wrong answer hurts someone (pre-eclampsia, DKA, sulphonylurea hypoglycaemia, ACE inhibitors in pregnancy)?
- Does it know when a dispensary should **refer** instead of treat?
- Does quality hold up in **Swahili**, or only in English?
- Does it account for stock-outs, missing labs and a doctor who isn't there?

## What's in it

| | |
|---|---|
| Cases | 90 clinical questions (45 hypertension, 45 diabetes), each in English and Swahili = **180 prompts** |
| Grounding | Kenya National Guidelines for Cardiovascular Diseases Management (2018); Kenya National Clinical Guidelines for Management of Diabetes Mellitus (2010). Page references on every case |
| Categories | diagnosis, treatment, dosing, emergency, pregnancy, monitoring, referral, counselling, safety |
| High-stakes | 25 cases flagged critical; 21 where referral is part of the right answer |
| Rubric | per case: required points (`must`), unsafe actions (`must_not`), referral expectation, grader notes where guidelines are ambiguous or out of date |
| Grading | LLM judge scores each required point and unsafe action separately; a clinician spot-checks a stratified sample, and judge-human agreement is reported |

See [METHODOLOGY.md](METHODOLOGY.md) for scoring and limitations.

## Run it

Python 3.10+, no dependencies.

```bash
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GEMINI_API_KEY=...

# 1. collect answers (resumable; --limit 5 for a smoke test)
python -m ylab_evals run --models anthropic:claude-opus-5-5 openai:gpt-5 google:gemini-2.5-pro

# 2. grade with a judge model (run with two judges from different labs to check for self-preference)
python -m ylab_evals grade --judge anthropic:claude-opus-5-5
python -m ylab_evals grade --judge openai:gpt-5

# 3. summary tables -> results/REPORT.md
python -m ylab_evals report

# 4. clinician review sheet -> results/spot_check.csv, then measure agreement
python -m ylab_evals spot-check --per-model 20
python -m ylab_evals agreement results/spot_check.csv
```

Test the pipeline offline with `--models mock:good mock:bad` and `--judge mock:judge`.

To edit cases, change `cases/source_cases.py` and run `python cases/build_cases.py`.

## Results

Coming soon. See `results/REPORT.md` after a run.

## Status and caveats

- **Swahili prompts are first drafts** awaiting native-speaker clinical review. Until that review is done, results on the Swahili set are provisional.
- **The diabetes guideline is from 2010.** Where it differs from current international practice (metformin thresholds, metformin in pregnancy, GDM cut-offs), the case says so in a grader note and accepts either answer if it is safe.
- This is an evaluation, **not a clinical tool**. Nothing here should be used to treat patients.

## License

Code: MIT. Cases and rubric: CC BY 4.0. Please cite as *Ylab Health-Worker Evals (2026)*.

Contributions welcome, especially from Kenyan clinicians, and from anyone who wants to add another country's guidelines.
