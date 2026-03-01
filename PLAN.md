# PLAN.md: Project Roadmap

## Vision

Build a full-stack travel recommendation service that demonstrates:
- Modern service-oriented architecture with gRPC and GraphQL
- Event-driven processing with Kafka
- Type-safe frontend-to-backend communication
- Dev/prod parity with containerization

**Success Criteria:**
- User sees personalized travel recommendations on frontend
- Backend processes user events asynchronously via Kafka
- All code is type-safe (Go, Python, TypeScript)
- Local development experience is smooth (Docker Compose)

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | NextJS 14 + TypeScript + urql | Modern React, server-side rendering, type safety |
| API Gateway | Go + gqlgen | Type-safe GraphQL, high performance |
| RPC Communication | gRPC + Protocol Buffers | Fast, typed, language-agnostic |
| Business Logic | Python 3.12 + Kafka consumer | Fast iteration, strong data processing |
| Event Streaming | Kafka / Redpanda | Async decoupling, event persistence |
| Database (Dev) | SQLite | Zero setup, perfect for local dev |
| Database (Prod) | PostgreSQL | Reliable, scalable, battle-tested |
| Package Managers | Go modules, uv (Python), pnpm (Node) | Modern, fast, reliable dependency management |
| Containerization | Docker + Docker Compose | Local dev parity with production |
| Linting | golangci-lint, Ruff, Biome | Multi-language quality standards |
| Testing | Go test, pytest, vitest, Playwright | Comprehensive coverage at all layers |

---

## Phase 1: Foundation (Weeks 1-2)

**Goal:** Establish proto-first architecture with working gRPC and GraphQL foundations.

### Tasks

#### 1.1 Project Scaffolding
- [x] Initialize git repository (main branch)
- [x] Create `.gitignore` (multi-stack)
- [x] Create `.claude/` configuration
  - [x] `settings.json` (custom commands)
  - [x] `agents/team.md` (role definitions)
  - [x] `skills/run-tests/SKILL.md`
  - [x] `skills/proto-gen/SKILL.md`
- [x] Create version pinning (`.nvmrc`, `.node-version`)
- [x] Create documentation
  - [x] `README.md` (Debian 13 onboarding)
  - [x] `CLAUDE.md` (AI agent guide)
  - [x] `PLAN.md` (this file)

#### 1.2 GitHub Setup
- [ ] Create remote repository on GitHub
- [ ] Push main branch
- [ ] Configure branch protection rules

#### 1.3 Proto & Code Generation
- [ ] Create `recommender/recommender.proto` with service definition
- [ ] Create `recommender/buf.yaml` (protobuf config)
- [ ] Run `buf generate` to create Go and Python bindings
- [ ] Verify generated files exist

#### 1.4 Go Module Setup
- [ ] Create `go.mod` with module name: `github.com/pluto-atom-4/grpc-graphql-playground`
- [ ] Define dependencies: gRPC, gqlgen, sqlite3
- [ ] Run `go mod download`

#### 1.5 Go gRPC Server Skeleton
- [ ] Create `recommender/client/client.go` (gRPC client wrapper)
- [ ] Create `recommender/client/client_test.go` (unit tests)
- [ ] Implement basic handler for `GetRecommendations` RPC
- [ ] Test: `go test ./recommender/client/...`

#### 1.6 Python Skeleton
- [ ] Create `recommender/pyproject.toml` with dependencies
- [ ] Run `cd recommender && uv sync`
- [ ] Create `recommender/app/entry/main.py` (gRPC server entrypoint)
- [ ] Test: `cd recommender && python3 app/entry/main.py` starts server

#### 1.7 GraphQL Gateway Skeleton
- [ ] Create `graphql/schema.graphql` with Query root
- [ ] Create `graphql/gqlgen.yml` config
- [ ] Run `go run github.com/99designs/gqlgen generate`
- [ ] Create `graphql/cmd/graphql/main.go` (HTTP server)
- [ ] Test: `curl http://localhost:8080/graphql` returns schema

#### 1.8 Tests & Quality
- [ ] Create `.pre-commit-config.yaml`
- [ ] Install pre-commit hooks: `pre-commit install`
- [ ] Run linters on all code: `golangci-lint run`, `ruff check`
- [ ] All tests passing: `go test ./...`

