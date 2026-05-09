# Experiments

MBP 上で文字起こし精度の改善要因を切り分けるための実験基盤です。ここでは「何が効くか」を先に決め、iPhone 側には採用した構成だけを戻します。

## 方針

- ベースラインは現行 iOS 実装に合わせます。
- 前処理・推論条件・後処理は 1 要素ずつ変えます。
- 音声・参照テキスト・結果はローカル保持前提で、Git には基本的に含めません。

## ディレクトリ

- `experiments/data/audio/`: 評価用音声
- `experiments/data/ref/`: 正解文字起こし (`.txt`)
- `experiments/data/dataset.csv`: 評価対象のマニフェスト
- `experiments/configs/`: 実験条件の固定 JSON
- `experiments/scripts/preprocess/`: ffmpeg ベースの前処理スクリプト
- `experiments/scripts/eval/`: CER/WER などの評価スクリプト
- `experiments/whisperkit-batch-runner/`: MBP 上で WhisperKit ベースラインを一括実行する Swift package
- `experiments/results/runs/`: 実験ごとの出力

## ベースライン

現行アプリの設定は [ContentView.swift](/Users/soichiro.inatani/src/local-mobile-transcription/LocalMobileTranscription/LocalMobileTranscription/ContentView.swift:217) に合わせています。

- `language = "ja"`
- `chunkingStrategy = .vad`
- モデルは `WhisperKit.recommendedModels().default`
- 前処理なし
- 後処理なし

定義ファイルは `experiments/configs/baseline.whisperkit.json` です。
比較用の叩き台は `experiments/configs/preprocess.matrix.json`、`experiments/configs/inference.matrix.json`、`experiments/configs/postprocess.matrix.json` に置いてあります。

## 初回セットアップ

1. 長尺の `sample.m4a` を分割して、評価候補を作る。
2. `experiments/data/dataset.csv` に採用したセグメントを残す。
3. `experiments/data/ref/` に同じ `audio_id` の `.txt` を置く。
4. ベースライン推論結果を `experiments/results/runs/<run_name>/hyp/` に保存する。
5. 評価スクリプトで数値化する。

## コマンド例

`sample.m4a` から 24 本の評価セットを均等サンプリングで作る:

```sh
python3 experiments/scripts/preprocess/seed_dataset.py \
  --input sample.m4a \
  --output-dir experiments/data/audio/sample_eval \
  --dataset experiments/data/dataset.csv \
  --count 24 \
  --segment-seconds 30 \
  --overwrite
```

`sample.m4a` を 30 秒ごとに分割して、候補マニフェストを作る:

```sh
python3 experiments/scripts/preprocess/split_audio.py \
  --input sample.m4a \
  --output-dir experiments/data/audio/sample_seed \
  --manifest experiments/data/dataset.sample.csv \
  --segment-seconds 30
```

ベースライン実験を評価する:

```sh
python3 experiments/scripts/eval/evaluate.py \
  --dataset experiments/data/dataset.csv \
  --hyp-dir experiments/results/runs/baseline_whisperkit_ios_current/hyp \
  --run-name baseline_whisperkit_ios_current
```

`hyp` を `ref` の下書きに流し込み、アノテーションキューを作る:

```sh
python3 experiments/scripts/eval/prepare_ref_drafts.py \
  --dataset experiments/data/dataset.csv \
  --hyp-dir experiments/results/runs/baseline_whisperkit_ios_current/hyp \
  --skip-existing
```

最初は `--limit 8` などで 8〜10 本に絞って始めるのが現実的です。

`hyp` と `ref` を並べた Markdown ビューを作る:

```sh
python3 experiments/scripts/eval/build_annotation_view.py \
  --dataset experiments/data/dataset.csv \
  --hyp-dir experiments/results/runs/baseline_whisperkit_ios_current/hyp \
  --output experiments/data/annotation_view.md \
  --limit 8
```

MBP 上で WhisperKit ベースラインを一括実行する:

```sh
arch -arm64 swift run \
  --package-path experiments/whisperkit-batch-runner \
  WhisperKitBatchRunner \
  --config experiments/configs/baseline.whisperkit.json
```

`Platform: x86_64` や Rosetta 実行になっている場合は、`WhisperKit` が不安定になることがあります。Apple Silicon では必ず `arm64` で起動してください。

複数 run の summary を 1 つの CSV にまとめる:

```sh
python3 experiments/scripts/eval/compare_runs.py \
  --results-dir experiments/results/runs \
  --output experiments/results/run_comparison.csv
```

## `dataset.csv` の列

- `audio_id`: 参照キー
- `audio_path`: 音声ファイルへの相対パス
- `ref_path`: 正解テキストへの相対パス
- `notes`: 収録条件メモ
- `tags`: `short|noise|multi_speaker|proper_noun` のように `|` 区切り
- `proper_nouns`: 評価したい固有名詞を `|` 区切り
- `start_sec`, `end_sec`, `duration_sec`: 元音声内の位置
- `source_audio`: 切り出し元ファイル

## 評価指標

- `CER`
- `WER`
- `CER(no punctuation)`
- `proper noun misses`

`WER` は日本語向けの軽量ヒューリスティック分かち書きです。比較用途には使えますが、絶対値を厳密に扱うなら SudachiPy / MeCab への差し替えを検討してください。

## 推奨ワークフロー

1. `prepare_ref_drafts.py` で `hyp` を `ref` の下書きにコピーする
2. `annotation_queue.csv` を上から見て、まず 8〜10 本だけ手修正する
3. `dataset.csv` の `tags` と `proper_nouns` をその 8〜10 本だけ埋める
4. `evaluate.py` で最初のベースライン値を出す
5. 前処理や分割の比較で効くものだけを増やす
