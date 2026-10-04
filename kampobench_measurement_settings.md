# KampoBench measurement conditions

**Written**: 4 September 2026. **Subject**: the measurements on the 74 physician-reviewed
scenarios (`jsonl/kampobench_pilot_samples_reviewed.jsonl`).
日本語版は `kampobench_measurement_settings_jp.md` にあります。

The Methods of the English paper draw on this file. **No value here is guessed.** What
can be established from the code is kept separate from what has not been checked.

---

## 1. System message: `None` for every model

No system message is given to any of the 21 candidate models.

### What changed since the previous measurement (19 May 2026)

Previously there were three different settings.

| Model | Previously |
|---|---|
| gpt-5.5 / gpt-5-mini | none |
| gemini models | `"You are a helpful assistant."` |
| **claude-sonnet-4-5-20250929** | **`CLAUDE_SYSTEM_MESSAGE_LMSYS`** |
| claude-haiku-4-5-20251001 | none |

`CLAUDE_SYSTEM_MESSAGE_LMSYS` comes from upstream simple-evals and tells the model that
the date is 1 April 2024, that its knowledge ends in August 2023, and that it should
answer simple questions concisely. Of the eight models, only Claude Sonnet 4.5 was
measured under it. The instruction to be concise in particular can count against criteria
that ask for completeness (253 of the 310 criteria carry `axis:completeness`). Its effect
on that model's low score in the previous measurement cannot be ruled out.

**To remove this inconsistency, every model is now given `None`.** The conditions differ
from those of the previous measurement, so the numbers must not be compared directly.

---

## 2. Temperature: not sent (each API's default applies)

**No temperature is specified.** The `temperature` of each sampler defaults to `None`,
and the request then carries no temperature. The gpt-5 and Claude 5 families do not
accept a temperature at all and return an error if given one, so none is sent to them
either.

### Background

The default of 0.5 in `GeminiCompletionSampler` was **merely what the upstream code said**
and is not the default of the Google API. The Models API reports the Gemini default as
**1.0** (`temperature=1`, `maxTemperature=2`, `topP=0.95`, `topK=64`; checked 4 September
2026). Rather than carry that discrepancy into the measurement, the samplers were set to
`None` and the choice of temperature was left to each API.

### Run-to-run variation

In the stage-0 measurement, `gemini-3.1-flash-lite` was run twice and the overall score
moved by **5 points** (54.0% to 49.0%). This is variation between runs, distinct from the
bootstrap standard deviation (3.9). Since no temperature is sent, this variation remains;
keep it in mind when discussing rankings.

### Wording for the paper

> Sampling parameters were not tuned for this benchmark; the configuration used is
> distributed with the evaluation code.

---

## 3. Output limit (max_tokens): 20,000 for every model

**This is a safety margin, not a matched condition.** What must be equal across models is
not the number but the fact that no response is cut off. The limit is a ceiling, not a
target, and cost follows what is actually generated.

### Why the numbers should not be matched

For a reasoning model, max_tokens covers thinking and answer together. At the same
number, a model that does not think can spend all of it on the answer while a model that
thinks can spend only part. **Matching the number makes the comparison less fair, not
more.**

A truncated response loses points on completeness, but that is not the model failing to
answer: it is us cutting it off. In a benchmark where 80% of the criteria ask about
completeness, that is a systematic error.

### Truncation as measured (4 September 2026, scenario kb_0020)

**With max_tokens = 4096**

```
claude-opus-5      stop=max_tokens  4,096 output tokens  1,084-character answer  thinking blocks present  <- truncated
claude-sonnet-5    stop=end_turn    2,475 output tokens  2,304-character answer
claude-opus-4-8    stop=end_turn    2,129 output tokens  1,933-character answer
claude-haiku-4-5   stop=end_turn    3,127 output tokens  3,235-character answer
```

claude-opus-5 spent more than 3,000 tokens on thinking and its answer was cut at 1,084
characters.

**After raising max_tokens to 20,000**

```
claude-opus-5      stop_reason=end_turn           4,123-character answer
claude-haiku-4-5   stop_reason=end_turn           1,911-character answer
gemini-3.8-flash   stop_reason=FinishReason.STOP  2,510-character answer
gpt-5.6-sol        stop_reason=completed          2,311-character answer
```

On the same scenario the answer grew from 1,084 to 4,123 characters, **about fourfold**.

### Traces left in the previous measurement (4096 / 8192 / 20000)

The longest answer from claude-haiku-4-5 (4,075 characters) ends mid-sentence. In the
previous measurement the median answer length was 750 to 881 characters for the Claude
models against 1,600 to 2,400 for gemini and gpt. How much of that gap came from the
difference in limits cannot be separated out from those data.

### Recording truncation

The samplers put `stop_reason` into `response_metadata`, and `healthbench_eval.py` keeps
it in `example_level_metadata`, so truncation can be counted after a run.

| Provider | Value indicating truncation |
|---|---|
| Anthropic | `stop_reason == "max_tokens"` |
| Google | `stop_reason` contains `MAX_TOKENS` |
| OpenAI | `stop_reason == "incomplete"` and `incomplete_reason == "max_output_tokens"` |

**The paper states that truncation was checked and found to be zero.** Had any remained,
the models and counts would be named.

---

## 4. Candidate models (21)