### Deliverables
- Working git repository with clean structure
- Proto definitions and generated bindings
- Go and Python gRPC servers start successfully
- GraphQL gateway responds to introspection queries
- All tests pass
- Pre-commit hooks configured

### Verification Checklist
- [ ] `go build ./...` succeeds
- [ ] `go test ./...` passes
- [ ] `cd recommender && uv run pytest` passes
- [ ] `curl http://localhost:8080/graphql` returns schema
- [ ] No linter errors

---

## Phase 2: Core Features (Weeks 3-4)

**Goal:** Implement recommendation logic, Kafka consumer, and complete GraphQL API.

### Tasks

#### 2.1 Database Models
- [ ] Create `recommender/app/db/models.py`
  - [ ] `Destination` model
  - [ ] `UserEvent` model
  - [ ] `Recommendation` model
- [ ] Create `recommender/app/db/session.py` (SQLite dev, PostgreSQL prod)
- [ ] Write model tests

#### 2.2 Kafka Consumer
- [ ] Create `recommender/app/entry/sync.py` (Kafka consumer loop)
  - [ ] Connect to Redpanda
  - [ ] Consume user events
  - [ ] Parse event schema
  - [ ] Update database state
- [ ] Create `docker-compose.yml` with Redpanda service
- [ ] Test: Events flow through Kafka to database

#### 2.3 Recommendation Logic
- [ ] Create `recommender/app/services/recommender.py`
  - [ ] Implement popularity-based recommendations (MVP)
  - [ ] Filter by user preferences
  - [ ] Return top N destinations
- [ ] Write unit tests for recommendation algorithm
- [ ] Test: `curl localhost:50051` gRPC call returns recommendations

#### 2.4 GraphQL Resolvers
- [ ] Update `graphql/schema.graphql` with full query fields
  - [ ] `recommendations(userId: String!, limit: Int): [Destination!]!`
  - [ ] `destinations: [Destination!]!`
- [ ] Create `graphql/graph/query.go` with resolvers
  - [ ] Call gRPC recommender service
  - [ ] Map gRPC response to GraphQL types
- [ ] Create `graphql/graph/query_test.go` with mock gRPC
- [ ] Test: `curl -X POST http://localhost:8080/graphql`

#### 2.5 Docker Compose Full Stack
- [ ] Add `recommender` Python service to `docker-compose.yml`
- [ ] Add `graphql-gateway` Go service
- [ ] Wire networking and port mappings
- [ ] Test: `docker-compose up -d && curl http://localhost:8080/graphql`

#### 2.6 Integration Tests
- [ ] Create integration test that flows: Kafka → Python → Go gRPC → GraphQL
- [ ] Document test execution in CI (pre-commit hooks)

### Deliverables
- Recommendation algorithm working (popularity-based MVP)
- Kafka consumer ingesting events
- GraphQL API resolving recommendations via gRPC
- Full stack running via Docker Compose
- Integration tests passing

### Verification Checklist
- [ ] `docker-compose up -d` starts all services
- [ ] GraphQL query returns recommendations: `curl -X POST http://localhost:8080/graphql -d '...'`
- [ ] Python consumer processes events
- [ ] All tests pass

---

## Phase 3: Frontend & E2E (Weeks 5-6)

**Goal:** Build NextJS frontend and E2E tests, complete MVP.

### Tasks

#### 3.1 NextJS Setup
- [ ] Initialize Next.js 14 in `frontend/` directory
- [ ] Configure TypeScript
- [ ] Install dependencies: urql, graphql-tag, etc.
- [ ] Create `frontend/next.config.js` with GraphQL gateway proxy

#### 3.2 GraphQL Code Generation
- [ ] Create `frontend/codegen.ts` (GraphQL codegen config)
- [ ] Configure schema source: `http://localhost:8080/graphql`
- [ ] Configure output: `src/generated/`
- [ ] Create `pnpm run codegen` script

#### 3.3 Frontend Components
- [ ] Create `frontend/src/app/page.tsx` (homepage)
  - [ ] Display travel recommendations
  - [ ] Accept user ID input
- [ ] Create `frontend/src/components/DestinationCard.tsx`
  - [ ] Display destination name, region, score
  - [ ] Responsive design
