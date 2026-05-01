//
//  ContentView.swift
//  LocalMobileTranscription
//
//  Created by soichiro inatani on 2026/05/01.
//

import SwiftUI
import Observation
import Combine
import AVFoundation
import UniformTypeIdentifiers
import WhisperKit

struct ContentView: View {
    @State private var whisper = WhisperHolder()
    @State private var showFileImporter = false

    var body: some View {
        VStack(spacing: 16) {
            Text("ローカル文字起こし")
                .font(.title2.bold())
                .padding(.top)

            statusBar

            transcriptArea

            actionButton
        }
        .padding()
        .task {
            await whisper.loadModel()
        }
        .fileImporter(
            isPresented: $showFileImporter,
            allowedContentTypes: [.audio],
            allowsMultipleSelection: false
        ) { result in
            handleFileImport(result)
        }
    }

    private var statusBar: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                if whisper.isBusy {
                    ProgressView().scaleEffect(0.8)
                }
                Text(whisper.statusMessage)
                    .font(.callout)
                    .foregroundStyle(.secondary)
                Spacer()
            }
            if whisper.phase == .transcribing && whisper.transcriptionProgress > 0 {
                ProgressView(value: whisper.transcriptionProgress)
                    .progressViewStyle(.linear)
            }
            if whisper.isBusy {
                Label {
                    Text("処理中はアプリを開いたまま、画面を点けたままにしてください。バックグラウンドや画面ロックで処理が止まる場合があります。")
                } icon: {
                    Image(systemName: "exclamationmark.triangle.fill")
                }
                .font(.caption)
                .foregroundStyle(.orange)
            }
        }
    }

    private var transcriptArea: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                if whisper.phase == .transcribing && !whisper.partialTranscript.isEmpty {
                    Label("途中経過", systemImage: "ellipsis.bubble")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text(whisper.partialTranscript)
                        .foregroundStyle(.secondary)
                        .italic()
                }

                if !whisper.transcript.isEmpty {
                    Text(whisper.transcript)
                        .textSelection(.enabled)
                } else if whisper.phase != .transcribing {
                    Text("（ここに文字起こし結果が表示されます）")
                        .foregroundStyle(.secondary)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding()
        }
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var actionButton: some View {
        Button {
            showFileImporter = true
        } label: {
            Label("音声ファイルを選択", systemImage: "waveform")
                .font(.body.bold())
                .frame(maxWidth: .infinity)
                .padding()
                .foregroundStyle(.white)
                .background(whisper.canPickFile ? Color.accentColor : Color.gray.opacity(0.4))
                .clipShape(RoundedRectangle(cornerRadius: 12))
        }
        .disabled(!whisper.canPickFile)
    }

    private func handleFileImport(_ result: Result<[URL], Error>) {
        switch result {
        case .failure(let error):
            whisper.statusMessage = "ファイル選択エラー: \(error.localizedDescription)"
        case .success(let urls):
            guard let url = urls.first else { return }
            Task { await whisper.transcribe(url: url) }
        }
    }
}

@MainActor
@Observable
final class WhisperHolder {
    enum Phase {
        case loadingModel
        case ready
        case transcribing
        case error
    }

    var phase: Phase = .loadingModel
    var statusMessage: String = "Whisper モデルを準備中..."
    var transcript: String = ""
    var partialTranscript: String = ""
    var transcriptionProgress: Double = 0

    @ObservationIgnored
    private var pipe: WhisperKit?

    var isBusy: Bool { phase == .loadingModel || phase == .transcribing }
    var canPickFile: Bool { phase == .ready }

    func loadModel() async {
        let modelName = WhisperKit.recommendedModels().default
        statusMessage = "Whisper モデル「\(modelName)」を準備中（初回は DL あり）..."
        do {
            let config = WhisperKitConfig(model: modelName)
            pipe = try await WhisperKit(config)
            phase = .ready
            statusMessage = "準備完了: \(modelName)"
        } catch {
            phase = .error
            statusMessage = "モデル「\(modelName)」のロードに失敗: \(error.localizedDescription)"
        }
    }

    func transcribe(url: URL) async {
        guard let pipe else { return }

        phase = .transcribing
        statusMessage = "文字起こしを実行中..."
        transcript = ""
        partialTranscript = ""
        transcriptionProgress = 0

        guard url.startAccessingSecurityScopedResource() else {
            statusMessage = "ファイルへのアクセス権限取得に失敗しました"
            phase = .ready
            return
        }

        let tmpURL = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathExtension(url.pathExtension)

        do {
            try FileManager.default.copyItem(at: url, to: tmpURL)
        } catch {
            url.stopAccessingSecurityScopedResource()
            statusMessage = "ファイルコピーに失敗: \(error.localizedDescription)"
            phase = .ready
            return
        }
        url.stopAccessingSecurityScopedResource()

        defer { try? FileManager.default.removeItem(at: tmpURL) }

        let totalSeconds: Double
        do {
            let asset = AVURLAsset(url: tmpURL)
            let duration = try await asset.load(.duration)
            totalSeconds = CMTimeGetSeconds(duration)
        } catch {
            totalSeconds = 0
        }

        let callback: TranscriptionCallback = { progress in
            let processedSeconds = Double(progress.windowId + 1) * 30.0
            let percent = totalSeconds > 0 ? min(1.0, processedSeconds / totalSeconds) : 0
            let text = progress.text
            Task { @MainActor [weak self] in
                guard let self else { return }
                self.transcriptionProgress = percent
                self.partialTranscript = text
                if totalSeconds > 0 {
                    self.statusMessage = "文字起こしを実行中... \(Int(percent * 100))%"
                }
            }
            return nil
        }

        do {
            let options = DecodingOptions(language: "ja", chunkingStrategy: .vad)
            let results = try await pipe.transcribe(
                audioPath: tmpURL.path,
                decodeOptions: options,
                callback: callback
            )
            transcript = results.map(\.text).joined(separator: "\n")
            partialTranscript = ""
            transcriptionProgress = 1.0
            statusMessage = "文字起こし完了（\(results.count) セグメント）"
            phase = .ready
        } catch {
            statusMessage = "文字起こしに失敗: \(error.localizedDescription)"
            phase = .ready
        }
    }
}

#Preview {
    ContentView()
}
