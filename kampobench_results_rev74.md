# KampoBench results (74 physician-reviewed scenarios)

**Written**: 7 September 2026
**Data**: `jsonl/kampobench_pilot_samples_reviewed.jsonl` (74 scenarios, 310 criteria)
**Conditions**: `kampobench_measurement_settings.md`
**Result files**: `tmp/results_rev74/<price tier>/graded_by_<grader>/`
日本語版は `kampobench_results_rev74_jp.md` にあります。

**Do not copy the numbers by hand.** Take them from the output of
`python -m sevals.aggregate_results`. Results covering fewer than 74 scenarios are
excluded automatically.

---

## Design

One model per capability tier from each of the three vendors (OpenAI, Google, Anthropic)
gives nine models; `claude-fable-5-1`, Anthropic's newest, makes ten. **Every response was
graded by a grading model from each of the three vendors, to check for family bias.**

**Responses were generated once and re-graded** (`grade_saved.py`), so the grader is the
only variable between the three sets of scores.

---

## Overall scores (%)

| Tier | Model | Vendor | luna<br>(OpenAI) | flash_lite_3_1<br>(Google) | haiku<br>(Anthropic) | Mean |
|---|---|---|---:|---:|---:|---:|
| Low | `gpt-5.6-luna` | OpenAI | 58.6 ± 3.7 | 71.5 ± 2.8 | 63.5 ± 3.7 | **64.5** |
| Low | `gemini-3.1-flash-lite` | Google | 49.0 ± 3.9 | 64.7 ± 3.1 | 56.1 ± 3.9 | **56.6** |
| Low | `claude-haiku-4-5-20251001` | Anthropic | 36.9 ± 3.4 | 51.0 ± 3.4 | 39.1 ± 3.3 | **42.4** |
| Mid | `gpt-5.6-terra` | OpenAI | 58.2 ± 3.6 | 74.6 ± 2.8 | 62.7 ± 3.4 | **65.2** |
| Mid | `gemini-3.8-flash` | Google | 65.1 ± 3.5 | 80.3 ± 2.8 | 74.1 ± 3.4 | **73.1** |
| Mid | `claude-sonnet-5` | Anthropic | 57.1 ± 4.1 | 68.3 ± 3.4 | 62.9 ± 3.9 | **62.8** |
| High | `gpt-5.6-sol` | OpenAI | 61.0 ± 3.5 | 76.4 ± 2.8 | 66.2 ± 3.8 | **67.9** |
| High | `gemini-3.1-pro-preview` | Google | 61.0 ± 3.7 | 78.0 ± 2.7 | 69.9 ± 3.6 | **69.6** |
| High | `claude-opus-5` | Anthropic | 74.8 ± 3.1 | 86.3 ± 2.7 | 81.2 ± 2.8 | **80.8** |
| Top | `claude-fable-5-1` | Anthropic | 72.2 ± 3.4 | 86.2 ± 2.6 | 81.4 ± 2.9 | **80.0** |
| | **Column mean (grader leniency)** | | **59.4** | **73.7** | **65.7** | |

The reference answers (`ideal_completion`) reach 87.9 ± 2.3% (grader luna).

## Rankings

    By grader
      luna             opus-5 > fable-5-1 > 3.8-flash > 5.6-sol > 3.1-pro-preview > 5.6-luna > 5.6-terra > sonnet-5 > 3.1-flash-lite > haiku-4-5
      flash_lite_3_1   opus-5 > fable-5-1 > 3.8-flash > 3.1-pro-preview > 5.6-sol > 5.6-terra > 5.6-luna > sonnet-5 > 3.1-flash-lite > haiku-4-5
      haiku            fable-5-1 > opus-5 > 3.8-flash > 3.1-pro-preview > 5.6-sol > 5.6-luna > sonnet-5 > 5.6-terra > 3.1-flash-lite > haiku-4-5

## Observations

**1. The ranking barely moves when the grader changes.**
The top two (`claude-opus-5`, `claude-fable-5-1`) are first and second under all three
graders. They swap places, but by 0.2 to 2.6 points, within the noise. The order below
them is nearly the same as well.

**2. No family favoritism was detected.**

    Family favoritism (deviation from each model's mean over the three graders)
      grader luna            (OpenAI   ) own family  -6.6 / others  -7.0 -> difference  +0.4
      grader flash_lite_3_1  (Google   ) own family  +7.9 / others  +7.3 -> difference  +0.6
      grader haiku           (Anthropic) own family  -0.3 / others  -0.7 -> difference  +0.4

Measured as the deviation from each model's mean over the three graders, a grader favors
its own family by **0.4 to 0.6 points**, far below the noise of a single measurement
(about ±3). **The suspicion that Gemini ranked high because a Gemini model did the
grading is refuted by the data.**

**3. Grader leniency spans 14.3 points** (luna 59.4 to flash_lite 73.7). It does not
change the ranking, but **an absolute score is meaningless without naming the grader**.

**4. Price tiers behave differently by vendor** (grader luna).

```
OpenAI     low 58.6 -> mid 58.2 -> high 61.0    (+2.4) almost flat, across a 20-fold price range
Google     low 49.0 -> mid 65.1 -> high 61.0    (+12.0) peaks at the mid tier
Anthropic  low 36.9 -> mid 57.1 -> high 74.8    (+37.9) rises throughout
```

**Comparing only the cheapest model of each vendor tells you nothing about the vendors.**

**5. The top two models stand out on `context_awareness`** (opus-5 67.1%, fable-5-1
59.5%); the other eight range from 21.6% to 46.8%. The ability to ask for information the
user has not given differs sharply, and a Kampo consultation needs it.

**6. `claude-fable-5-1` did not beat `claude-opus-5`** (72.2% against 74.8%, grader luna).
The difference is within the noise and they should be read as equal, but fable-5-1 costs
twice as much ($10/$50 against $5/$25).

## Health of the runs

    Checked on the results graded by luna
      gpt-5.6-luna               74 scenarios, 0 truncated, 0 empty, median 1,490 characters
      gemini-3.1-flash-lite      74 scenarios, 0 truncated, 0 empty, median 1,627
      claude-haiku-4-5-20251001  74 scenarios, 0 truncated, 0 empty, median 898
      gpt-5.6-terra              74 scenarios, 0 truncated, 0 empty, median 1,831
      gemini-3.8-flash           74 scenarios, 0 truncated, 0 empty, median 1,936
      claude-sonnet-5            74 scenarios, 0 truncated, 0 empty, median 1,182
      gpt-5.6-sol                74 scenarios, 0 truncated, 0 empty, median 965
      gemini-3.1-pro-preview     74 scenarios, 0 truncated, 0 empty, median 2,054
      claude-opus-5              74 scenarios, 0 truncated, 0 empty, median 2,895
      claude-fable-5-1           74 scenarios, 0 truncated, 0 empty, median 2,005
      -> 0 truncated or empty responses in total

## How this is reported in the paper (decided 7 September 2026)

**All three graders' scores are given in the table**, together with the finding that no
family favoritism was detected. That lets the reader check the point rather than trusting
a single grader's numbers.

## On the record: an error made on 7 September 2026

While aggregating, `gemini-3.1-flash-lite` was almost reported at 83.3% under the haiku
grader, which would have put it first overall. The figure came from **a file covering
only two scenarios**, made while testing the cache and left in the same directory; the
newer timestamp won. The correct value is 56.1%.

In response, **`aggregate_results.py` now excludes any result covering fewer than 74
scenarios**, and the offending file was deleted. Numbers must always be taken from that
script.