- [ ] Create `frontend/src/hooks/useRecommendations.ts`
  - [ ] GraphQL query wrapper
  - [ ] Error handling

#### 3.4 Frontend Testing
- [ ] Set up vitest for unit tests
- [ ] Create `frontend/tests/components.test.tsx`
  - [ ] Test DestinationCard rendering
  - [ ] Mock GraphQL responses
- [ ] Run: `cd frontend && pnpm test`

#### 3.5 E2E Tests
- [ ] Set up Playwright
- [ ] Create `frontend/tests/e2e/recommendations.spec.ts`
  - [ ] Load homepage
  - [ ] Enter user ID
  - [ ] Verify recommendations appear
  - [ ] Click destination (future interaction)
- [ ] Run: `cd frontend && pnpm exec playwright test`

#### 3.6 End-to-End Verification
- [ ] Start full stack: `docker-compose up -d && cd frontend && pnpm dev`
- [ ] Verify frontend loads: `http://localhost:3000`
- [ ] Verify GraphQL requests work
- [ ] Verify recommendations display correctly

### Deliverables
- NextJS frontend running on `localhost:3000`
- GraphQL code generation working
- Component tests passing
- E2E tests passing (full flow: UI → GraphQL → gRPC → Kafka → DB)
- MVP complete and functional

### Verification Checklist
- [ ] `pnpm dev` starts frontend
- [ ] Frontend loads recommendations from GraphQL
- [ ] E2E tests pass: `cd frontend && pnpm exec playwright test`
- [ ] No console errors in browser
- [ ] Can trace: UI → GraphQL → gRPC → Python → Kafka → SQLite

---

## Phase 4: Production Readiness (Future)

**Goal:** Prepare for production deployment.

### Tasks

#### 4.1 Database
- [ ] Create Alembic migrations for SQLAlchemy models
- [ ] Test PostgreSQL locally
- [ ] Document connection string configuration

#### 4.2 Scaling & Performance
- [ ] Implement caching layer (Redis)
- [ ] Add request timeout handling
- [ ] Implement rate limiting on GraphQL gateway
- [ ] Load test full stack

#### 4.3 Observability
- [ ] Add structured logging
- [ ] Add distributed tracing (Jaeger)
- [ ] Add metrics (Prometheus)
- [ ] Create dashboards

#### 4.4 Security
- [ ] Add authentication (JWT)
- [ ] Add authorization on GraphQL
- [ ] Audit dependencies for vulnerabilities
- [ ] Document security best practices

#### 4.5 Deployment
- [ ] Create Kubernetes manifests
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Document production deployment
- [ ] Create runbook for common operations

---

## Critical Milestones

| Milestone | Target Date | Criteria |
|-----------|------------|----------|
| Scaffolding Complete | Week 1 | Git repo, docs, proto definitions |
| Recommendations API Live | Week 2 | gRPC server serving real recommendations |
| Full Stack Running | Week 3 | Docker Compose with all services |
| Frontend MVP | Week 4 | NextJS displaying recommendations |
| E2E Passing | Week 5 | Full flow tested end-to-end |
| Production Ready | Week 8+ | Monitoring, security, scalability |

---

## Known Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Proto changes break multiple services | Semantic versioning, generated code in git |
| Kafka ordering issues | Use partitions by user_id |
| GraphQL N+1 queries | DataLoader pattern (future phase) |
| Database migrations blocking | Separate migration services, backward compatibility |
| Python/Go version mismatch | Pin versions in `.python-version`, `go.mod` |

---

## Success Metrics

- All tests passing in CI/CD
- Frontend E2E tests pass reliably
- Code coverage > 80%
- No linter errors
- Deployment time < 5 minutes
- P99 latency < 100ms for recommendations query

---

## Glossary of Phases

- **Phase 1: Foundation** — Infrastructure, proto, skeletons
- **Phase 2: Core Features** — Business logic, Kafka, GraphQL API
- **Phase 3: Frontend & E2E** — User interface, full-stack testing
- **Phase 4: Production** — Scaling, observability, security

---

## How to Use This Plan

1. **Agents:** Review your phase tasks before starting work
2. **PM:** Update task status as work progresses
3. **All:** Check verification checklist before marking phase complete
4. **All:** Report blockers immediately; don't work around them

**Questions?** See CLAUDE.md for architecture details, README.md for setup help.
