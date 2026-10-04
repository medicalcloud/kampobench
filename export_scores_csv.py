# -*- coding: utf-8 -*-
"""測定結果から、採点の可否だけを取り出した CSV を作る（公開用）。

    python -m sevals.export_scores_csv            # dataset_release/ に出力

出力するのは「どの基準を満たしたか」の真偽と、配点・タグ・症例スコアのみである。
**モデルの回答文と、採点者の説明文は含めない。** 基準の文も含めず、
`prompt_id` と `criterion_index` でデータ本体（JSONL）と突き合わせる。

採用するファイルの選び方は `aggregate_results.py` と同一である
（74症例そろったもののうち最も新しいもの）。論文の表と同じ数値が再現できる。
"""
import csv, glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def _result_root() -> str:
    """結果の置き場を探す。環境変数 > このファイルの隣 > 親ディレクトリ の順。"""
    env = os.environ.get("KAMPOBENCH_RESULTS")
    if env:
        return env
    for cand in (os.path.join(HERE, "tmp", "results_rev74"),
                 os.path.join(os.path.dirname(HERE), "tmp", "results_rev74")):
        if os.path.isdir(cand):
            return cand
    return os.path.join(HERE, "tmp", "results_rev74")


def _out_path() -> str:
    """書き出し先。dataset_release があればそこへ、なければこのファイルの隣へ。"""
    rel = os.path.join(os.path.dirname(HERE), "dataset_release")
    d = rel if os.path.isdir(rel) else HERE
    return os.path.join(d, "kampobench_results_rev74_scores.csv")


BASE = os.path.dirname(HERE)
ROOT = _result_root()
OUT = _out_path()
N = 74

GRADERS = [("luna", "gpt-5.6-luna", "OpenAI"),
           ("flash_lite_3_1", "gemini-3.1-flash-lite", "Google"),
           ("haiku", "claude-haiku-4-5-20251001", "Anthropic")]

MODELS = [("low", "gpt-5.6-luna", "OpenAI"),
          ("low", "gemini-3.1-flash-lite", "Google"),
          ("low", "claude-haiku-4-5-20251001", "Anthropic"),
          ("mid", "gpt-5.6-terra", "OpenAI"),
          ("mid", "gemini-3.8-flash", "Google"),
          ("mid", "claude-sonnet-5", "Anthropic"),
          ("high", "gpt-5.6-sol", "OpenAI"),
          ("high", "gemini-3.1-pro-preview", "Google"),
          ("high", "claude-opus-5", "Anthropic"),
          ("top", "claude-fable-5-1", "Anthropic"),
          ("reference", "ideal", "physician-revised")]


def load(model, gdir, gname):
    """74症例そろった結果のうち、最も新しいものを返す（aggregate_results と同じ規則）。"""
    best = None
    for f in sorted(glob.glob(
            f"{ROOT}/*/graded_by_{gdir}/kampobench_{model}_*by_{gname}_*_allresults.json")):
        d = json.load(open(f, encoding="utf-8"))
        if len(d["metadata"]["example_level_metadata"]) == N:
            best = (d, os.path.relpath(f, BASE))
    return best


def main():
    rows, sources, missing = [], [], []
    for tier, model, vendor in MODELS:
        for gdir, gname, gvendor in GRADERS:
            got = load(model, gdir, gname)
            if got is None:
                missing.append((model, gname))
                continue
            d, path = got
            sources.append((model, gname, path, round(d["score"] * 100, 2)))
            for e in d["metadata"]["example_level_metadata"]:
                for i, r in enumerate(e["rubric_items"]):
                    rows.append({
                        "model": model, "vendor": vendor, "tier": tier,
                        "grader": gname, "grader_vendor": gvendor,
                        "prompt_id": e["prompt_id"], "criterion_index": i,
                        "points": r["points"], "tags": "|".join(r["tags"]),
                        "criteria_met": int(bool(r["criteria_met"])),
                        "example_score": round(e["score"], 6),
                    })
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)

    print(f"{OUT}: {len(rows):,} 行")
    print(f"採用した結果ファイル: {len(sources)} 件")
    for m, g, p, s in sources:
        print(f"  {m:28s} by {g:28s} {s:5.1f}%  {p}")
    if missing:
        print("欠測:", missing)


if __name__ == "__main__":
    main()
