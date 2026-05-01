# Claude Code 設定

このリポジトリは **バイブコーディング用 AI 開発テンプレート** です。
新しいプロジェクトを始める際のスターターキットとして使用します。

---

## スラッシュコマンド

| コマンド | 動作 |
|--------|------|
| `/generate-agents-md` | プロジェクトを分析して `AGENTS.md` を自動生成 |
| `/generate-adr` | ADR エントリを対話式で生成 |

---

## 新規プロジェクト作成手順

### 方法 A: コピー + git 履歴リセット（推奨）

```bash
# 1. テンプレートをコピー
cp -r /c/src/ai-dev-template /c/src/my-new-project
cd /c/src/my-new-project

# 2. git 履歴を完全にリセット
rm -rf .git
git init
git add .
git commit -m "Initial commit from ai-dev-template"

# 3. AGENTS.md をプロジェクトに合わせて更新
# Claude Code を開き、/generate-agents-md を実行
```

### 方法 B: git clone + 履歴削除

```bash
git clone /c/src/ai-dev-template /c/src/my-new-project
cd /c/src/my-new-project
rm -rf .git
git init
git add .
git commit -m "Initial commit"
```

### 方法 C: GitHub テンプレートリポジトリ（GitHub 使用時）

1. GitHub にこのリポジトリをプッシュ
2. リポジトリ設定 → "Template repository" にチェック
3. 新プロジェクト作成時に "Use this template" を選択
   - git 履歴は自動的にリセットされる

---

## 新プロジェクト開始後のチェックリスト

```
[ ] rm -rf .git && git init（履歴をリセット）
[ ] /generate-agents-md を実行して AGENTS.md を更新
[ ] AGENTS.md の {{PLACEHOLDERS}} をすべて埋める
[ ] ADR.md の内容をプロジェクトに合わせてリセット
[ ] .github/copilot-instructions.md の {{PLACEHOLDERS}} を埋める
[ ] .github/agents/main.agent.md のブラスト半径ゲートをプロジェクトに合わせて更新
[ ] .github/instructions/ のコーディング規約をプロジェクトに合わせて更新
[ ] skills/ にプロジェクト固有のドメイン知識を追加
[ ] GitHub リモートを設定: git remote add origin <URL>
```

---

## このテンプレートのディレクトリ構造

```
ai-dev-template/
├── .claude/
│   └── commands/
│       ├── generate-agents-md.md   # /generate-agents-md コマンド
│       └── generate-adr.md         # /generate-adr コマンド
├── .github/
│   ├── agents/
│   │   ├── main.agent.md           # @Main 自律オーケストレーター（フルパイプライン）
│   │   ├── explore.agent.md        # @Explore 読み取り専用調査
│   │   ├── plan.agent.md           # @Plan 設計・計画
│   │   ├── implementer.agent.md    # @Implementer 実装（Plan 経由のみ）
│   │   ├── verification.agent.md   # @Verification lint/build/test
│   │   └── reviewer.agent.md       # @Reviewer 品質・セキュリティ監査
│   ├── instructions/
│   │   ├── src-coding.instructions.md  # コーディング規約テンプレート
│   │   └── testing.instructions.md     # テスト規約テンプレート
│   ├── prompts/
│   │   ├── plan-change.prompt.md        # 変更計画プロンプト
│   │   ├── implement-change.prompt.md   # 変更実装プロンプト
│   │   └── verify-workspace.prompt.md   # 検証プロンプト
│   └── copilot-instructions.md          # GitHub Copilot グローバル指示
├── skills/
│   ├── generate-agents-md/
│   │   └── SKILL.md                # AGENTS.md 生成手順書
│   └── generate-adr/
│       └── SKILL.md                # ADR 生成手順書
├── AGENTS.md                       # ← 新プロジェクト向けテンプレート
├── AGENTS_PROMPT.md                # ← AI に貼り付けて AGENTS.md を生成するプロンプト
├── ADR.md                          # ← ADR テンプレート
└── Claude.md                       # ← このファイル（Claude Code 設定）
```
