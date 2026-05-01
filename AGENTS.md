# AGENTS.md — local-mobile-transcription AI エージェント向けインデックス

> **このファイルは北極星（North Star）です。**
> AI ツール（Claude / Copilot / Cursor）はこのファイルを起点にプロジェクトを把握します。
> **このファイルを最初に読み、ここに書かれたルールと制約に従ってください。**

> [!IMPORTANT]
> **このプロジェクトは初期セットアップ段階です（スタックは ADR-002 で確定済み、実装は未着手）。**
> 既存ファイル（AGENTS.md / ADR.md など）の破壊的変更をいとわない。
> 仕様が固まるまでは ADR ドリブンで進め、決定前に実装に着手しない。

---

## 📋 プロジェクト概要

**local-mobile-transcription** は、iPhone(15 Pro 以降)上でローカル動作する音声文字起こしアプリ。会議の議事録を端末内で完結して残すことを目的とする。

- **スタック**: Swift / SwiftUI(iOS 17+) + WhisperKit(Whisper large-v3-turbo) + AVFoundation。詳細は ADR-002 を参照
- **テストアセット**: 未配置（日本語会議の短尺サンプル音声を `tests/fixtures/` などに用意予定）
- **対象**: 議事録を残したい個人・チーム（クラウドに音声を出せない要件のあるユース）

現在の状態：
- ai-dev-template ベースのリポジトリスケルトンのみ存在（`.claude/commands/`, `.github/agents/`, `.github/instructions/`, `.github/prompts/`, `skills/`）
- スタック選定は ADR-002 で承認済み
- Xcode プロジェクト・Swift ソース・テストは未着手
- **次のタスク: Xcode プロジェクト初期化（iOS 17+, SwiftUI, SwiftPM で WhisperKit 導入）← ここから始める**

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

1. **Xcode プロジェクト初期化**（iOS 17+ ターゲット、SwiftUI、Swift Package Manager で WhisperKit 導入）
2. **モデル DL オンボーディング UX 実装**（ADR-003 — Wi-Fi 接続中に約 1.5GB を初回 DL、失敗時リトライ）
3. **MVP 実装** — 録音(AVFoundation) → セグメント分割(30 秒〜1 分) → 逐次転写(WhisperKit) → テキスト保存
4. **検証** — `@Verification` で実機(iPhone 15 Pro) 動作確認、1 時間音声でのメモリ・処理時間計測
5. **将来 ADR 候補** — 話者識別アプローチ（VAD 簡易版 / sherpa-onnx 本格版）

---

## 🚫 絶対守るべき制約

- **クロスプラットフォーム化禁止**: コア実装は Swift ネイティブ(ADR-002)。React Native / Flutter 等への切り替えは ADR 必須
- **クラウド ASR 禁止**: 文字起こしは WhisperKit + AVFoundation のローカル処理に限定。OpenAI Whisper API / Google Speech-to-Text 等への切り替えは ADR 必須
- **音声データの外部送信禁止**: 録音データ・文字起こし結果を外部サービス（解析・ログ・クラッシュレポートを含む）に送信する変更は ADR 必須
- **メモリ前提**: 1 時間音声を一括処理しない。30 秒〜1 分のセグメント単位で逐次転写すること（iPhone 15 Pro 8GB RAM 制約）
- **モデル同梱禁止**: Whisper モデルは WhisperKit Hub から初回 DL する方式（ADR-003）。アプリへの同梱・別経路 DL に切り替える変更は ADR 必須
- スタック・アーキテクチャに関わる変更は ADR を経ること（仕様先行）

---

## 📚 参考

- エージェント定義は `.github/agents/` ディレクトリに存在
- コーディング規約は `.github/instructions/` ディレクトリに存在
- スキル（手順書）は `skills/` ディレクトリに存在
- アーキテクチャ決定は `ADR.md` に記録

---

**Last Updated**: 2026-05-01
**Version**: 2.0
