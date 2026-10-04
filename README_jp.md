**英語版は `README.md` にあります。**

# KampoBench（simple-evals/HealthBench 派生）

KampoBench は、OpenAI の **HealthBench** を基に、日本語の**漢方（Kampo）医療**シナリオで LLM を評価するためのベンチマークです。本ディレクトリは `simple-evals` の最小限の改変コピーを含み、HealthBench 互換の評価フレームワーク上で KampoBench の JSONL データを評価できます。

**このリポジトリには評価コードのみを収録し、データは含みません。**

データセット（74症例・採点基準310項目）は、大規模言語モデルが草案を生成し、
複数の漢方専門医が査読・修正したものです。**CC BY 4.0 で別途配布します。**

| | |
|---|---|
| データセット | https://doi.org/10.5281/zenodo.23129442（Zenodo） |
| ライセンス | CC BY 4.0（`DATA_LICENSE.md`） |
| 来歴 | `jsonl/kampobench_provenance_jp.md` |
| 測定条件 | `kampobench_measurement_settings_jp.md` |
| 測定結果 | `kampobench_results_rev74_jp.md`（10モデル×3採点者） |

**学習コーパスへの混入を防ぐため、データの内容を平文や画像でウェブ上に再掲しないでください。**
全例にカナリア文字列を埋め込んであります（`jsonl/kampobench_canary.md`／`_jp.md`）。

## KampoBench の実行手順

### 1. リポジトリを配置する

このリポジトリは**パッケージとして実行**します（内部で相対 import を使っています）。
クローンしたディレクトリを `sevals` という名前にし、**その親ディレクトリから**実行してください。

```bash
git clone https://github.com/medicalcloud/kampobench.git sevals
cd ..            # sevals の親ディレクトリに移動して実行する
```

別の名前で置いた場合は、`sevals` をその名前に読み替えてください
（例：`kampobench` なら `python -m kampobench.simple_evals ...`）。

### 2. データを取得する

データセットはこのリポジトリに含まれません。**Zenodo（doi:10.5281/zenodo.23129442）から
`kampobench_pilot_samples_reviewed.jsonl` を取得し、`jsonl/` に置いてください。**

```
sevals/
└── jsonl/
    └── kampobench_pilot_samples_reviewed.jsonl   ← ここに置く
```

読み込み先は `healthbench_eval.py` の `INPUT_PATH_KAMPOBENCH` で定義しています。

### 3. 依存パッケージとAPIキー

```
pip install -r requirements.txt
export OPENAI_API_KEY=...      # 必須（モデルレジストリの生成時に参照されます）
export ANTHROPIC_API_KEY=...   # Claude を評価対象または採点者にするとき
export GEMINI_API_KEY=...      # Gemini を評価対象または採点者にするとき
```

`--eval=kampobench` は起動時に全モデルのサンプラーを生成するため、**Claude や Gemini だけを
測る場合でも `OPENAI_API_KEY` が必要**です（未設定だと `Please set OPENAI_API_KEY` で止まります）。

### 4. 測定する

```
python -m sevals.simple_evals --eval=kampobench --model=<モデル> --grader=<採点者> --n-threads 10
```

回答を生成し直さずに採点者だけを替えるときは、保存済みの結果を使います。

```
python -m sevals.grade_saved --source=<allresults.json> --grader=<採点者>
```

### 5. 集計する

```
python -m sevals.aggregate_results             # 全体スコア・順位・系列バイアス
python -m sevals.aggregate_results --markdown  # 論文の表の形式
python -m sevals.export_scores_csv             # 採点の可否だけを CSV に書き出す
```

`aggregate_results` は74症例そろった結果のみを採用します（部分実行の結果は自動的に除外）。

—

### HealthBench 本家のデータについて

本リポジトリには HealthBench のデータを含みません。OpenAI が同様の依頼をしているためです。
必要な場合は https://github.com/openai/simple-evals から取得してください。

本プロジェクトは研究目的で提供されます。医療アドバイスの提供を目的とせず、臨床判断には利用しないでください。

