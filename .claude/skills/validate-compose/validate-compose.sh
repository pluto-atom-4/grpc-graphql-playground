#!/bin/bash
# Docker Compose validation script
# Validates docker-compose.yml without building images or starting containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║         DOCKER-COMPOSE VALIDATION (WITHOUT BUILDING/STARTING)             ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check docker compose command exists
if ! command -v docker compose &> /dev/null; then
    echo "❌ ERROR: 'docker compose' command not found"
    echo "   Please install Docker Desktop or Docker Engine"
    exit 1
fi

# Step 2: Syntax validation using docker compose config
echo "📋 STEP 1: Validating YAML syntax..."
echo "   Command: docker compose config --quiet"
echo ""

if docker compose -f "$PROJECT_ROOT/docker-compose.yml" config --quiet 2>&1 | grep -q "the attribute \`version\` is obsolete"; then
    echo "   ⚠️  Warning: 'version' field is deprecated (can be removed)"
    echo ""
fi

if docker compose -f "$PROJECT_ROOT/docker-compose.yml" config --quiet; then
    echo "   ✅ YAML syntax is valid"
    echo ""
else
    echo "   ❌ YAML syntax error"
    exit 1
fi

# Step 3: Python-based comprehensive analysis
echo "📋 STEP 2: Detailed configuration analysis..."
echo ""

PYTHON_SCRIPT="$SCRIPT_DIR/validate-compose.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ ERROR: validate-compose.py not found"
    exit 1
fi

# Run Python validation
python3 "$PYTHON_SCRIPT" "$PROJECT_ROOT/docker-compose.yml"

echo ""
echo "✅ VALIDATION COMPLETE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next step: Run 'docker compose up -d' to start services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
