# CLAUDE.md: Technical Guide for AI Agents

This document guides AI agents through the project architecture, development philosophy, and key patterns.

## Project Context

**Goal:** Build a full-stack travel recommendation service demonstrating modern distributed system patterns.

**Stack:**
- **Frontend:** NextJS 14 (TypeScript, urql GraphQL client)
- **API Gateway:** Go (GraphQL via gqlgen)
- **Recommender Service:** Python (Kafka consumer, gRPC server)
- **Infrastructure:** Docker Compose, Redpanda (Kafka), SQLite/PostgreSQL
- **Message Queue:** Kafka (Redpanda locally)

**Decision Rationale:**
- **Go over Ruby/Python for gRPC:** 3-10x faster performance, better concurrency for high-volume event processing
- **SQLite for dev:** Zero infrastructure, instant setup, eliminates local network latency
- **Redpanda over Kafka:** Drop-in replacement, faster startup, lower memory footprint for local dev
- **GraphQL + gRPC:** GraphQL for unified frontend API, gRPC for performant internal communication
- **NextJS + Go Gateway:** Type-safe full-stack with modern tooling, avoiding NestJS overweight

---

## Architecture

### Data Flow

```
Frontend (NextJS)
    ↓ GraphQL Query (HTTP)
GraphQL Gateway (Go gqlgen)
    ↓ gRPC Call
Recommender Server (Go gRPC)
    ↓ Query/Insert
SQLite (dev) / PostgreSQL (prod)

User Events → Kafka → Python Recommender Consumer → Builds state in DB
```

### Service Boundaries

1. **Frontend:** UI rendering, user interactions, GraphQL queries
2. **GraphQL Gateway:** HTTP endpoint, resolves GraphQL schema to gRPC calls
3. **Recommender (Go gRPC):** Core business logic, queries recommendations from state
4. **Recommender (Python Consumer):** Ingests user events from Kafka, updates state

### Why Separate Go gRPC + Python Consumer?

- **Go gRPC:** Synchronous request-response, low latency, suitable for real-time queries
- **Python Consumer:** Asynchronous event processing, state building, loose coupling via Kafka
- **Separation of concerns:** Recommendation generation (Python) independent from serving (Go)

---

## Development Phases

### Phase 1: Foundation (Proto-first)
1. Define `recommender.proto` with service contract
2. Generate Go and Python bindings via `buf`
3. Implement Go gRPC server skeleton
4. Implement Python gRPC server entrypoint
5. Test proto → bindings pipeline

**Key commands:**
```bash
buf generate -C recommender
go build ./recommender/...
cd recommender && python3 -m grpc_tools.protoc...
```

### Phase 2: Services
1. Implement Go gRPC server logic (client wrapper, handlers)
2. Implement Python Kafka consumer (event loop, state building)
3. Implement database models (SQLAlchemy)
4. Wire up Docker Compose services

**Key files:**
- `recommender/client/client.go` — gRPC client for gateway to use
- `recommender/app/entry/main.py` — Python gRPC server
- `recommender/app/entry/sync.py` — Kafka consumer loop
- `recommender/app/services/recommender.py` — Recommendation algorithm

### Phase 3: Gateway
1. Define `graphql/schema.graphql` (Query for destinations)
2. Configure `gqlgen.yml`
3. Run `go run github.com/99designs/gqlgen generate`
4. Implement resolvers in `graphql/graph/query.go`
5. Wire up gRPC client calls
6. Test via `curl localhost:8080/graphql`

### Phase 4: Frontend
1. Initialize Next.js 14 with TypeScript
2. Configure GraphQL code generation (codegen.ts)
3. Create UI components (DestinationCard)
4. Implement GraphQL queries using urql
5. Add vitest and Playwright tests
6. Verify end-to-end flow

---

## Code Generation Pipeline

### Protobuf Generation
**Trigger:** After modifying `recommender/recommender.proto`

```bash
cd recommender
buf generate
```

