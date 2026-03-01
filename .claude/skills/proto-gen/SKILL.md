# Skill: proto-gen

Generate protobuf bindings from .proto definitions.

## Description

This skill regenerates all protobuf-generated code from the source .proto files. Use this after modifying any `.proto` file in the `recommender/` directory.

## Usage

```bash
/proto-gen
```

## What it does

1. Runs `buf generate` from the `recommender/` directory
2. Generates Go bindings: `recommender/generated/pb/*.pb.go` and `*_grpc.pb.go`
3. Generates Python bindings: `recommender/generated/pb/*_pb2.py` and `*_pb2_grpc.py`
4. Validates protobuf definitions against buf linting rules

## Files Generated

- `recommender/generated/pb/recommender.pb.go` — Go protobuf types
- `recommender/generated/pb/recommender_grpc.pb.go` — Go gRPC client/server
- `recommender/generated/pb/recommender_pb2.py` — Python protobuf types
- `recommender/generated/pb/recommender_pb2_grpc.py` — Python gRPC client/server

## Prerequisites

- `buf` CLI installed (see README.md for setup)
- `protoc` compiler installed
- Valid `buf.yaml` in recommender directory

## When to use

- After modifying `recommender/recommender.proto`
- After updating dependencies in `buf.yaml`
- Before committing proto changes

## Common Issues

**"buf: command not found":** Install buf: `go install github.com/bufbuild/buf/cmd/buf@latest`

**Generation fails:** Check `buf.yaml` is valid and dependencies are available

**Import errors in Go:** Run `go mod tidy` after proto generation to update go.mod

## Related

- recommender/recommender.proto
- buf.yaml
- CLAUDE.md (Code Generation section)
