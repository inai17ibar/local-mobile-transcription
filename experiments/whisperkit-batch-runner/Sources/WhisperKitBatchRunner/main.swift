import AVFoundation
import Foundation
import WhisperKit
#if canImport(Darwin)
import Darwin
#endif

struct CLIOptions {
    let configPath: String
    let datasetPath: String?
    let outputDir: String?
    let overwrite: Bool

    static func parse() throws -> CLIOptions {
        var configPath: String?
        var datasetPath: String?
        var outputDir: String?
        var overwrite = false

        var index = 1
        let arguments = CommandLine.arguments
        while index < arguments.count {
            let argument = arguments[index]
            switch argument {
            case "--config":
                index += 1
                configPath = try value(after: index, in: arguments, flag: argument)
            case "--dataset":
                index += 1
                datasetPath = try value(after: index, in: arguments, flag: argument)
            case "--output-dir":
                index += 1
                outputDir = try value(after: index, in: arguments, flag: argument)
            case "--overwrite":
                overwrite = true
            case "--help":
                printUsageAndExit()
            default:
                throw RunnerError.invalidArguments("Unknown argument: \(argument)")
            }
            index += 1
        }

        guard let configPath else {
            throw RunnerError.invalidArguments("Missing required --config")
        }
        return CLIOptions(configPath: configPath, datasetPath: datasetPath, outputDir: outputDir, overwrite: overwrite)
    }

    private static func value(after index: Int, in arguments: [String], flag: String) throws -> String {
        guard index < arguments.count else {
            throw RunnerError.invalidArguments("Missing value for \(flag)")
        }
        return arguments[index]
    }

    private static func printUsageAndExit() -> Never {
        print(
            """
            Usage:
              WhisperKitBatchRunner --config <path> [--dataset <path>] [--output-dir <path>] [--overwrite]
            """
        )
        exit(0)
    }
}

enum RunnerError: Error, LocalizedError {
    case invalidArguments(String)
    case invalidConfig(String)
    case invalidDataset(String)
    case unsupportedChunkingStrategy(String)
    case unsupportedArchitecture(String)

    var errorDescription: String? {
        switch self {
        case .invalidArguments(let message),
             .invalidConfig(let message),
             .invalidDataset(let message):
            return message
        case .unsupportedChunkingStrategy(let value):
            return "Unsupported chunking strategy: \(value)"
        case .unsupportedArchitecture(let message):
            return message
        }
    }
}

struct RunConfig: Decodable {
    let name: String
    let transcription: TranscriptionConfig
    let datasetManifest: String?
    let outputDir: String?

    enum CodingKeys: String, CodingKey {
        case name
        case transcription
        case datasetManifest = "dataset_manifest"
        case outputDir = "output_dir"
    }
}

struct TranscriptionConfig: Decodable {
    let model: String?
    let language: String?
    let chunkingStrategy: String?
    let temperature: Double?

    enum CodingKeys: String, CodingKey {
        case model
        case language
        case chunkingStrategy = "chunking_strategy"
        case temperature
    }
}

struct DatasetRow {
    let audioID: String
    let audioPath: String
    let refPath: String
    let notes: String
    let tags: String
}

struct SegmentDump: Encodable {
    let start: Float
    let end: Float
    let text: String
}

struct FileReport: Encodable {
    let audioID: String
    let audioPath: String
    let audioDurationSec: Double?
    let elapsedSec: Double
    let realtimeFactor: Double?
    let segmentCount: Int
}

struct RunSummary: Encodable {
    let runName: String
    let dataset: String
    let outputDir: String
    let model: String
    let language: String?
    let chunkingStrategy: String?
    let filesProcessed: Int
    let totalAudioDurationSec: Double
    let totalElapsedSec: Double
    let meanRealtimeFactor: Double?
}