—

## 含まれる主な変更点

- **推論モデル対応のサンプラ**
  - o1/o3/o4 などの推論モデルで `temperature` を送らない
  - API 仕様に応じて `max_completion_tokens` を使用
- **モデルレジストリの更新**
  - 一部のモデルエントリの整理・追加
- **入力 JSONL の切り替え**
  - HealthBench 公式 JSONL に加え、KampoBench の JSONL を評価対象に設定可能

詳細は `NOTICE` を参照してください（上流リポジトリの帰属と変更概要）。

—

## 要件

- Python 3.10+（3.12 で動作確認）
- APIキー
  - `OPENAI_API_KEY`（**必須**）／`ANTHROPIC_API_KEY`／`GEMINI_API_KEY`（使う系列のもの）

オプション（推奨）:
- `jq`（JSONL の確認）
- `tabulate`（表形式の表示）

インストール:

```bash
pip install -r requirements.txt
```

—

## 使い方

KampoBench の実行は「KampoBench の実行手順」を参照してください。

HealthBench（オリジナル）のサブセットを実行する例（データは別途取得が必要）:

```bash
python -m sevals.simple_evals --eval=healthbench --model=<モデル名>
python -m sevals.simple_evals --eval=healthbench_hard --model=<モデル名>
python -m sevals.simple_evals --eval=healthbench_consensus --model=<モデル名>
```

`--n-threads` は並列度（デフォルトはソース参照）。`--examples` で少数サンプルに絞れます。

—

## データセット

**本リポジトリにデータは含まれません。**

- KampoBench（74症例・採点基準310項目）: Zenodo（doi:10.5281/zenodo.23129442）から取得し、`jsonl/` に置く。
  ライセンスは CC BY 4.0（`DATA_LICENSE_jp.md`）
- スキーマ・タグ規約: `jsonl/kampobench_jsonl_tag_rule.md`（英語）／`jsonl/kampobench_jsonl_tag_rule_jp.md`
- 来歴: `jsonl/kampobench_provenance.md`（英語）／`jsonl/kampobench_provenance_jp.md`
- HealthBench 公式 JSONL: https://github.com/openai/simple-evals から取得し、同じく `jsonl/` に置く

学習コーパスへの混入を防ぐため、データの内容を平文や画像でウェブ上に再掲しないでください
（`jsonl/kampobench_canary.md`／`_jp.md`）。

—

## 再現性

- 乱数シードはコード内で固定化（必要に応じて実装参照）
- 並列度は `--n-threads` で制御

### 温度（temperature）は任意の設定です

各サンプラーの `temperature` は**既定で `None`** であり、そのとき API に温度を**送りません**
（各社の既定値に従います）。値を固定したい場合は、`simple_evals.py` のモデルレジストリで
`temperature=0.0` のように明示してください。測定対象にも採点者にも同じ仕組みが効きます。

温度を送らない場合、同じモデル・同じ設問でも実行のたびに結果が動きます。順位の比較を行うときは
この点に留意してください。なお gpt-5 系・Claude 5 系は温度を受け付けず、指定するとエラーを
返すため送りません。

—

## サンプル出力について

評価は HTML 断片やメトリクスの要約を生成します（実装の `common`/各 Eval クラス参照）。小規模 JSONL で動作確認してから本番実行を推奨します。

—

## 開発・貢献

開発手順や PR ルールは `CONTRIBUTING_jp.md` を参照してください。

—

## 引用（Citation）

研究で利用する場合は、後日追加予定の `CITATION.cff` または本 README の引用情報をご参照ください。

—

## ライセンス

- **コード**: MIT License（© 2024 OpenAI, © 2025 Takata Hideaki）
- **データ**: CC BY 4.0（© 2025 Takata Hideaki）

詳細は `LICENSE`（コード）および `DATA_LICENSE.md`（データ）を参照してください。上流リポジトリおよび変更点の詳細は `NOTICE` を参照してください。
