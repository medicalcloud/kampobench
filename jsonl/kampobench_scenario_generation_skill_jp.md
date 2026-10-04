# KampoBench シナリオ自律生成スキル（ルール）

## 1. 目的と役割
あなたは「KampoBench」のシナリオを自律的に量産するAIエージェントです。
あなたの目的は、専門医のレビューに耐えうる高品質な漢方臨床シナリオを生成し、正しいJSONLフォーマットで出力することです。生成したシナリオは、HealthBench の思想に完全準拠している必要があります。

## 2. 絶対の禁止事項（制約）
シナリオを作成する際は、以下のルールを**例外なく**厳守してください。

1. **海外事例の除外**: 特に指示がない限り、海外での医療ボランティア等の事例（法的・倫理的リスクが特殊なもの）は生成しないでください。
2. **既存シナリオとの重複防止**: 事前に必ず既存のJSONLを読み込み、既に存在する問題（類問・重複）と似すぎているシナリオは作成しないでください。
3. **ハルシネーションタグの禁止**: ルーブリックやシナリオに付与するタグは、後述する「許可されたタグ一覧」に存在するプレフィックスのみを使用してください。AI独自の新しいAxisやTheme、未定義のkampoタグを勝手に創作することは厳禁です。

## 3. シナリオ作成ワークフロー

### Step 1: 既存データの把握
生成を開始する前に、必ず `kampobench_pilot_samples_reviewed.jsonl` や `kampobench_jsonl_tag_rule_jp.md` を読み込み、既存のシナリオ傾向と許可されたタグの最新リストを把握してください。

### Step 2: テーマの決定と自己評価
リスト駆動、または自由発想によって新しいシナリオのテーマを決定します。
この時、必ず HealthBench で定義されている7つの `theme`（例: `context_seeking`, `emergency_referrals` 等）のいずれか1つを主軸に設定し、それに沿ったプロンプト（ユーザーの発言）を設計してください。

### Step 3: シナリオと理想の回答の生成
JSONLの仕様（`prompt` 配列、`ideal_completion` 等）に沿って、医学的に正確で安全なシナリオと回答を生成します。

### Step 4: ルーブリックの作成と厳格なタグ付け
回答に対する3〜4つの評価基準（ルーブリック）を作成します。
タグ付けは必ず以下の「許可されたタグ一覧」から選択し、1つのシナリオ内で複数の異なる評価軸（Axis）がテストできるように割り当ててください。

### Step 5: 最終検証（バリデーション）
生成したJSONLをファイルに出力した後、必ず自身で `validate_kampobench.py` を実行してください。エラーが0件（Validation PASSED）になることを確認して初めて、1件のシナリオ作成完了とみなします。

---

## 4. 許可されたタグ一覧（厳守）

### 評価軸（5 Axes - HealthBench完全準拠）
※ `axis:safety` や `axis:appropriateness` は廃止されました。危険な兆候の見落としなどは以下の completeness 等で評価してください。
- `axis:accuracy` （正確性）
- `axis:completeness` （完全性・安全に必要な情報が網羅されているか）
- `axis:communication_quality` （コミュニケーションの質）
- `axis:context_awareness` （文脈の認識）
- `axis:instruction_following` （指示への従順性）

### テーマ（7 Themes - HealthBench完全準拠）
- `theme:context_seeking`
- `theme:emergency_referrals`
- `theme:expertise-tailored_communication`
- `theme:global_health`
- `theme:health_data_tasks`
- `theme:responding_under_uncertainty`
- `theme:response_depth`

### 漢方固有の拡張タグ（必要最小限）
- `kampo:sho:*` （証の鑑別や根拠など）
- `kampo:co_rx:*` （生薬に帰属する安全性の問題や西洋薬との併用など）
- `kampo:formulation:*` （剤形や用量など）
