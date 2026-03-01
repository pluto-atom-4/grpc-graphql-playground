# Skill: run-tests

Run the complete test suite across Go, Python, and Frontend.

## Description

This skill orchestrates testing across all components of the project:
- **Go:** Unit tests for gRPC server and GraphQL gateway
- **Python:** Unit and integration tests for Kafka consumer
- **Frontend:** Component tests (vitest) and E2E tests (Playwright)

## Usage

```bash
/run-tests
```

## What it does

1. Runs Go tests: `go test ./...` (excludes frontend)
2. Runs Python tests: `cd recommender && uv run pytest`
3. Runs Frontend unit tests: `cd frontend && pnpm test`
4. Runs E2E tests: `cd frontend && pnpm exec playwright test`

## Success Criteria

- All Go tests pass
- All Python tests pass
- All frontend unit tests pass
- All E2E tests pass
- Coverage reports generated

## Common Issues

**Go tests fail:** Check `go.mod` dependencies are installed with `go mod download`

**Python tests fail:** Ensure venv is active and dependencies installed: `cd recommender && uv sync`

**Frontend tests fail:** Ensure Node modules installed: `cd frontend && pnpm install`

**Playwright fail:** Ensure browsers installed: `cd frontend && pnpm exec playwright install`

## Related

- PLAN.md (Phase 4: Tests)
- CLAUDE.md (Testing approach section)
