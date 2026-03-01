# Skill: validate-compose

Validate docker-compose.yml configuration without building images or starting containers.

## Description

This skill performs comprehensive validation of the `docker-compose.yml` file including:
- YAML syntax validation
- Service configuration verification
- Dockerfile & build context validation
- Network and volume configuration checks
- Port conflict detection
- Service dependency analysis
- Environment variable verification
- Health check validation
- Data persistence review

All validation is performed **without**:
- Building Docker images
- Starting containers
- Pulling images from registry
- Requiring Docker daemon to be running

## Usage

```bash
/validate-compose
```

## What It Does

1. **Syntax Check**: Validates YAML structure using `docker compose config --quiet`
2. **Configuration Analysis**: Extracts and verifies all service settings
3. **Build Context Validation**: Checks that all Dockerfiles exist
4. **Dependency Graph**: Analyzes service startup order and dependencies
5. **Port Mapping**: Verifies no port conflicts
6. **Network Connectivity**: Checks internal service communication setup
7. **Volume Configuration**: Reviews data persistence setup
8. **Health Checks**: Validates health check configuration
9. **Environment Variables**: Verifies all required env vars are set

## Output

Generates comprehensive report with:
- ✅ Validation results for each check
- ⚠️ Warnings for deprecated settings
- 📋 Service dependency chain
- 🔌 Port mapping diagram
- 🔗 Service connectivity verification
- 💾 Data persistence review
- 🌐 Network configuration details

## Example Output

```
✅ YAML syntax valid

SERVICES VALIDATION:
✅ redpanda - Uses image: docker.redpanda.com/redpanda:latest
✅ recommender - Dockerfile exists
✅ graphql-gateway - Dockerfile exists

STARTUP ORDER:
1. redpanda (wait for health check)
2. recommender (wait for redpanda healthy)
3. graphql-gateway (wait for recommender started)

PORT MAPPING:
✅ 8081, 8082, 29092, 9092 (Redpanda)
✅ 50051 (Recommender gRPC)
✅ 8080 (GraphQL Gateway)
✅ No port conflicts detected
```

## Prerequisites

- `docker compose` CLI installed
- `python3` with `pyyaml` module
- Read access to docker-compose.yml
- No Docker daemon required

## Common Issues

**"YAML syntax error"**
- Fix the YAML formatting in docker-compose.yml
- Use an online YAML validator to debug

**"Dockerfile not found"**
- Verify Dockerfile path in build context
- Check relative paths from docker-compose.yml directory

**"Port already in use"**
- Choose a different port in docker-compose.yml
- Or stop the service using the port: `lsof -i :PORT`

## Related Skills

- `proto-gen` - Generate protobuf code
- `run-tests` - Run all tests
- `lint` - Run linters

## When to Use

✅ Before pushing changes to docker-compose.yml
✅ When troubleshooting Docker Compose issues
✅ During code review to validate infrastructure
✅ In CI/CD to catch configuration errors early
✅ When onboarding new team members
