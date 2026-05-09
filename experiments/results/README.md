# Results

各実験 run は `experiments/results/runs/<run_name>/` に保存します。

推奨構成:

- `hyp/`: 仮説文字起こし (`audio_id.txt`)
- `metrics.csv`: 1 音声ごとの指標
- `summary.json`: run 全体の要約

`run_comparison.csv` は複数 run の summary を横並び比較するための集約ファイルです。