@main
struct WhisperKitBatchRunner {
    static func main() async {
        do {
            try ensureSupportedRuntime()
            let options = try CLIOptions.parse()
            let config = try loadConfig(from: options.configPath)
            let datasetPath = options.datasetPath ?? config.datasetManifest ?? "experiments/data/dataset.csv"
            let outputDir = options.outputDir ?? config.outputDir ?? "experiments/results/runs/\(config.name)"
            try FileManager.default.createDirectory(atPath: outputDir, withIntermediateDirectories: true)
            try FileManager.default.createDirectory(atPath: "\(outputDir)/hyp", withIntermediateDirectories: true)
            try FileManager.default.createDirectory(atPath: "\(outputDir)/segments", withIntermediateDirectories: true)

            let dataset = try loadDataset(from: datasetPath)
            let model = resolvedModelName(from: config.transcription.model)
            let whisperConfig = WhisperKitConfig(model: model)
            let whisperKit = try await WhisperKit(whisperConfig)

            var reports: [FileReport] = []
            var totalAudioDuration = 0.0
            var totalElapsed = 0.0

            for row in dataset {
                let hypPath = "\(outputDir)/hyp/\(row.audioID).txt"
                let segmentsPath = "\(outputDir)/segments/\(row.audioID).json"
                if !options.overwrite,
                   FileManager.default.fileExists(atPath: hypPath),
                   FileManager.default.fileExists(atPath: segmentsPath) {
                    print("Skipping \(row.audioID) because outputs already exist")
                    continue
                }

                let audioDuration = try await durationSeconds(for: row.audioPath)
                let start = CFAbsoluteTimeGetCurrent()
                let decodeOptions = try makeDecodingOptions(from: config.transcription)
                let results = try await whisperKit.transcribe(audioPath: row.audioPath, decodeOptions: decodeOptions)
                let elapsed = CFAbsoluteTimeGetCurrent() - start

                let transcript = results.map(\.text).joined(separator: "\n").trimmingCharacters(in: .whitespacesAndNewlines)
                let segments = results.flatMap(\.segments).map { segment in
                    SegmentDump(start: segment.start, end: segment.end, text: segment.text)
                }

                try transcript.write(toFile: hypPath, atomically: true, encoding: .utf8)
                let encoder = JSONEncoder()
                encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
                let segmentData = try encoder.encode(segments)
                try segmentData.write(to: URL(fileURLWithPath: segmentsPath))

                let realtimeFactor = audioDuration.flatMap { duration in
                    duration > 0 ? elapsed / duration : nil
                }
                reports.append(
                    FileReport(
                        audioID: row.audioID,
                        audioPath: row.audioPath,
                        audioDurationSec: audioDuration,
                        elapsedSec: elapsed,
                        realtimeFactor: realtimeFactor,
                        segmentCount: segments.count
                    )
                )
                totalAudioDuration += audioDuration ?? 0
                totalElapsed += elapsed
                print("Processed \(row.audioID) in \(String(format: "%.2f", elapsed))s")
            }

            try writeReports(
                reports: reports,
                config: config,
                datasetPath: datasetPath,
                outputDir: outputDir,
                model: model,
                totalAudioDuration: totalAudioDuration,
                totalElapsed: totalElapsed
            )
        } catch {
            fputs("Error: \(error.localizedDescription)\n", stderr)
            exit(1)
        }
    }

    private static func loadConfig(from path: String) throws -> RunConfig {
        let data = try Data(contentsOf: URL(fileURLWithPath: path))
        return try JSONDecoder().decode(RunConfig.self, from: data)
    }

    private static func ensureSupportedRuntime() throws {
        #if arch(x86_64)
        throw RunnerError.unsupportedArchitecture(
            "WhisperKitBatchRunner is running as x86_64. WhisperKit/CoreML transcription should be run as arm64 on Apple Silicon. Try `arch -arm64 swift run --package-path experiments/whisperkit-batch-runner WhisperKitBatchRunner --config experiments/configs/baseline.whisperkit.json`."
        )
        #else
        if isRunningTranslated() {
            throw RunnerError.unsupportedArchitecture(
                "WhisperKitBatchRunner is running under Rosetta translation. Re-run it as arm64."
            )
        }
        #endif
    }

    private static func isRunningTranslated() -> Bool {
        #if canImport(Darwin)
        var translated: Int32 = 0
        var size = MemoryLayout<Int32>.size
        let result = sysctlbyname("sysctl.proc_translated", &translated, &size, nil, 0)
        return result == 0 && translated == 1
        #else
        return false
        #endif
    }

    private static func resolvedModelName(from rawValue: String?) -> String {
        guard let rawValue, rawValue != "WhisperKit.recommendedModels().default" else {
            return WhisperKit.recommendedModels().default
        }
        return rawValue
    }

    private static func makeDecodingOptions(from config: TranscriptionConfig) throws -> DecodingOptions {
        let chunkingStrategy: ChunkingStrategy?
        switch config.chunkingStrategy?.lowercased() {
        case nil, "":
            chunkingStrategy = nil
        case "vad":
            chunkingStrategy = .vad
        default:
            throw RunnerError.unsupportedChunkingStrategy(config.chunkingStrategy ?? "")
        }

        if let temperature = config.temperature, let chunkingStrategy {
            return DecodingOptions(language: config.language, temperature: Float(temperature), chunkingStrategy: chunkingStrategy)
        }
        if let temperature = config.temperature {
            return DecodingOptions(language: config.language, temperature: Float(temperature))
        }
        if let chunkingStrategy {
            return DecodingOptions(language: config.language, chunkingStrategy: chunkingStrategy)
        }
        return DecodingOptions(language: config.language)
    }

