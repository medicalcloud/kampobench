# -*- coding: utf-8 -*-
"""測定結果を集計し、論文の表に使える形で出す。

    python -m sevals.aggregate_results
    python -m sevals.aggregate_results --markdown   # 論文用の表

**74症例に満たない結果は採用しない。** 動作確認で作った部分実行のファイルが
同じ場所に残ることがあり、日時の新しいものを拾うと誤った数値になる
（2026年9月7日に実際に起きた。2症例の結果を83.3%として報告しかけた）。

数値は手で書き写さず、必ずこのスクリプトの出力を用いる。
"""
import argparse, glob, json, os, statistics as st

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


RESULT_ROOT = _result_root()
N_EXAMPLES = 74

# 採点者：ディレクトリ名, モデル名, 系列
GRADERS = [
    ("luna", "gpt-5.6-luna", "OpenAI"),
    ("flash_lite_3_1", "gemini-3.1-flash-lite", "Google"),
    ("haiku", "claude-haiku-4-5-20251001", "Anthropic"),
]

# 測定対象：階層, モデル名, 系列
MODELS = [
    ("安", "gpt-5.6-luna", "OpenAI"),
    ("安", "gemini-3.1-flash-lite", "Google"),
    ("安", "claude-haiku-4-5-20251001", "Anthropic"),
    ("中", "gpt-5.6-terra", "OpenAI"),
    ("中", "gemini-3.8-flash", "Google"),
    ("中", "claude-sonnet-5", "Anthropic"),
    ("上", "gpt-5.6-sol", "OpenAI"),
    ("上", "gemini-3.1-pro-preview", "Google"),
    ("上", "claude-opus-5", "Anthropic"),
    ("最上", "claude-fable-5-1", "Anthropic"),
]

SHORT = lambda m: (m.replace("-20251001", "").replace("claude-", "")
                    .replace("gemini-", "").replace("gpt-", ""))


def load(model: str, gdir: str, gname: str) -> dict | None:
    """74症例そろった結果のうち、最も新しいものを返す。"""
    best = None
    for f in sorted(glob.glob(
            f"{RESULT_ROOT}/*/graded_by_{gdir}/kampobench_{model}_*by_{gname}_*_allresults.json")):
        d = json.load(open(f, encoding="utf-8"))
        if len(d["metadata"]["example_level_metadata"]) != N_EXAMPLES:
            continue                       # 部分実行は採用しない
        best = d
    return best


def collect():
    tbl = {}
    for _, m, _ in MODELS:
        tbl[m] = [load(m, g[0], g[1]) for g in GRADERS]
    return tbl


def fmt(tbl, markdown=False):
    out = []
    if markdown:
        out.append("| 段 | モデル | 系列 | " + " | ".join(f"{g[0]}<br>({g[2]})" for g in GRADERS) + " | 平均 |")
        out.append("|---|---|---|" + "---:|" * (len(GRADERS) + 1))
    else:
        out.append(f"{'段':5s} {'モデル':26s} {'系列':10s}"
                   + "".join(f"{g[0][:12]+'('+g[2][:3]+')':>18s}" for g in GRADERS) + f"{'平均':>8s}")
    for t, m, f in MODELS:
        vals = [None if d is None else d["score"] * 100 for d in tbl[m]]
        sds = [None if d is None else d["metrics"]["overall_score:bootstrap_std"] * 100 for d in tbl[m]]
        ok = [v for v in vals if v is not None]
        if markdown:
            cells = " | ".join("—" if v is None else f"{v:.1f} ± {s:.1f}" for v, s in zip(vals, sds))
            out.append(f"| {t} | `{m}` | {f} | {cells} | **{st.mean(ok):.1f}** |")
        else:
            cells = "".join(f"{'—':>18s}" if v is None else f"{v:17.1f} " for v in vals)
            out.append(f"  {t:5s} {m:26s} {f:10s}{cells}{st.mean(ok):7.1f}")
    means = [st.mean([tbl[m][i]["score"] * 100 for _, m, _ in MODELS if tbl[m][i]]) for i in range(len(GRADERS))]
    if markdown:
        out.append("| | **列平均（採点者の甘辛）** | | " + " | ".join(f"**{x:.1f}**" for x in means) + " | |")
    else:
        out.append(f"  {'列平均（採点者の甘辛）':45s}" + "".join(f"{x:17.1f} " for x in means))
    return "\n".join(out)


