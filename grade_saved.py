# -*- coding: utf-8 -*-
"""保存済みの回答（または理想回答）を、指定した採点者で採点し直す。

    python -m sevals.grade_saved --source=ideal --grader=gpt-5.6-luna
    python -m sevals.grade_saved --source=<allresults.json> --grader=gemini-3.8-flash

回答を作り直さずに採点者だけを差し替えられる。採点者の違いを分離して見るために使う
（kampobench_experiment_matrix.md を参照）。

採点・集計は HealthBenchEval をそのまま用いるので、通常の測定と同じ計算になる。
回答を返すだけの差し替えサンプラー（ReplaySampler）を渡す仕組みである。
"""
import argparse, json, os, re
from datetime import datetime

from . import common
from .healthbench_eval import HealthBenchEval, INPUT_PATH_KAMPOBENCH
from .response_cache import wrap as cache_wrap, report as cache_report
from .result_paths import output_dir, ideal_dir
from .types import MessageList, SamplerBase, SamplerResponse

TMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmp")


class ReplaySampler(SamplerBase):
    """あらかじめ用意した回答を返すだけのサンプラー。プロンプトで引き当てる。"""

    def __init__(self, mapping: dict[str, str], label: str):
        self.mapping = mapping
        self.label = label
        self.missing = 0

    @staticmethod
    def key(message_list: MessageList) -> str:
        return json.dumps(message_list, ensure_ascii=False, sort_keys=True)

    def _pack_message(self, role: str, content):
        return {"role": role, "content": content}

    def __call__(self, message_list: MessageList) -> SamplerResponse:
        k = self.key(message_list)
        if k not in self.mapping:
            self.missing += 1
            raise KeyError(f"保存済みの回答に見つからないプロンプトがある（{self.missing}件目）")
        return SamplerResponse(
            response_text=self.mapping[k],
            actual_queried_message_list=message_list,
            response_metadata={"replayed_from": self.label},
        )


def build_mapping(source: str) -> tuple[dict[str, str], str]:
    rows = [json.loads(l) for l in open(INPUT_PATH_KAMPOBENCH, encoding="utf-8")]
    if source == "ideal":
        # 理想回答（Gemini 3.0 の草案に専門医が添削したもの。kampobench_provenance.md 参照）
        m = {ReplaySampler.key(r["prompt"]): r["ideal_completion"] for r in rows
             if r.get("ideal_completion")}
        return m, "ideal_completion"
    # 保存済みの測定結果から回答を取り出す
    d = json.load(open(source, encoding="utf-8"))
    by_id = {r["prompt_id"]: r["prompt"] for r in rows}
    m = {}
    for ex in d["metadata"]["example_level_metadata"]:
        pid = ex["prompt_id"]
        if pid in by_id:
            m[ReplaySampler.key(by_id[pid])] = ex["completion"][0]["content"]
    return m, os.path.basename(source)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True,
                   help="'ideal' か、保存済みの *_allresults.json のパス")
    p.add_argument("--grader", required=True, help="採点者のモデル名")
    p.add_argument("--n-threads", type=int, default=10)
    p.add_argument("--examples", type=int, default=None)
    p.add_argument("--no-cache", action="store_true",
                   help="API応答のキャッシュを使わない（既定は使う）")
    args = p.parse_args()

    from .simple_evals import build_model_registry
    models = build_model_registry()
    if args.grader not in models:
        raise SystemExit(f"採点者 '{args.grader}' がレジストリにない")

    mapping, label = build_mapping(args.source)
    print(f"回答の出所: {label}（{len(mapping)}件）")
    print(f"Grader: {args.grader}")

    sampler = ReplaySampler(mapping, label)
    grader = cache_wrap(models[args.grader], f"grader_{args.grader}", not args.no_cache)
    eval_obj = HealthBenchEval(grader_model=grader, subset_name="kampobench",
                              num_examples=args.examples, n_threads=args.n_threads)
    result = eval_obj(sampler)

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.source == "ideal":
        src_tag = "ideal"
    else:
        # 元ファイル名から対象モデル名を取り出し、どの回答を採点し直したか分かるようにする
        m = re.match(r"kampobench_(.+?)_by_.+", os.path.basename(args.source))
        src_tag = f"{m.group(1)}_replay" if m else "replay"
    stem = f"kampobench_{src_tag}_by_{args.grader}_{date_str}"
    # 参照回答は ideal 用の場所、再採点は元モデルの価格帯へ振り分ける（result_paths.py）
    if args.source == "ideal":
        out = ideal_dir(args.grader)
    else:
        out = output_dir(src_tag.replace("_replay", ""), args.grader)
    with open(f"{out}/{stem}.html", "w", encoding="utf-8") as fh:
        fh.write(common.make_report(result))
    with open(f"{out}/{stem}.json", "w", encoding="utf-8") as fh:
        json.dump({k: v for k, v in result.metrics.items() if k != "chars"} | {"score": result.score},
                  fh, indent=2, ensure_ascii=False)
    with open(f"{out}/{stem}_allresults.json", "w", encoding="utf-8") as fh:
        json.dump({"score": result.score, "metrics": result.metrics,
                   "htmls": result.htmls, "convos": result.convos,
                   "metadata": result.metadata}, fh, indent=2, ensure_ascii=False)
    rep = cache_report([grader])
    if rep: print("キャッシュ:"); print(rep)
    print(f"全体スコア: {result.score*100:.1f}%")
    print(f"出力: {out}/{stem}_allresults.json")


if __name__ == "__main__":
    main()
