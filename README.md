# gRPC-GraphQL Playground

A full-stack travel recommendation service demonstrating:
- **Frontend:** NextJS 14 + TypeScript + GraphQL client
- **API Gateway:** Go with GraphQL (gqlgen)
- **Backend Services:** Python Kafka consumer + Go gRPC server
- **Data Layer:** SQLite (dev) / PostgreSQL (prod) + Redpanda (Kafka)

![Architecture](docs/architecture.svg) *(to be added)*

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Agent Team](#agent-team)
5. [Development Workflow](#development-workflow)
6. [Troubleshooting](#troubleshooting)
7. [Glossary](#glossary)

---

## Prerequisites

### System Requirements (Debian 13)

#### Go 1.22+
```bash
# Option 1: Via apt (may be older version)
sudo apt update
sudo apt install golang-go

# Option 2: Via official binary (recommended for 1.22+)
wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

Verify: `go version` should output 1.22+

#### Python 3.12+
```bash
sudo apt update
sudo apt install python3 python3-dev python3-venv
```

Verify: `python3 --version` should output 3.12+

#### uv (Python package manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

Verify: `uv --version`

#### Node.js 22 LTS (via nvm)
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
# Reload shell or run: source ~/.bashrc
nvm install 22.10.0
nvm use 22.10.0
```

Verify: `node --version` should output 22.10.0

#### pnpm (Node package manager)
```bash
npm install -g pnpm
# Or via corepack (Node 16.13+):
corepack enable
```

Verify: `pnpm --version`

#### Protobuf Tools
```bash
# protoc compiler (Debian package)
sudo apt install protobuf-compiler

# buf CLI (protobuf code generator)
go install github.com/bufbuild/buf/cmd/buf@latest
```

Verify: `protoc --version` and `buf --version`

#### golangci-lint (Go linter)
```bash
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

Verify: `golangci-lint --version`

#### Docker + Docker Compose
```bash
sudo apt install docker.io docker-compose

# Add current user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

Verify: `docker --version` and `docker-compose --version`

#### GitHub CLI
```bash
sudo apt install gh
```

Verify: `gh --version`

---

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/your-org/grpc-graphql-playground.git
cd grpc-graphql-playground

# Install Node dependencies (frontend)
cd frontend
pnpm install
cd ..

# Install Python dependencies (recommender)
cd recommender
uv sync
cd ..

# Download Go modules
go mod download
```

### 2. Generate Code
```bash
# Regenerate protobuf bindings
buf generate -C recommender

# Regenerate GraphQL code
cd graphql && go run github.com/99designs/gqlgen generate && cd ..
cd frontend && pnpm run codegen && cd ..
```

### 3. Run Services with Docker Compose
```bash
# Start all backend services: Redpanda, Python recommender, Go GraphQL gateway
docker-compose up -d

# View logs from all services
docker-compose logs -f

# View logs from a specific service
docker-compose logs -f recommender
docker-compose logs -f graphql-gateway
docker-compose logs -f redpanda

# Start frontend dev server (separate terminal)
cd frontend
pnpm dev
# Frontend runs on http://localhost:3000
```

### 4. Verify Services
```bash
# Check Redpanda (Kafka) health
curl http://localhost:8081/healthz || echo "Redpanda not ready"

# Check GraphQL gateway is running
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ recommendations(userId: \"test\", limit: 5) { id name score } }"}'

# Frontend should load on http://localhost:3000

# Check all services are running
docker-compose ps
```

### 5. Stop Services
```bash
# Stop all services
docker-compose down

# Stop services and remove data volumes
docker-compose down -v
```

---

## Project Structure

```
grpc-graphql-playground/
├── .claude/                          # Claude Code configuration
│   ├── settings.json                 # Custom commands
│   ├── agents/
│   │   └── team.md                   # Agent role definitions
│   └── skills/
│       ├── run-tests/SKILL.md
│       └── proto-gen/SKILL.md
├── .gitignore                        # Multi-stack ignore patterns
├── .pre-commit-config.yaml           # Pre-commit hooks
├── README.md                         # This file
├── CLAUDE.md                         # AI agent technical guide
├── PLAN.md                           # Project roadmap
├── docker-compose.yml                # Local dev services
├── go.mod, go.sum                    # Go module definition
│
├── recommender/                      # Python Kafka consumer + gRPC server
│   ├── recommender.proto             # Service definition
│   ├── buf.yaml                      # Protobuf build config
│   ├── pyproject.toml                # Python dependencies (uv)
│   ├── generated/pb/                 # Generated protobuf code (auto)
│   ├── app/
│   │   ├── db/
│   │   │   ├── models.py             # SQLAlchemy models
│   │   │   └── session.py            # DB session factory
│   │   ├── services/
│   │   │   └── recommender.py        # Recommendation logic
│   │   └── entry/
│   │       ├── main.py               # gRPC server
│   │       └── sync.py               # Kafka consumer
│   └── tests/
│       └── test_recommender.py       # Unit tests
│
├── graphql/                          # Go GraphQL gateway (gqlgen)
│   ├── schema.graphql                # GraphQL schema
│   ├── gqlgen.yml                    # gqlgen config
│   ├── cmd/graphql/
│   │   └── main.go                   # HTTP server entrypoint
│   ├── config/
│   │   └── config.go                 # Config loading
│   ├── graph/
│   │   ├── query.go                  # Query resolvers
│   │   ├── mutation.go               # Mutation resolvers
│   │   └── query_test.go             # Tests
│   └── generated/                    # gqlgen output (auto)
│
└── frontend/                         # NextJS 14 app
    ├── package.json
    ├── pnpm-lock.yaml
    ├── next.config.js
    ├── tsconfig.json
    ├── codegen.ts                    # GraphQL code generation
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx              # Homepage
    │   │   └── layout.tsx
    │   ├── components/
    │   │   └── DestinationCard.tsx
    │   ├── generated/                # GraphQL types (auto)
    │   └── hooks/
    │       └── useRecommendations.ts
    ├── tests/
    │   ├── components.test.tsx       # vitest
    │   └── e2e/                      # Playwright
    │       └── recommendations.spec.ts
    └── public/
```

---

## Agent Team

The project uses a five-role agent team:

1. **Project Manager (PM)**
   - Roadmap management, GitHub Issues, PR reviews

2. **Backend Engineer (Go) – gRPC & GraphQL**
   - Proto definitions, gRPC server, GraphQL gateway

3. **Backend Engineer (Python) – Kafka**
   - Kafka consumer, recommendations algorithm, DB models

4. **Frontend Engineer**
   - NextJS, GraphQL client, UI components, E2E tests

5. **DevOps/QA**
   - Docker Compose, CI/CD, linting, testing coordination

See `.claude/agents/team.md` for detailed role descriptions and handshake protocol.

---

## Development Workflow

### 1. Feature Branch
```bash
# PM creates GitHub Issue with description
# Backend/Frontend engineer creates feature branch:
git checkout -b feat/issue-123-description
```

### 2. Development
```bash
# Make changes, commit with issue reference:
git commit -m "[agent-action] feat/...: description (fixes #123)"

# Run tests:
go test ./...                    # Go tests
cd recommender && uv run pytest  # Python tests
cd frontend && pnpm test         # Frontend tests
```

### 3. Code Generation
```bash
# After modifying .proto files:
buf generate -C recommender

# After modifying graphql/schema.graphql:
cd graphql && go run github.com/99designs/gqlgen generate

# After modifying GraphQL schema:
cd frontend && pnpm run codegen
```

### 4. Pull Request
```bash
# Push and create PR:
git push -u origin feat/issue-123-description
gh pr create --title "..." --body "..." --base main
```

### 5. Review & Merge
```bash
# PM reviews and merges:
gh pr merge <PR_NUMBER>
```

---

## Troubleshooting

### "protoc: command not found"
Install protobuf compiler: `sudo apt install protobuf-compiler`

### "buf: command not found"
Install buf: `go install github.com/bufbuild/buf/cmd/buf@latest`

### Python import errors after proto changes
Run: `cd recommender && uv sync` to update dependencies

### Go build fails with proto errors
Run: `buf generate -C recommender` to regenerate bindings

### Docker Compose Issues

#### Redpanda won't start
```bash
# Check Docker is running
docker ps

# Check disk space
df -h

# View Redpanda logs
docker-compose logs redpanda

# Restart Redpanda
docker-compose restart redpanda

# Full rebuild
docker-compose down -v
docker-compose up -d
```

#### Recommender service won't connect to Kafka
```bash
# Check service is running
docker-compose ps recommender

# View logs
docker-compose logs recommender

# Verify Kafka broker is accessible
docker-compose exec recommender nc -zv redpanda 29092
```

#### GraphQL gateway can't connect to gRPC recommender
```bash
# Check service is running
docker-compose ps graphql-gateway

# View logs
docker-compose logs graphql-gateway

# Check network connectivity
docker-compose exec graphql-gateway nc -zv recommender 50051
```

#### Database file permissions
```bash
# Ensure data directory is writable
chmod -R 755 ./recommender/data

# Check ownership
ls -la ./recommender/data/
```

### Frontend Issues

#### Frontend won't load recommendations
```bash
# Check GraphQL gateway is running
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ recommendations(userId: \"test\") { id name } }"}'

# Check all services are running
docker-compose ps

# View frontend logs
cd frontend && pnpm dev
# Check browser console for GraphQL errors
```

#### Port already in use (8080, 8081, 3000)
```bash
# Find process using port:
lsof -i :8080

# Kill process or use different port in docker-compose.yml
# Example: Change 8080:8080 to 8090:8080 in docker-compose.yml
```

### Clean Reset
```bash
# Stop and remove all containers, volumes, and networks
docker-compose down -v

# Remove local database
rm -f ./recommender/data/*.db

# Rebuild everything
docker-compose up -d

# Check services are healthy
docker-compose ps

# View combined logs
docker-compose logs -f
```

---

## Glossary

**gRPC:** Google's high-performance RPC framework using Protocol Buffers. Used for internal service-to-service communication.

**GraphQL:** Query language for APIs. Unified interface for frontend to query backend services (both gRPC and HTTP).

**Kafka:** Distributed event streaming platform. Used for asynchronous event processing and state building in the recommender.

**Redpanda:** Kafka-compatible message broker written in C++. Faster startup and lower resource usage than Kafka, perfect for local development.

**Protocol Buffers (Proto):** Method of serializing structured data. Defines the gRPC service contract and message types.

**buf:** Tool for working with Protocol Buffers. Lints, formats, and generates code from .proto files.

**gqlgen:** Go library for building GraphQL servers. Generates type-safe resolvers from schema.graphql.

**SQLite:** Lightweight SQL database. Used for development—zero setup required.

**PostgreSQL:** Production-grade SQL database. Replaces SQLite in production deployments.

**NextJS:** React framework for production. Provides server-side rendering, API routes, and optimizations.

**pnpm:** Fast Node package manager. Efficient monorepo and workspace support.

**uv:** Fast Python package installer and resolver. Replaces pip + venv.

**Docker Compose:** Tool for defining and running multi-container environments. Local dev stack includes Redpanda, Recommender, Gateway.

---

## Getting Help

- **Project Questions:** See CLAUDE.md and PLAN.md
- **Claude Code Help:** Run `/help`
- **Bug Report:** [GitHub Issues](https://github.com/pluto-atom-4/grpc-graphql-playground/issues)
- **Contributing:** Follow the handshake protocol in `.claude/agents/team.md`

---

**Happy building! 🚀**
