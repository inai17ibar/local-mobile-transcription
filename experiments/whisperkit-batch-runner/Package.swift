// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "WhisperKitBatchRunner",
    platforms: [
        .macOS(.v14),
    ],
    products: [
        .executable(name: "WhisperKitBatchRunner", targets: ["WhisperKitBatchRunner"]),
    ],
    dependencies: [
        .package(
            url: "https://github.com/argmaxinc/WhisperKit",
            revision: "9b415e5dc9b9fb4c3f55b70b89af237f8408b3c2"
        ),
    ],
    targets: [
        .executableTarget(
            name: "WhisperKitBatchRunner",
            dependencies: [
                .product(name: "WhisperKit", package: "WhisperKit"),
            ]
        ),
    ]
)