**Output:**
- `generated/pb/recommender.pb.go` — Go message types
- `generated/pb/recommender_grpc.pb.go` — Go service stubs
- `generated/pb/recommender_pb2.py` — Python message types
- `generated/pb/recommender_pb2_grpc.py` — Python service stubs

**Dependencies:**
- `buf.yaml` in recommender directory
- `protoc` compiler installed
- `buf` CLI installed

### GraphQL Code Generation
**Trigger:** After modifying `graphql/schema.graphql`

```bash
cd graphql
go run github.com/99designs/gqlgen generate
```

**Output:** `graphql/generated/generated.go` with type-safe resolvers

**Config:** `graphql/gqlgen.yml` defines schema location, output paths

### Frontend GraphQL Code Generation
**Trigger:** After updating GraphQL schema

```bash
cd frontend
pnpm run codegen
```

**Output:** `src/generated/` with TypeScript types matching schema

**Config:** `codegen.ts` defines schema source and output directory

---

## Testing Strategy

### Go Tests
**Command:** `go test ./...` (from repo root)

**Scope:**
- Unit tests for gRPC client wrapper (`recommender/client/client_test.go`)
- Unit tests for GraphQL resolvers (`graphql/graph/query_test.go`)
- Mock gRPC servers for testing without live services
- Table-driven tests for multiple scenarios

**Pattern:**
```go
func TestGetRecommendations(t *testing.T) {
    // Setup mock gRPC server
    // Make gRPC call
    // Assert response
}
```

### Python Tests
**Command:** `cd recommender && uv run pytest`

**Scope:**
- Unit tests for recommendation logic (`tests/test_recommender.py`)
- Unit tests for DB models (`tests/test_models.py`)
- Integration tests with SQLite in-memory DB
- Event processing pipeline tests

**Pattern:**
```python
def test_get_recommendations():
    # Setup in-memory DB
    # Call recommendation service
    # Assert results
```

### Frontend Tests
**Unit Tests:**
```bash
cd frontend && pnpm test
```

Scope: Component rendering, GraphQL query mocking, user interactions

**E2E Tests:**
```bash
cd frontend && pnpm exec playwright test
```

Scope: Full flow from user action to recommendation display

**Pattern:**
```typescript
test('shows recommendations', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await expect(page).toContainText('Recommendations');
});
```

### Integration Testing
**Command:** `docker-compose up -d && npm run test:integration`

Tests full stack:
1. Python consumer ingests events from Redpanda
2. Go gRPC server queries updated state
3. GraphQL gateway resolves queries
4. Frontend displays results

---

## Key Configuration Files

### `.claude/settings.json`
Custom commands for development workflow:
```json
{
  "commands": {
    "proto-gen": "cd recommender && buf generate",
    "graphql-gen": "cd graphql && go run github.com/99designs/gqlgen generate",
    "test-go": "go test ./...",
    "test-py": "cd recommender && uv run pytest",
    "test-e2e": "cd frontend && pnpm exec playwright test"
  }
}
```

### `.claude/agents/team.md`
Defines five agent roles and handshake protocol:
1. Project Manager
2. Backend Engineer (Go)
3. Backend Engineer (Python)
4. Frontend Engineer
5. DevOps/QA

Agents verify GitHub Issue assignment → implement → create PR → PM reviews/merges

### `go.mod`
Go module definition and dependencies:
```
module github.com/pluto-atom-4/grpc-graphql-playground
go 1.22

require (
    google.golang.org/grpc v1.50+
    github.com/99designs/gqlgen v0.17+
    github.com/mattn/go-sqlite3 v1.14+
)
```

### `recommender/pyproject.toml`
Python project config using uv:
```toml
[project]
name = "recommender"
dependencies = [
    "grpcio==1.50+",
    "kafka-python==2.0+",
    "sqlalchemy==2.0+",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"
```

### `recommender/buf.yaml`
Protobuf build configuration:
```yaml
version: v2
modules:
  - path: recommender
deps:
  - buf.build/googleapis/googleapis
```

### `graphql/schema.graphql`
GraphQL schema defining the API:
```graphql
type Query {
    recommendations(userId: String!, limit: Int): [Destination!]!
}

type Destination {
    id: String!
    name: String!
    region: String!
    score: Float!
}
```

