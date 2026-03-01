# Claude Code Configuration

This directory contains AI agent configuration and automation for development using Claude Code.

## Files & Purpose

### `settings.json`
Custom CLI commands for the project development workflow:
- `proto-gen` - Regenerate protobuf bindings
- `graphql-gen` - Regenerate GraphQL code
- `test-go`, `test-py`, `test-e2e` - Run test suites
- `lint-go`, `lint-py`, `lint-frontend` - Run linters
- `dev-all` - Start all services with Docker Compose

**For:** Claude Code users (accessible via `/command-name`)

### `agents/team.md`
Defines the multi-agent team structure and coordination workflow:
- **Project Manager** - GitHub issues, PR reviews, planning
- **Backend Engineer (Go)** - gRPC server, GraphQL gateway
- **Backend Engineer (Python)** - Kafka consumer, recommendations
- **Frontend Engineer** - NextJS, React components, E2E tests
- **DevOps/QA** - Docker, CI/CD, testing, linting

**Includes:** Agent handshake protocol for coordinated development

**For:** Team members using Claude Code for multi-agent workflows

### `skills/`
Reusable automation skills:
- `run-tests/SKILL.md` - Run full test suite (Go + Python + E2E)
- `proto-gen/SKILL.md` - Regenerate protobuf bindings

**For:** Automating common repetitive tasks

---

## Who Uses This?

### ✅ **Claude Code Users**
These files enable AI-assisted development with:
- Shared team configuration
- Automated command execution
- Consistent development workflow
- Reusable skills and automation

### ❌ **Regular Developers**
You don't need this. Use your standard workflow:
- Git, CLI, and your favorite IDE
- `go test`, `pytest`, `pnpm test` directly
- `docker compose up` for services

---

## Local Files (Not Committed)

These are in `.gitignore` and are local-only:
- `.claude/cache/` - Session cache
- `.claude/workspace/` - Workspace state
- `.claude/*.log` - Execution logs
- `.claude/session-*` - Session files
- `.claude/tmp/` - Temporary files

---

## Getting Started with Claude Code

1. **If using Claude Code:**
   - Open this project
   - Use custom commands: `/proto-gen`, `/test-go`, `/lint-py`
   - Read `agents/team.md` for team workflow
   - Access skills for automation

2. **If not using Claude Code:**
   - You can safely ignore this directory
   - It won't affect your normal development

---

## References

- **README.md** - Main project documentation
- **CLAUDE.md** - Technical guide for AI agents
- **PLAN.md** - Project roadmap and phases
