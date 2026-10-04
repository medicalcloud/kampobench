# KampoBench (derived from simple-evals / HealthBench)

KampoBench is a benchmark for evaluating large language models on Japanese-language
**Kampo** (traditional Japanese medicine) consultations, built on OpenAI's
**HealthBench**. This repository contains a minimally modified copy of `simple-evals`, so
that the KampoBench JSONL can be evaluated on a HealthBench-compatible framework.

**This repository contains the evaluation code only. The data is not included.**

The dataset (74 scenarios, 310 rubric criteria) was drafted by a large language model and
then reviewed and revised by several board-certified Kampo physicians. **It is
distributed separately under CC BY 4.0.**

| | |
|---|---|
| Dataset | https://doi.org/10.5281/zenodo.23129442 (Zenodo) |
| License | CC BY 4.0 (`DATA_LICENSE.md`) |
| Provenance | `jsonl/kampobench_provenance.md` |
| Measurement conditions | `kampobench_measurement_settings.md` |
| Results | `kampobench_results_rev74.md` (ten models, three graders) |

**To help keep the benchmark out of training corpora, please do not repost the contents
of the data in plain text or as images on the open web.** Every example carries a canary
string (`jsonl/kampobench_canary.md`).

日本語版は `README_jp.md` にあります。

## Running KampoBench

### 1. Place the repository

This repository is **run as a package** (it uses relative imports internally). Name the
cloned directory `sevals` and run from **its parent directory**.

```bash
git clone https://github.com/medicalcloud/kampobench.git sevals
cd ..            # run from the parent of sevals
```

If you place it under another name, substitute that name for `sevals`
(for example, `python -m kampobench.simple_evals ...`).

### 2. Obtain the data

The dataset is not in this repository. **Download
`kampobench_pilot_samples_reviewed.jsonl` from Zenodo
(doi:10.5281/zenodo.23129442) and put it in `jsonl/`.**

```
sevals/
└── jsonl/
    └── kampobench_pilot_samples_reviewed.jsonl   <- here
```

The path is defined as `INPUT_PATH_KAMPOBENCH` in `healthbench_eval.py`.

### 3. Dependencies and API keys

```
pip install -r requirements.txt
export OPENAI_API_KEY=...      # required (read when the model registry is built)
export ANTHROPIC_API_KEY=...   # to evaluate or grade with Claude
export GEMINI_API_KEY=...      # to evaluate or grade with Gemini
```

`--eval=kampobench` builds samplers for every model at start-up, so **`OPENAI_API_KEY` is
needed even to measure Claude or Gemini alone** (without it the run stops with
`Please set OPENAI_API_KEY`).

### 4. Measure

```
python -m sevals.simple_evals --eval=kampobench --model=<model> --grader=<grader> --n-threads 10
```

To change the grader without generating the responses again, grade the saved results.

```
python -m sevals.grade_saved --source=<allresults.json> --grader=<grader>
```

### 5. Aggregate

```
python -m sevals.aggregate_results             # overall scores, rankings, family bias
python -m sevals.aggregate_results --markdown  # in the format of the paper's tables
python -m sevals.export_scores_csv             # write the grading outcomes to CSV
```

`aggregate_results` uses only results that cover all 74 scenarios; partial runs are
excluded automatically.

—

### About the HealthBench data

This repository does not include the HealthBench data, since OpenAI makes the same
request about it. Obtain it from https://github.com/openai/simple-evals if you need it.

This project is provided for research. It is not intended to give medical advice and must
not be used for clinical decisions.

—

## What was changed from upstream

- **Samplers for reasoning models**
  - do not send `temperature` to reasoning models such as o1/o3/o4
  - use `max_completion_tokens` where the API requires it
- **Model registry** — entries tidied up and added
- **Input JSONL** — the KampoBench JSONL can be selected in addition to the official
  HealthBench files

See `NOTICE` for attribution to the upstream repository and a summary of the changes.

—

## Requirements

- Python 3.10+ (tested on 3.12)
- API keys
  - `OPENAI_API_KEY` (**required**), `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` (whichever
    vendors you use)

Optional but useful:
- `jq` (for inspecting JSONL)
- `tabulate` (for table output)

Install:

```bash
pip install -r requirements.txt
```

—

## Other evaluations

For KampoBench, see "Running KampoBench" above.

To run the original HealthBench subsets (the data must be obtained separately):

```bash
python -m sevals.simple_evals --eval=healthbench --model=<model>
python -m sevals.simple_evals --eval=healthbench_hard --model=<model>
python -m sevals.simple_evals --eval=healthbench_consensus --model=<model>
```

`--n-threads` sets the degree of parallelism; `--examples` restricts the run to a few
examples.

—

## The dataset

**No data is included in this repository.**

- KampoBench (74 scenarios, 310 rubric criteria): download from Zenodo
  (doi:10.5281/zenodo.23129442) and put it in `jsonl/`. Licensed CC BY 4.0
  (`DATA_LICENSE.md`)
- Schema and tag conventions: `jsonl/kampobench_jsonl_tag_rule.md` (and `_jp.md`)
- Provenance: `jsonl/kampobench_provenance.md`
- Official HealthBench JSONL: obtain from https://github.com/openai/simple-evals and
  place it in `jsonl/` as well

To help keep the benchmark out of training corpora, please do not repost the contents in
plain text or as images on the open web (`jsonl/kampobench_canary.md`).

—

## Reproducibility

- Random seeds are fixed in the code where applicable
- Parallelism is controlled with `--n-threads`

### Temperature is an optional setting

The `temperature` of each sampler defaults to **`None`**, and no temperature is then sent
to the API (each vendor's default applies). To fix a value, state it in the model
registry in `simple_evals.py`, for example `temperature=0.0`. The same mechanism applies
to the models being evaluated and to the graders.

When no temperature is sent, the same model and the same question can give different
results from run to run. Keep this in mind when comparing rankings. Note that the gpt-5
and Claude 5 families do not accept a temperature and return an error if one is given, so
none is sent to them.

—

## Output

An evaluation produces HTML fragments and a summary of metrics (see `common` and the
individual eval classes). Try a small JSONL first before a full run.

—

## Development and contributions

See `CONTRIBUTING.md` for the development workflow and the rules for pull requests.

—

## Citation

If you use this work in research, cite the dataset by its DOI
(10.5281/zenodo.23129442) and see `CITATION.cff` for the software and the accompanying
paper.

—

## License

- **Code**: MIT License (© 2024 OpenAI, © 2025 Hideaki Takata)
- **Data**: CC BY 4.0 (© 2025 Hideaki Takata)

See `LICENSE` for the code and `DATA_LICENSE.md` for the data. The upstream repository and
the changes made to it are described in `NOTICE`.