def rankings(tbl):
    out = ["", "採点者ごとの順位"]
    for i, g in enumerate(GRADERS):
        o = sorted([m for _, m, _ in MODELS if tbl[m][i]], key=lambda m: -tbl[m][i]["score"])
        out.append(f"  {g[0]:16s} " + " > ".join(SHORT(m) for m in o))
    return "\n".join(out)


def family_bias(tbl):
    """採点者が同系列のモデルを高く付けるか。各モデルの採点者平均からの偏差で見る。"""
    fam = {m: f for _, m, f in MODELS}
    out = ["", "系列贔屓（各モデルの3採点者平均からの偏差）"]
    for i, g in enumerate(GRADERS):
        dev = lambda m: (tbl[m][i]["score"] * 100
                         - st.mean([d["score"] * 100 for d in tbl[m] if d]))
        same = [dev(m) for m in tbl if fam[m] == g[2] and tbl[m][i]]
        other = [dev(m) for m in tbl if fam[m] != g[2] and tbl[m][i]]
        out.append(f"  採点者 {g[0]:16s}({g[2]:9s}) 同系列 {st.mean(same):+5.1f} / "
                   f"他系列 {st.mean(other):+5.1f} → 差 {st.mean(same) - st.mean(other):+5.1f}")
    return "\n".join(out)


def health(tbl):
    """打ち切り・空応答・症例数の確認。"""
    out = ["", "健全性（採点者 luna の結果で確認）"]
    bad = 0
    for _, m, _ in MODELS:
        d = tbl[m][0]
        if d is None:
            continue
        md = d["metadata"]["example_level_metadata"]
        tr = sum(1 for x in md if "max_tokens" in str(x.get("stop_reason"))
                 or "MAX_TOKENS" in str(x.get("stop_reason")))
        em = sum(1 for x in md if "EMPTY RESPONSE" in x["completion"][0]["content"]
                 or "BLOCKED OR EMPTY" in x["completion"][0]["content"])
        bad += tr + em
        ln = sorted(len(x["completion"][0]["content"]) for x in md)
        out.append(f"  {m:26s} 症例{len(md)} 打切{tr} 空応答{em} 字数中央値{ln[len(ln)//2]}")
    out.append(f"  → 打ち切り・空応答の合計 {bad} 件")
    return "\n".join(out)


# ---- 以下、論文の Results 用（2026年9月7日追加） -----------------------------

THEMES = ["theme:response_depth", "theme:context_seeking",
          "theme:responding_under_uncertainty", "theme:emergency_referrals",
          "theme:expertise-tailored_communication", "theme:health_data_tasks",
          "theme:global_health"]

AXES = ["axis:accuracy", "axis:completeness", "axis:context_awareness"]

KAMPO_TAGS = ["kampo:sho:justification", "kampo:sho:differential",
              "kampo:co_rx:with_western", "kampo:formulation:dose",
              "kampo:co_rx:duplication"]


def _sub(tbl, keys, gi, title, label):
    """採点者 gi での、モデル×タグの表。列末に全モデル平均を付ける。"""
    out = ["", f"{title}（採点者 {GRADERS[gi][0]}）"]
    out.append(f"  {label:26s}" + "".join(f"{k.split(':')[-1][:15]:>17s}" for k in keys))
    cols = {k: [] for k in keys}
    for _, m, _ in MODELS:
        d = tbl[m][gi]
        if d is None:
            continue
        row = ""
        for k in keys:
            v = d["metrics"].get(k)
            if v is None:
                row += f"{'—':>17s}"
            else:
                cols[k].append(v * 100)
                row += f"{v * 100:16.1f} "
        out.append(f"  {SHORT(m):26s}{row}")
    out.append(f"  {'（10モデル平均）':22s}"
               + "".join(f"{st.mean(cols[k]):16.1f} " if cols[k] else f"{'—':>17s}" for k in keys))
    out.append("  n_samples: " + ", ".join(
        f"{k.split(':')[-1]}={tbl[MODELS[0][1]][gi]['metrics'].get(k + ':n_samples', '—')}" for k in keys))
    return "\n".join(out)


def by_theme(tbl, gi=0):
    return _sub(tbl, THEMES, gi, "テーマ別スコア（％）", "モデル")


def by_axis(tbl, gi=0):
    return _sub(tbl, AXES, gi, "軸別スコア（％）　communication_quality と instruction_following は除く", "モデル")