### `graphql/gqlgen.yml`
gqlgen configuration:
```yaml
schema:
  - graphql/schema.graphql
exec:
  filename: graphql/generated/generated.go
resolver:
  layout: follow-schema
```

### `.pre-commit-config.yaml`
Pre-commit hooks:
- Python: Ruff (lint + format)
- Go: gofmt + golangci-lint
- General: Large files, trailing whitespace, merge conflicts

### `docker-compose.yml`
Local services:
- `redpanda`: Kafka-compatible message broker (port 29092)
- `recommender`: Python gRPC service (port 50051)
- `graphql-gateway`: Go GraphQL HTTP (port 8080)

---

## Common Patterns

### Implementing a GraphQL Query
1. Add field to `graphql/schema.graphql`
2. Run `go run github.com/99designs/gqlgen generate`
3. Implement resolver in `graphql/graph/query.go`
4. Call gRPC method: `g.recommender.GetRecommendations(...)`
5. Return typed response
6. Test with `curl -X POST http://localhost:8080/graphql -d '...'`

### Modifying Proto
1. Edit `recommender/recommender.proto`
2. Run `buf generate -C recommender`
3. Update corresponding handlers in Go gRPC server
4. Update corresponding methods in Python gRPC server
5. Ensure tests still pass

### Adding Python Dependency
1. Edit `recommender/pyproject.toml` (dependencies section)
2. Run `cd recommender && uv sync`
3. Commit pyproject.toml (uv.lock is generated)
4. All agents can now use dependency

### Deploying to Production
1. Update `recommender/app/db/session.py` to use PostgreSQL DSN
2. Update `docker-compose.yml` to use PostgreSQL
3. Update environment variables for production Kafka
4. Run migrations: `alembic upgrade head`
5. Deploy containers (specific deployment platform not in scope)

---

## Debugging Tips

### gRPC Client Won't Connect
- Check service is running: `docker-compose ps`
- Check port: GraphQL → Recommender should use port 50051
- Check network: `docker network ls` and ensure services on same network

### GraphQL Query Returns Error
- Check resolver is implemented in `graphql/graph/query.go`
- Check gRPC call syntax and error handling
- Check mock data if testing without live gRPC service
- Use `curl -X POST http://localhost:8080/graphql` to test directly

### Python Tests Fail
- Ensure venv is active or using uv: `cd recommender && uv run pytest`
- Check database file path in `config/settings.py`
- Check Kafka is running if testing consumer

### Protobuf Import Errors
- Run `go mod tidy` after proto generation
- Ensure `buf.yaml` dependencies are available
- Check generated files were created in expected paths

### Docker Container Won't Start
- Check logs: `docker-compose logs <service>`
- Check ports not already in use
- Check volume permissions for SQLite files

---

## Agent Responsibilities Matrix

| Phase | Go Backend | Python Backend | Frontend | DevOps |
|-------|-----------|-----------------|----------|--------|
| Proto definition | ✓ | review | — | review |
| Generate bindings | ✓ (via buf) | ✓ (generated) | — | ✓ (setup) |
| gRPC server | ✓ | ✓ | — | — |
| Kafka consumer | — | ✓ | — | ✓ (setup) |
| GraphQL schema | ✓ | — | review | — |
| GraphQL resolvers | ✓ | — | — | — |
| GraphQL codegen | — | — | ✓ | — |
| Frontend | — | — | ✓ | — |
| Tests | ✓ (Go) | ✓ (Python) | ✓ (TS) | ✓ (E2E) |
| Docker Compose | review | — | — | ✓ |
| CI/CD | — | — | — | ✓ |

---

## When to Ask for Help

- **Blocking:** Can't find file, unclear architecture decision → Ask PM
- **Proto/gRPC issue:** Multiple agents affected → PM coordinates
- **Build failure:** After code changes → Relevant agent debugs
- **Dependency conflict:** Multiple agents affected → DevOps resolves
- **Test failure:** Work with relevant agent for domain
