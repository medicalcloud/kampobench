# 漢方専門医向けデータレビュー手順 (Markdown ワークフロー)

このドキュメントでは、エンジニアではない医療従事者（漢方専門医など）が、KampoBench の評価用データをテキストエディタを用いて容易に確認・修正するための手順を解説します。
文章ベースの編集に適した、シンプルでミスの少ない推奨ワークフローです。

---

## 全体フロー
1. **JSONL データ**（元の評価データ）を **Markdown** に変換して取り出す
2. 取り出した Markdown を **テキストエディタで開き、レビュー・修正** を行う
3. 修正済みの Markdown を、再び **JSONL データ** に変換して戻す
4. バリデーションスクリプトで**エラーがないか最終チェック**を行う

---

## 1. JSONL から Markdown の作成

以下のコマンドを実行します。

```bash
python3 sevals/jsonl/format_for_md_review.py jsonl2md sevals/jsonl/kampobench_pilot_samples_reviewed.jsonl sevals/jsonl/kampobench_pilot_samples.md
```
※ `kampobench_pilot_samples.md` は新しく作る Markdown のファイル名です。

---

## 2. Markdownでのレビュー作業

`kampobench_pilot_samples.md` をテキストエディタ（VS Code, メモ帳等）で開き、内容を編集します。
- `#### [ideal_completion]` などのセクションを直接書き換えることができます。
- 各行の構造やヘッダーを壊さないように注意してください。

---

## 3. Markdown から JSONL への復元

編集・保存した Markdown を元の JSONL 形式に戻します。

```bash
python3 sevals/jsonl/format_for_md_review.py md2jsonl sevals/jsonl/kampobench_pilot_samples.md sevals/jsonl/updated_samples.jsonl
```

---

## 4. [重要] 最終バリデーション（エラーチェック）

ファイルを本番で使用する前に、**必ず**チェックツールを実行してください。

```bash
python3 sevals/jsonl/validate_kampobench.py sevals/jsonl/updated_samples.jsonl
```

`[OK] Validation PASSED.` と表示されれば完成です！
 エラー（`[ERROR]`）が出た場合は、表示される指示に従って修正してください。
