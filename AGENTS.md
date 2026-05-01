# AGENTS.md — {{PROJECT_NAME}} AI エージェント向けインデックス

> **このファイルは北極星（North Star）です。**
> AI ツール（Claude / Copilot / Cursor）はこのファイルを起点にプロジェクトを把握します。
> **このファイルを最初に読み、ここに書かれたルールと制約に従ってください。**

> [!IMPORTANT]
> **{{PROJECT_STATUS_NOTE}}**
> 例: このプロジェクトはプロトタイプ・スペック・ファースト段階です。
> {{EDIT_PHILOSOPHY}}
> 例: 既存ファイルの破壊的変更をいとわない。より良い設計を根本から再考することを優先します。

---

## 📋 プロジェクト概要

**{{PROJECT_NAME}}** は、{{PROJECT_DESCRIPTION}}

- **スタック**: {{TECH_STACK}}
- **テストアセット**: {{TEST_ASSETS（例: `sample.glb` — 動作確認用）}}
- **対象**: {{TARGET_AUDIENCE（例: 社内ツール / セミナー参加者 / 個人利用）}}

現在の状態：
- {{CURRENT_STATE_1（例: 仕様書の段階 / 実装済み）}}
- {{CURRENT_STATE_2（例: フロントエンド骨格は実装済み）}}
- **{{NEXT_TASK（例: バックエンド API 実装が次のタスク）}}**

---

## 🔄 ADR 駆動設計

複雑なアーキテクチャ決定が必要な場合、以下のワークフローで進めます。

**ワークフロー**:
```
1. [LANE:explore]   — @Explore: コンテキスト調査（読み取り専用）
2. [LANE:plan]      — @Plan: 複数アプローチを比較・提示
3. ★ ADR 検討       — ADR.md に候補・決定・根拠を記載
4. ✓ ADR 承認       — ユーザーと確認して決定を固める
5. [LANE:implement] — @Implementer: 決定に基づき実装
6. [LANE:verify]    — @Verification: lint / build / test 実行
7. [LANE:review]    — @Reviewer: 品質・ADR 整合性チェック
```

**ADR.md の役割**: アーキテクチャ決定の候補と根拠を記録する台帳。詳細は `ADR.md` を参照。

---

## 🤖 エージェント

| エージェント | 用途 | 呼び出しタイミング |
|------------|------|----------------|
| `@Main` | 自律フルパイプライン（explore→plan→implement→verify→review） | 高レベルタスク・フィーチャー追加 |
| `@Plan` | 設計・ADR 複数案提示 → @Implementer にハンドオフ | アーキテクチャ決定が必要な際 |
| `@Explore` | 読み取り専用調査・Q&A | コード理解・質問 |
| `@Implementer` | 承認済み計画の実行（@Plan 経由のみ） | Plan 承認後 |
| `@Reviewer` | 品質・セキュリティ・ADR 監査 | 実装後 |
| `@Verification` | lint / build / test 実行 | 実装後の動作確認 |

**プロンプトショートカット** (`.github/prompts/`):
- **Plan Change** — 変更リクエストを実装計画に分解
- **Implement Change** — フルパイプラインで変更を実装
- **Verify Workspace** — 最小スコープの検証を実行

---

## 📌 次のステップ

1. **ADR.md を確認** — アーキテクチャ決定の方針が記載されています
2. **{{NEXT_STEP_2（例: 初期スキャフォルド開始 — `@Plan` に構成を相談）}}**
3. **{{NEXT_STEP_3（例: ADR.md に決定を記入）}}**
4. **実装開始** — `@Implementer` を通じて決定に基づき実装

---

## 🚫 絶対守るべき制約

- {{CONSTRAINT_1（例: `dist/` は生成物 — 直接編集禁止）}}
- {{CONSTRAINT_2（例: テストなしでの機能追加禁止）}}
- {{CONSTRAINT_3（例: 外部 API キーをコードに直書き禁止）}}

---

## 📚 参考

- エージェント定義は `.github/agents/` ディレクトリに存在
- コーディング規約は `.github/instructions/` ディレクトリに存在
- スキル（手順書）は `skills/` ディレクトリに存在
- アーキテクチャ決定は `ADR.md` に記録

---

**Last Updated**: {{DATE}}
**Version**: 2.0
