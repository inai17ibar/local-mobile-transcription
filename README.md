# ai-dev-template 使い方ガイド

AI ツール（Claude Code / GitHub Copilot / Cursor）と協調して開発するためのプロジェクトテンプレートです。
このガイドを読めば、テンプレートの全機能を使いこなせます。

---

## 目次

1. [新プロジェクトの始め方](#1-新プロジェクトの始め方)
2. [初期セットアップ（最初の一回だけ）](#2-初期セットアップ最初の一回だけ)
3. [日常の使い方](#3-日常の使い方)
4. [Claude Code と GitHub Copilot の使い分け](#4-claude-code-と-github-copilot-の使い分け)
5. [エージェント早見表](#5-エージェント早見表)
6. [コマンド・ショートカット一覧](#6-コマンドショートカット一覧)
7. [よくある使い方パターン](#7-よくある使い方パターン)
7. [ファイル一覧と役割](#7-ファイル一覧と役割)

---

## 1. 新プロジェクトの始め方

### Step 1: テンプレートをコピーする

```bash
cp -r /c/src/ai-dev-template /c/src/my-new-project
cd /c/src/my-new-project
rm -rf .git
git init
git add .
git commit -m "Initial commit from ai-dev-template"
```

### Step 2: AGENTS.md を自動生成する

Claude Code を開き、以下を実行します：

```
/generate-agents-md
```

Claude がプロジェクトを自動分析して `AGENTS.md` を生成します。
残った `{{PLACEHOLDER}}` は手動で埋めてください。

### Step 3: 残りのプレースホルダーを埋める

以下のファイルの `{{...}}` をすべてプロジェクトに合わせて書き換えます：

| ファイル | 主な変更箇所 |
|--------|------------|
| `AGENTS.md` | プロジェクト名・スタック・制約・次のタスク |
| `.github/copilot-instructions.md` | プロジェクト名・制約・ソース構成・検証コマンド |
| `.github/instructions/src-coding.instructions.md` | 命名規則・フォーマット・アーキテクチャパターン |
| `.github/instructions/testing.instructions.md` | テストコマンド・フレームワーク・カバレッジ目標 |
| `.github/agents/verification.agent.md` | lint/build/test の実際のコマンド |
| `.github/agents/implementer.agent.md` | 検証コマンド（self-correction ループ内） |
| `ADR.md` | ADR-001 の日付・決定者を実際の値に変更 |

### Step 4: 最初の ADR を記録する

重要な技術選定（フレームワーク・DB・言語など）を行ったら `/generate-adr` で記録します。
詳細は [ADR の使い方](#パターン3-アーキテクチャ決定を記録する) を参照。

---

## 2. 初期セットアップ（最初の一回だけ）

### ブラスト半径ゲートを設定する

`.github/agents/main.agent.md` の **Phase 2 — Plan** にある blast-radius gate を
プロジェクトの制約に合わせて書き換えます。

例（デフォルト）:
```
- Check AGENTS.md constraints — 違反があれば abort
- Plan touches > 10 files → pause and confirm
- Plan includes file deletion → pause and confirm
```

プロジェクト固有の追加例:
```
- dist/ を触るプランは即 abort
- DB マイグレーションを含むプランは必ず確認
- 認証系ファイルへの変更は必ず確認
```

### ドメインスキルを追加する（あれば）

`skills/` にプロジェクト固有の知識ファイルを追加すると、AI がより正確な提案をできるようになります。

```
skills/
└── {ドメイン名}/
    └── SKILL.md   # 仕様・アルゴリズム・API 詳細などを記述
```

例: gaussian-splat プロジェクトでは `skills/3dgs-rendering/SKILL.md` に
300 行のレンダリング仕様書を置き、AI がシェーダーの実装を正確に行えるようにしています。

---

## 3. 日常の使い方

### 何かを実装したいとき

**シンプルな変更**: そのまま Claude に頼む（@Main や @Plan は不要）

**複雑な変更**: 以下のどちらかを使う

```
# 方法A: フルオートで実装してもらう
@Main {やりたいこと}

# 方法B: まず計画を見てから実装する
@Plan {設計したいこと}
→ 計画を確認して承認
→ ハンドオフボタンで @Implementer に引き渡す
```

### コードについて質問したいとき

```
@Explore {知りたいこと}
例: @Explore ユーザー認証の処理はどのファイルで行っていますか？
```

`@Explore` は読み取り専用なのでファイルを変更しません。安心して何でも聞けます。

### テスト・ビルドを確認したいとき

```
@Verification {確認したい範囲}
例: @Verification src/api/ の変更が既存テストを壊していないか確認してください
```

### コードレビューしたいとき

```
@Reviewer {レビュー対象}
例: @Reviewer src/auth/ のセキュリティレビューをしてください
```

---

## 4. Claude Code と GitHub Copilot の使い分け

このテンプレートは **Claude Code と GitHub Copilot の両方を役割分担して使う**設計です。
どちらか片方だけでも使えますが、両方使うと最も効果を発揮します。

### 担当する機能の範囲

```
このテンプレート
│
├── Claude Code が使う部分
│   ├── .claude/commands/     ← /generate-agents-md, /generate-adr
│   ├── AGENTS.md             ← 会話の文脈として読み込まれる
│   └── ADR.md                ← 同上
│
└── GitHub Copilot が使う部分
    ├── .github/agents/       ← @Plan @Main など VS Code で実際に呼び出せる
    ├── .github/instructions/ ← src/** 編集中に自動適用されるコーディング規約
    ├── .github/prompts/      ← ワンクリックで実行できるプロンプト
    └── .github/copilot-instructions.md  ← Copilot が毎回読むグローバル設定
```

### 何が違うか

| 操作 | Claude Code | GitHub Copilot |
|---|---|---|
| `@Plan` と書く | Claude が「Planエージェントとして振る舞う」（文脈参照） | VS Code で `plan.agent.md` が**実際にロードされて動く** |
| `/generate-agents-md` | ✅ 動く | ❌ 使えない |
| `.github/instructions/` | 手動で参照しないと読まれない | src/ ファイル編集中に**自動で適用**される |
| `AGENTS.md` | ✅ 毎回の文脈として読む | ✅ 同様に読む |

### 実用的な使い分け

**Claude Code（設計・分析フェーズ向き）**
- `/generate-agents-md` でプロジェクトを分析して AGENTS.md を生成
- `/generate-adr` でアーキテクチャ決定を記録
- 「この設計どう思う？」などの複雑な対話・相談

**GitHub Copilot（実装フェーズ向き）**
- VS Code の Copilot Chat で `@Main` `@Plan` などを呼び出す
- ファイルを編集するたびに `instructions/` が自動適用されコード品質が保たれる
- プロンプトショートカットで繰り返し作業を自動化

---

## 5. エージェント早見表

| エージェント | できること | できないこと | 典型的な使いどころ |
|------------|-----------|------------|-----------------|
| `@Main` | 探索→計画→実装→検証→レビューを自律実行 | — | 「〜機能を追加して」という高レベル指示 |
| `@Plan` | 実装計画の作成・比較・推奨 | コード編集 | 大きな変更の前に計画を立てる |
| `@Explore` | コード読み取り・説明・質問回答 | コード編集・実行 | 「〜はどこで処理してる？」という質問 |
| `@Implementer` | 承認済み計画の実装 | 計画の変更・スコープ外の変更 | @Plan のハンドオフ後に自動起動 |
| `@Verification` | lint / build / test の実行 | ソースコードの編集 | 変更後の動作確認 |
| `@Reviewer` | 品質・セキュリティ・ADR 整合性チェック | 新機能の実装 | 実装完了後のレビュー |

### レーンシグナルの読み方

エージェントが処理中に以下のシグナルを出力します：

```
▶ [LANE:explore]            → 探索フェーズ開始
✓ [LANE:explore:complete]   → 探索フェーズ完了
✗ [LANE:plan:blocked]       → 計画フェーズでブロック（制約違反など）
```

`✗` が出たら何かブロックされています。理由を読んで対処してください。

---

## 6. コマンド・ショートカット一覧

### Claude Code スラッシュコマンド

| コマンド | 何をする | いつ使う |
|--------|---------|---------|
| `/generate-agents-md` | プロジェクトを分析して AGENTS.md を生成・更新 | プロジェクト開始時、構成が大きく変わったとき |
| `/generate-adr` | ADR エントリを対話式で ADR.md に追記 | 技術的な決定をしたとき |

### GitHub Copilot プロンプトショートカット（`.github/prompts/`）

VS Code で Copilot を使っている場合、以下のプロンプトがワンクリックで使えます：

| ショートカット | 何をする | いつ使う |
|-------------|---------|---------|
| **Plan Change** | 変更リクエストを実装計画に分解 | 実装前に計画を確認したいとき |
| **Implement Change** | @Main を使ってフルパイプライン実装 | 高レベルの変更依頼 |
| **Verify Workspace** | 最小スコープの検証を実行 | 変更後の動作確認 |

---

## 7. よくある使い方パターン

### パターン1: 新機能を追加する

```
1. @Explore で既存コードを把握
   → 「@Explore {新機能}に関係するモジュールを教えてください」

2. @Plan で実装計画を立てる
   → 「@Plan {機能名}の実装計画を立ててください」
   → 計画を確認・承認

3. ハンドオフボタンで @Implementer に引き渡す
   → 自動的に @Reviewer にもハンドオフされる

4. @Reviewer の指摘を確認して完了
```

または、すべて自動でやってもらいたい場合：

```
@Main {機能名}を追加してください。{要件の詳細}
```

---

### パターン2: バグを修正する

```
1. 症状を伝えて @Explore で原因を調査
   → 「@Explore {エラーメッセージ}の原因を探してください」

2. 原因が特定できたら直接修正を依頼
   → または @Plan でリスクを確認してから修正

3. @Verification で回帰テストを実行
   → 「@Verification 変更後のテストを実行してください」
```

---

### パターン3: アーキテクチャ決定を記録する

```
1. /generate-adr を実行
2. Claude に質問に答える:
   - どんな決定について記録しますか？
   - 検討した選択肢は？
   - 最終的にどれを選びましたか？
   - その理由は？
3. ADR が ADR.md に追記される
4. 制約に関わる決定は AGENTS.md の「🚫 絶対守るべき制約」にも反映される
```

**ADR を書くべきタイミング**:
- ✅ フレームワーク・DB・言語の選定
- ✅ アーキテクチャの分割方針（モノリス vs マイクロサービスなど）
- ✅ パフォーマンスとシンプルさのトレードオフ
- ✅ セキュリティ上の重要な制約
- ❌ 変数名・関数の内部ロジック（ADR 不要）
- ❌ バグ修正（ADR 不要）

---

### パターン4: プロジェクトの状況を AI に把握させる

```
# プロジェクトの構成が変わったとき
/generate-agents-md

# 「今どんな状態？」と聞きたいとき
@Explore AGENTS.md と最近の変更から現在の実装状況を教えてください
```

---

### パターン5: ドメイン知識をスキルとして追加する

AI に繰り返し同じ背景知識を説明している場合、`skills/` に書いておくと毎回説明しなくて済みます。

```
# ファイルを作成
skills/{ドメイン名}/SKILL.md

# AGENTS.md の参考セクションにリンクを追記
## 📚 参考
- ドメイン知識は `skills/{ドメイン名}/SKILL.md` を参照
```

書く内容の例:
- API の仕様・エンドポイント一覧
- 独自のアルゴリズムや計算式
- 外部サービスとの連携方法
- ドメイン用語の定義

---

## 8. ファイル一覧と役割

```
ai-dev-template/
│
├── AGENTS.md                    ★ AI の北極星。最初に読まれる。プロジェクト概要・制約・次のタスクを記載
├── ADR.md                       ★ アーキテクチャ決定の台帳。重要な技術選定を記録
├── Claude.md                      Claude Code の設定ファイル。スラッシュコマンドの定義場所
│
├── .claude/commands/
│   ├── generate-agents-md.md    /generate-agents-md の実装
│   └── generate-adr.md          /generate-adr の実装
│
├── .github/
│   ├── copilot-instructions.md  GitHub Copilot へのグローバル指示（制約・構成を記載）
│   │
│   ├── agents/                  ★ エージェント定義（Claude & Copilot 両対応）
│   │   ├── main.agent.md        @Main: 自律フルパイプライン
│   │   ├── explore.agent.md     @Explore: 読み取り専用調査
│   │   ├── plan.agent.md        @Plan: 計画策定
│   │   ├── implementer.agent.md @Implementer: 実装（Plan 経由）
│   │   ├── verification.agent.md @Verification: lint/build/test
│   │   └── reviewer.agent.md    @Reviewer: 品質・セキュリティ監査
│   │
│   ├── instructions/            ★ コーディング規約（IDE が自動読み込み）
│   │   ├── src-coding.instructions.md  src/** に適用されるスタイルガイド
│   │   └── testing.instructions.md     tests/** に適用されるテスト規約
│   │
│   └── prompts/                 プロンプトショートカット（Copilot でワンクリック実行）
│       ├── plan-change.prompt.md
│       ├── implement-change.prompt.md
│       └── verify-workspace.prompt.md
│
└── skills/                      ★ ドメイン固有の知識ファイル（プロジェクトごとに追加）
    ├── generate-agents-md/SKILL.md  /generate-agents-md の手順書
    └── generate-adr/SKILL.md        /generate-adr の手順書
```

### ★ マークのファイルは特に重要

| ファイル | 誰が読む | いつ更新する |
|--------|---------|-----------|
| `AGENTS.md` | すべての AI ツール（毎回） | 構成変更・制約追加のたびに |
| `ADR.md` | AI ツール・人間 | 技術的決定のたびに（`/generate-adr`） |
| `.github/agents/` | Claude / Copilot | セットアップ時・エージェント動作を変えたいとき |
| `.github/instructions/` | IDE（自動） | コーディング規約を変えたいとき |
| `skills/` | AI ツール（明示的に参照時） | ドメイン知識を追加したいとき |

---

## よくある質問

**Q: `@Main` と直接 Claude に頼む違いは？**
A: `@Main` は必ず explore → plan → implement → verify → review の順に進み、各フェーズでブラスト半径チェックを行います。重要な変更には `@Main` を使うと安全です。小さな変更は直接頼んでも構いません。

**Q: `@Implementer` を直接呼ぶことはできる？**
A: できますが推奨しません。`@Implementer` は「承認済みの計画を実行する」役割なので、計画なしに呼ぶとスコープが曖昧になります。`@Plan` → ハンドオフ という流れが基本です。

**Q: スキルはいつ追加するべき？**
A: AI に同じ背景説明を 2〜3 回以上している場合がサイン。その知識を `skills/{topic}/SKILL.md` に書いて `AGENTS.md` に参照先を追記すると、以降は説明不要になります。

**Q: ADR は毎回書く必要がある？**
A: 「なぜこうしたのか」を 6 ヶ月後に説明できるかどうかが判断基準です。技術スタックの選定や大きなアーキテクチャ判断は記録し、バグ修正や細かい実装詳細は不要です。