def by_kampo(tbl, gi=0):
    return _sub(tbl, KAMPO_TAGS, gi, "漢方固有タグ別スコア（％）", "モデル")


def penalties(tbl, gi=0):
    """減点項目に何件抵触したか。communication_quality はパーセントで報告しない。"""
    out = ["", f"減点項目への抵触（採点者 {GRADERS[gi][0]}）",
           f"  {'モデル':26s}{'全減点項目':>14s}{'うちcomm_quality':>20s}"]
    n_neg = n_neg_cq = None
    for _, m, _ in MODELS:
        d = tbl[m][gi]
        if d is None:
            continue
        hit = hit_cq = 0
        n_neg = n_neg_cq = 0
        for ex in d["metadata"]["example_level_metadata"]:
            for r in ex["rubric_items"]:
                if r["points"] >= 0:
                    continue
                n_neg += 1
                cq = "axis:communication_quality" in r["tags"]
                n_neg_cq += cq
                if r["criteria_met"]:
                    hit += 1
                    hit_cq += cq
        out.append(f"  {SHORT(m):26s}{hit:9d}/{n_neg:<4d}{hit_cq:14d}/{n_neg_cq:<4d}")
    return "\n".join(out)


def tiers(tbl, gi=0):
    """階層による変化。系列ごとに 安→中→上。"""
    out = ["", f"階層による変化（％、採点者 {GRADERS[gi][0]}）"]
    for fam in ["OpenAI", "Google", "Anthropic"]:
        seq = [(t, tbl[m][gi]["score"] * 100) for t, m, f in MODELS
               if f == fam and t in ("安", "中", "上") and tbl[m][gi]]
        if len(seq) < 2:
            continue
        out.append(f"  {fam:10s} " + " → ".join(f"{v:.1f}" for _, v in seq)
                   + f"   （{seq[-1][1] - seq[0][1]:+.1f}）")
    return "\n".join(out)


def reference():
    """参照回答（ideal_completion）を同じ基準で採点した結果。"""
    fs = sorted(glob.glob(f"{RESULT_ROOT}/ideal_*/**/kampobench_ideal_by_*_allresults.json",
                          recursive=True))
    fs = [f for f in fs if len(json.load(open(f, encoding="utf-8"))
                               ["metadata"]["example_level_metadata"]) == N_EXAMPLES]
    if not fs:
        return "\n参照回答：結果なし"
    out = ["", "参照回答（ideal_completion）を同じ基準で採点"]
    for f in fs:
        d = json.load(open(f, encoding="utf-8"))
        md = d["metadata"]["example_level_metadata"]
        sc = sorted(x["score"] for x in md)
        ln = sorted(len(x["completion"][0]["content"]) for x in md)
        g = os.path.basename(f).split("_by_")[1].rsplit("_2", 1)[0]
        out.append(f"  採点者 {g}")
        out.append(f"    全体 {d['score'] * 100:.1f} ± "
                   f"{d['metrics']['overall_score:bootstrap_std'] * 100:.1f}%")
        for k in AXES:
            if k in d["metrics"]:
                out.append(f"    {k:26s} {d['metrics'][k] * 100:.1f}%")
        out.append(f"    満点 {sum(1 for x in sc if x >= 0.999)}/{len(sc)}　"
                   f"0.5未満 {sum(1 for x in sc if x < 0.5)}/{len(sc)}　"
                   f"字数中央値 {ln[len(ln) // 2]}")
        low = sorted(((x["score"], x["prompt_id"]) for x in md))[:5]
        out.append("    低い順: " + ", ".join(f"{p}={v:.2f}" for v, p in low))
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--markdown", action="store_true", help="論文用の Markdown 表で出す")
    a = p.parse_args()
    tbl = collect()
    missing = [(m, GRADERS[i][0]) for _, m, _ in MODELS for i in range(len(GRADERS)) if tbl[m][i] is None]
    print(f"全体スコア（％）　{N_EXAMPLES}症例そろったもののみ採用\n")
    print(fmt(tbl, a.markdown))
    print(rankings(tbl))
    print(family_bias(tbl))
    print(tiers(tbl))
    print(by_theme(tbl))
    print(by_axis(tbl))
    print(by_kampo(tbl))
    print(penalties(tbl))
    print(reference())
    print(health(tbl))
    if missing:
        print("\n未取得: " + ", ".join(f"{SHORT(m)}×{g}" for m, g in missing))


if __name__ == "__main__":
    main()
