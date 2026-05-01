このプロジェクトを分析して `AGENTS.md` を生成してください。

## 実行手順

### Step 1: プロジェクト構造を把握する

以下を実行してファイル構造を確認してください:
```bash
find . -maxdepth 4 \
  -not -path './.git/*' \
  -not -path './node_modules/*' \
  -not -path './.venv/*' \
  -not -path './target/*' \
  -not -path './dist/*' \
  -not -path './.next/*' \
  -type f | sort
```

### Step 2: マニフェストファイルを読む

存在する場合は以下を読んでください（存在しないものはスキップ）:
- `package.json`
- `pyproject.toml` / `requirements.txt`
- `Cargo.toml`
- `go.mod`
- `README.md`
- 既存の `AGENTS.md`（内容があれば上書き前に確認）

### Step 3: 以下を特定する

- **プロジェクト名**: リポジトリ名 or package.json の name
- **説明**: README か package.json の description
- **テックスタック**: 言語・フレームワーク・主要ライブラリ
- **テストアセット**: `public/`, `assets/`, `tests/fixtures/` などのサンプルデータ
- **現在の状態**: 何が実装済みで何が未実装か
- **次のタスク**: 最も優先度の高い未実装機能

### Step 4: AGENTS.md を生成する

以下の構造で `AGENTS.md` を生成してください（プレースホルダーは実際の値で埋めること）:

```markdown
# AGENTS.md — {プロジェクト名} AI エージェント向けインデックス

> **このファイルは北極星（North Star）です。**
> AI ツール（Claude / Copilot / Cursor）はこのファイルを起点にプロジェクトを把握します。

> [!IMPORTANT]
> **{プロジェクトの現在フェーズ: 例「このプロジェクトはプロトタイプ段階です」}**
> {編集方針}

---

## 📋 プロジェクト概要

**{プロジェクト名}** は、{一文の説明}

- **スタック**: {技術スタック}
- **テストアセット**: {テスト用ファイル（あれば）}
- **対象**: {誰のためのプロジェクトか}

現在の状態：
- {実装済みの項目を列挙}
- **{次のタスク ← ここから始める}**

---

## 🔄 ADR 駆動設計

複雑なアーキテクチャ決定が必要な場合、以下のワークフローで進めます。

**ワークフロー**:
\`\`\`
1. [LANE:explore]   — @Explore: コンテキスト調査
2. [LANE:plan]      — @Plan: 複数アプローチを比較・提示
3. ★ ADR 検討       — ADR.md に候補・決定・根拠を記載
4. ✓ ADR 承認       — ユーザーと確認して決定
5. [LANE:implement] — @Implementer: 決定に基づき実装
6. [LANE:verify]    — @Verification: 動作確認
7. [LANE:review]    — @Reviewer: ADR 整合性チェック
\`\`\`

---

## 🤖 エージェント

| エージェント | 用途 | 呼び出し |
|------------|------|--------|
| `@Main` | 自律フルパイプライン（explore→plan→implement→verify→review） | 高レベルタスク |
| `@Plan` | 設計・ADR 複数案提示 → @Implementer にハンドオフ | アーキテクチャ決定が必要な際 |
| `@Explore` | 読み取り専用調査・Q&A | コード質問 |
| `@Implementer` | 承認済み計画の実行（@Plan 経由のみ） | Plan 承認後 |
| `@Reviewer` | 品質・セキュリティ・ADR 監査 | 実装後 |
| `@Verification` | lint / build / test 実行 | 実装後 |

**プロンプトショートカット** (`.github/prompts/`):
- **Plan Change** — 変更リクエストを実装計画に分解
- **Implement Change** — フルパイプラインで変更を実装
- **Verify Workspace** — 最小スコープの検証を実行

---

## 📌 次のステップ

1. **ADR.md を確認** — アーキテクチャ決定の方針が記載されています
2. {プロジェクト固有のステップ}
3. **実装開始** — `@Implementer` を通じて決定に基づき実装

---

## 🚫 絶対守るべき制約

- {コードから読み取ったプロジェクト固有の制約}

---

## 📚 参考

- エージェント定義は `.github/agents/` ディレクトリに存在
- コーディング規約は `.github/instructions/` ディレクトリに存在
- スキルは `skills/` ディレクトリに存在

---

**Last Updated**: {今日の日付}
**Version**: 1.0
```

### 注意事項
- 既存の `AGENTS.md` に実質的な内容（10行以上）がある場合は上書き前に確認を取ること
- プレースホルダー `{...}` はすべて実際の値に置き換えること
- 「現在の状態」と「次のステップ」はコードから読み取った事実を書くこと（推測不可）
