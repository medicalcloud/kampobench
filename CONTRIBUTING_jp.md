**英語版は `CONTRIBUTING.md` にあります。**

# Contributing to KampoBench

KampoBench への貢献をご検討いただき、ありがとうございます。

## 現在の状況

**注意**: 現在このプロジェクトは **pilot段階** であり、限定的な関係者のみに公開されています。将来的にパブリック化した際に、外部からの貢献を歓迎する予定です。

## 開発環境のセットアップ

### 必要な環境
- Python 3.10 以上（3.12 推奨）
- OpenAI API キー

### インストール手順

1. リポジトリをクローン
```bash
git clone <repository-url>
cd sevals
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# または
venv\Scripts\activate     # Windows
```

3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 開発ワークフロー

### コードスタイル
- Python コードは [PEP 8](https://pep8.org/) に準拠
- 将来的に `black` と `ruff` の導入を予定

### テスト
```bash
# 小規模テスト実行
python -m sevals.simple_evals --eval=kampobench --model=gpt-4o-mini --examples=2

# HealthBench との互換性確認
python -m sevals.simple_evals --eval=healthbench --model=gpt-4o-mini --examples=2
```

### データの取り扱い
- JSONL ファイルの編集時は `sevals/jsonl/kampobench_jsonl_tag_rule_jp.md` のスキーマに準拠
- 個人情報（PII）や個人健康情報（PHI）を含めない
- 合成データのみを使用（現在の pilot 段階）

## 貢献ガイドライン（将来のパブリック化後）

### Issue の報告
- バグ報告、機能要望、質問は GitHub Issues を使用
- 明確なタイトルと詳細な説明を提供
- 再現手順（バグの場合）や使用例（機能要望の場合）を含める

### Pull Request
- フォークしてフィーチャーブランチを作成
- 明確なコミットメッセージを使用
- 変更内容の説明と動作確認結果を PR 説明に記載
- 既存のテストが通ることを確認

### データ貢献
- 新しい評価シナリオの提案は Issue で議論
- 漢方医学の専門知識を持つ方の監修が必要
- データの品質と一貫性を重視

## ライセンス

貢献されたコードは MIT License の下で公開されます。データ貢献は CC BY 4.0 の下で公開されます。

## 行動規範

このプロジェクトは [Contributor Covenant](https://www.contributor-covenant.org/) に準拠します。

## 質問・サポート

- 技術的な質問: GitHub Issues
- プロジェクトに関する一般的な質問: Zenodo のレコード（doi:10.5281/zenodo.23129442）に
  記載の責任著者まで

## 謝辞

すべての貢献者に感謝いたします。貢献者リストは将来的に追加予定です。
