# -*- coding: utf-8 -*-
"""測定結果の保存先を決める。

`tmp/results_rev74/<価格帯>/graded_by_<採点者>/` へ振り分ける。
手で移す運用は移し忘れが起きるため、出力の時点で置き場所を決める。

価格帯の区分は kampobench_experiment_matrix.md の設計（3階層×3系列）に対応する。
"""
import os

TMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmp")
RESULT_ROOT = os.path.join(TMP_DIR, "results_rev74")

# モデル → 価格帯
COST_TIER = {
    # 各系列の最安
    "gpt-5.6-luna": "low_cost",
    "gemini-3.1-flash-lite": "low_cost",
    "claude-haiku-4-5-20251001": "low_cost",
    # 各系列の中位
    "gpt-5.6-terra": "middle_cost",
    "gemini-3.8-flash": "middle_cost",
    "claude-sonnet-5": "middle_cost",
    # 各系列の上位
    "gpt-5.6-sol": "high_cost",
    "gemini-3.1-pro-preview": "high_cost",
    "claude-opus-5": "high_cost",
    "claude-fable-5-1": "high_cost",
    "claude-fable-5": "high_cost",
    "claude-opus-4-8": "high_cost",
    "gpt-5.5": "high_cost",
    # 旧世代・補足
    "gemini-2.5-flash": "low_cost",
    "gemini-3.5-flash-lite": "low_cost",
    "gemini-3-flash-preview": "low_cost",
    "gpt-5-mini": "low_cost",
    "gemini-3.6-flash": "middle_cost",
    "gemini-3.7-flash": "middle_cost",
    "gemini-3.5-flash": "middle_cost",
    "claude-sonnet-4-5-20250929": "middle_cost",
}

# 採点者 → ディレクトリ名（短く読みやすい形）
GRADER_DIR = {
    "gpt-5.6-luna": "graded_by_luna",
    "gpt-5.6-terra": "graded_by_terra",
    "gpt-5.6-sol": "graded_by_sol",
    "gemini-3.1-flash-lite": "graded_by_flash_lite_3_1",
    "gemini-3.8-flash": "graded_by_flash_3_8",
    "gemini-3.1-pro-preview": "graded_by_pro_3_1",
    "claude-haiku-4-5-20251001": "graded_by_haiku",
    "claude-sonnet-5": "graded_by_sonnet_5",
    "claude-opus-5": "graded_by_opus_5",
}


def output_dir(model: str, grader: str) -> str:
    """保存先を返し、無ければ作る。

    未登録のモデル・採点者は、取りこぼしを避けるため専用のディレクトリへ落とす
    （静かに tmp/ 直下へ散らばるより、名前で気づけるほうがよい）。"""
    tier = COST_TIER.get(model, "unclassified")
    gdir = GRADER_DIR.get(grader, f"graded_by_{grader}")
    d = os.path.join(RESULT_ROOT, tier, gdir)
    os.makedirs(d, exist_ok=True)
    return d


def ideal_dir(grader: str) -> str:
    """参照回答の採点結果の保存先。"""
    d = os.path.join(RESULT_ROOT, "ideal_20260904",
                     GRADER_DIR.get(grader, f"graded_by_{grader}"))
    os.makedirs(d, exist_ok=True)
    return d