    private static func loadDataset(from path: String) throws -> [DatasetRow] {
        let content = try String(contentsOfFile: path, encoding: .utf8)
        let rows = content.split(whereSeparator: \.isNewline).map(String.init)
        guard let header = rows.first else {
            throw RunnerError.invalidDataset("Dataset CSV is empty: \(path)")
        }
        let headers = parseCSVRow(header)
        let audioIDIndex = try requireColumn("audio_id", in: headers, file: path)
        let audioPathIndex = try requireColumn("audio_path", in: headers, file: path)
        let refPathIndex = try requireColumn("ref_path", in: headers, file: path)
        let notesIndex = headers.firstIndex(of: "notes")
        let tagsIndex = headers.firstIndex(of: "tags")

        return try rows.dropFirst().map { line in
            let columns = parseCSVRow(line)
            guard columns.count >= headers.count else {
                throw RunnerError.invalidDataset("Malformed CSV row in \(path): \(line)")
            }
            return DatasetRow(
                audioID: columns[audioIDIndex],
                audioPath: columns[audioPathIndex],
                refPath: columns[refPathIndex],
                notes: notesIndex.map { columns[$0] } ?? "",
                tags: tagsIndex.map { columns[$0] } ?? ""
            )
        }
    }

    private static func requireColumn(_ name: String, in headers: [String], file: String) throws -> Int {
        guard let index = headers.firstIndex(of: name) else {
            throw RunnerError.invalidDataset("Missing required column '\(name)' in \(file)")
        }
        return index
    }

    private static func parseCSVRow(_ line: String) -> [String] {
        var fields: [String] = []
        var current = ""
        var inQuotes = false
        var iterator = line.makeIterator()

        while let character = iterator.next() {
            if character == "\"" {
                if inQuotes, let next = iterator.next() {
                    if next == "\"" {
                        current.append("\"")
                    } else {
                        inQuotes = false
                        if next == "," {
                            fields.append(current)
                            current = ""
                        } else {
                            current.append(next)
                        }
                    }
                } else {
                    inQuotes = false
                }
            } else if character == "," && !inQuotes {
                fields.append(current)
                current = ""
            } else {
                if character == "\"" && current.isEmpty {
                    inQuotes = true
                } else {
                    current.append(character)
                }
            }
        }
        fields.append(current)
        return fields
    }

    private static func durationSeconds(for path: String) async throws -> Double? {
        let url = URL(fileURLWithPath: path)
        let asset = AVURLAsset(url: url)
        let duration = try await asset.load(.duration)
        let seconds = CMTimeGetSeconds(duration)
        return seconds.isFinite ? seconds : nil
    }

    private static func writeReports(
        reports: [FileReport],
        config: RunConfig,
        datasetPath: String,
        outputDir: String,
        model: String,
        totalAudioDuration: Double,
        totalElapsed: Double
    ) throws {
        let reportPath = "\(outputDir)/transcription_report.csv"
        var csv = "audio_id,audio_path,audio_duration_sec,elapsed_sec,realtime_factor,segment_count\n"
        for report in reports {
            let audioDuration = report.audioDurationSec.map { String(format: "%.3f", $0) } ?? ""
            let elapsed = String(format: "%.3f", report.elapsedSec)
            let realtime = report.realtimeFactor.map { String(format: "%.3f", $0) } ?? ""
            csv.append("\(report.audioID),\(escapeCSV(report.audioPath)),\(audioDuration),\(elapsed),\(realtime),\(report.segmentCount)\n")
        }
        try csv.write(toFile: reportPath, atomically: true, encoding: .utf8)

        let meanRealtimeFactor = totalAudioDuration > 0 ? totalElapsed / totalAudioDuration : nil
        let summary = RunSummary(
            runName: config.name,
            dataset: datasetPath,
            outputDir: outputDir,
            model: model,
            language: config.transcription.language,
            chunkingStrategy: config.transcription.chunkingStrategy,
            filesProcessed: reports.count,
            totalAudioDurationSec: totalAudioDuration,
            totalElapsedSec: totalElapsed,
            meanRealtimeFactor: meanRealtimeFactor
        )
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let data = try encoder.encode(summary)
        try data.write(to: URL(fileURLWithPath: "\(outputDir)/run_summary.json"))
    }

    private static func escapeCSV(_ value: String) -> String {
        if value.contains(",") || value.contains("\"") {
            return "\"\(value.replacingOccurrences(of: "\"", with: "\"\""))\""
        }
        return value
    }
}