The eight models measured previously, plus thirteen released after 19 May 2026.

**Anthropic**: claude-sonnet-4-5-20250929, claude-haiku-4-5-20251001, claude-opus-4-8,
claude-fable-5, claude-sonnet-5, claude-opus-5, claude-fable-5-1

**OpenAI**: gpt-5.5, gpt-5-mini, gpt-5.6-luna, gpt-5.6-terra, gpt-5.6-sol
(luna, terra and sol are capability tiers, sol > terra > luna)

**Google**: gemini-2.5-flash, gemini-3-flash-preview, gemini-3.1-pro-preview,
gemini-3.1-flash-lite, gemini-3.5-flash, gemini-3.5-flash-lite, gemini-3.6-flash,
gemini-3.7-flash, gemini-3.8-flash
(3.1 is the latest Pro; from 3.5 onward only Flash models have been released)

All 21 were confirmed to respond through the existing samplers (4 September 2026).

---

## 5. How to run

Run from the parent directory of the package. **Do not start python inside the package
directory**, because `types.py` there shadows the standard library `types`.

```
python -m sevals.simple_evals --eval=kampobench --model=<model> --n-threads 10
```

API keys are read from the environment. Note that variables already set in the shell can
override those in an `.env` file; load it with `set -a && . ./.env && set +a` if you use
one.

---

## 6. `communication_quality` is not reported as a percentage (decided 4 September 2026)

Of the 16 criteria on `axis:communication_quality`, **15 deduct points and only one
awards them** (kb_0021, +1). Since a score is the points obtained divided by the total
positive points, **the denominator of this axis is 1 point across all 74 scenarios**.

In the stage-0 measurement all three models gave the same result.

```
claude-haiku-4-5        0 of 15 penalty criteria triggered / the single positive criterion not met -> 0%
gemini-3.1-flash-lite   0 of 15 penalty criteria triggered / the single positive criterion not met -> 0%
gpt-5.6-luna            the same                                                                   -> 0%
```

**0% does not mean the communication was terrible.** It means the model triggered no
penalty criterion at all but missed the single opportunity to earn a point. Reporting it
as a percentage misleads.

### Decision

**This axis is reported as the number of penalty criteria triggered, not as a
percentage.** That is how penalty criteria should be read in any case, and the fact that
no model triggered any of them is itself worth reporting.

The data is not altered: this is a matter of aggregation and presentation, and the
measurement itself is sound.

### Tags with the same problem

| Tag | Criteria | Positive points | Penalty criteria | Reported as |
|---|---:|---:|---:|---|
| axis:completeness | 253 | 421 | 0 | percentage |
| axis:accuracy | 146 | 203 | 31 | percentage |
| axis:context_awareness | 45 | 81 | 0 | percentage |
| **axis:communication_quality** | 16 | **1** | 15 | **count of penalties triggered** |
| axis:instruction_following | **0** | 0 | 0 | **no criteria; not reported** |
| kampo:sho:justification | 66 | 126 | 0 | percentage |
| kampo:sho:differential | 53 | 86 | 0 | percentage |
| kampo:co_rx:with_western | 25 | 41 | 0 | percentage |
| kampo:formulation:dose | 21 | 41 | 0 | percentage |
| kampo:co_rx:duplication | 12 | 24 | 0 | percentage |
| **kampo:formulation:administration** | 1 | 1 | 0 | **a single criterion; no percentage** |
| **kampo:sho:general** | 1 | 1 | 0 | **a single criterion; no percentage** |

**Only accuracy, completeness and context awareness can be given as percentages in the
paper.** It must not be described as following all five axes.

---

## 7. Interrupting and resuming a measurement (6 September 2026)

**A run that dies because an API quota is exhausted can be resumed, reusing the calls
already made.**

`SamplerWithRetry` gives up after five attempts and raises, the exception escapes the
thread pool of `map_with_progress`, and the whole run dies. **No result file is written
then.** Even with 73 of the 74 scenarios finished, every token paid for is wasted.

To avoid this, `response_cache.py` **stores each API response on disk, call by call**.

```
tmp/api_cache/<kind>_<model>_<fingerprint of the settings>/<first two characters of the key>/<key>.json
```

- **It works for generating responses and for grading**, since both go through
  `SamplerBase.__call__`
- **Separate settings are kept apart.** The key includes the model name, system message,
  temperature, output limit and reasoning effort, so changing a setting gives a different
  location and old results are not mixed in
- The number of reused responses is printed at the end of a run, so it is clear whether
  resumption worked

### How to use it

**Nothing to do.** It is on by default. If a run dies, issue the same command again.

```
reused 4 / new 4 (50% reused)
```

### As measured (6 September 2026)

| What was checked | Result |
|---|---|
| Running the same measurement twice | The second run **reused everything**: 3 responses and 14 gradings (no charge) |
| Killing a run, then running again | No result file had been written, but the 20 completed responses remained and **about half were reused**, and the run finished |
| Changing only the grader | **Responses reused 100%**, only the grading new. This matches the design of generating once and re-grading |
| Changing the model | A different location; nothing is mixed |
| `--no-cache` | The cache is not used |

### A caution

**Re-running is not an independent trial.** To measure run-to-run variation, add
`--no-cache`. Because no temperature is sent, results can move between runs; for any
discussion of that variation the flag is required.
