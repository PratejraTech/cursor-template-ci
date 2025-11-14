#!/bin/zsh

set -e

ROOT="achilles"

echo "Creating Achilles Project Structure..."

# --- Helper functions ---
make_dir() {
  mkdir -p "$ROOT/$1"
  echo "  ✓ Created dir  $1"
}

make_file() {
  # ensure parent dir exists
  mkdir -p "$(dirname "$ROOT/$1")"
  touch "$ROOT/$1"
  echo "  ✓ Created file $1"
}

# --- Root ---
mkdir -p "$ROOT"

########################################
# BACKEND
########################################

# achilles_core
make_dir "backend/achilles_core/models"
make_dir "backend/achilles_core/db"
make_dir "backend/achilles_core/validation"
make_dir "backend/achilles_core/config"
make_dir "backend/achilles_core/logging"
make_dir "backend/achilles_core/tracing"
make_dir "backend/achilles_core/utils"

make_file "backend/achilles_core/__init__.py"
make_file "backend/achilles_core/models/__init__.py"
make_file "backend/achilles_core/db/__init__.py"
make_file "backend/achilles_core/validation/__init__.py"
make_file "backend/achilles_core/config/__init__.py"
make_file "backend/achilles_core/logging/__init__.py"
make_file "backend/achilles_core/tracing/__init__.py"
make_file "backend/achilles_core/utils/__init__.py"

# Placeholder module files (you'll fill them with real code)
make_file "backend/achilles_core/models/events.py"
make_file "backend/achilles_core/models/sessions.py"
make_file "backend/achilles_core/models/clusters.py"
make_file "backend/achilles_core/models/correlations.py"
make_file "backend/achilles_core/models/agent_performance.py"
make_file "backend/achilles_core/models/compressed_views.py"
make_file "backend/achilles_core/db/base.py"
make_file "backend/achilles_core/db/session.py"
make_file "backend/achilles_core/validation/events.py"
make_file "backend/achilles_core/config/settings.py"
make_file "backend/achilles_core/logging/setup.py"
make_file "backend/achilles_core/tracing/setup.py"
make_file "backend/achilles_core/utils/time.py"
make_file "backend/achilles_core/utils/ids.py"

# achilles_api
make_dir "backend/achilles_api/routers"
make_dir "backend/achilles_api/deps"
make_dir "backend/achilles_api/schemas"
make_dir "backend/achilles_api/services"
make_dir "backend/achilles_api/middleware"

make_file "backend/achilles_api/main.py"
make_file "backend/achilles_api/__init__.py"
make_file "backend/achilles_api/routers/__init__.py"
make_file "backend/achilles_api/deps/__init__.py"
make_file "backend/achilles_api/schemas/__init__.py"
make_file "backend/achilles_api/services/__init__.py"
make_file "backend/achilles_api/middleware/__init__.py"

# Placeholder router files
make_file "backend/achilles_api/routers/events.py"
make_file "backend/achilles_api/routers/sessions.py"
make_file "backend/achilles_api/routers/agents.py"
make_file "backend/achilles_api/routers/insights.py"

# achilles_processing
make_dir "backend/achilles_processing/workers"
make_dir "backend/achilles_processing/jobs"
make_dir "backend/achilles_processing/milestones"
make_dir "backend/achilles_processing/noise"
make_dir "backend/achilles_processing/clustering"
make_dir "backend/achilles_processing/correlations"
make_dir "backend/achilles_processing/summaries"
make_dir "backend/achilles_processing/scheduler"

make_file "backend/achilles_processing/__init__.py"
make_file "backend/achilles_processing/workers/__init__.py"
make_file "backend/achilles_processing/jobs/__init__.py"
make_file "backend/achilles_processing/milestones/__init__.py"
make_file "backend/achilles_processing/noise/__init__.py"
make_file "backend/achilles_processing/clustering/__init__.py"
make_file "backend/achilles_processing/correlations/__init__.py"
make_file "backend/achilles_processing/summaries/__init__.py"
make_file "backend/achilles_processing/scheduler/__init__.py"

# Entry & core processing modules
make_file "backend/achilles_processing/workers/worker_entry.py"
make_file "backend/achilles_processing/jobs/session_jobs.py"
make_file "backend/achilles_processing/milestones/inference.py"
make_file "backend/achilles_processing/noise/compression.py"
make_file "backend/achilles_processing/clustering/errors.py"
make_file "backend/achilles_processing/correlations/engine.py"
make_file "backend/achilles_processing/summaries/session_summary.py"
make_file "backend/achilles_processing/scheduler/loop.py"

# achilles_agent
make_dir "backend/achilles_agent/graphs"
make_dir "backend/achilles_agent/nodes"
make_dir "backend/achilles_agent/tools"
make_dir "backend/achilles_agent/prompts"
make_dir "backend/achilles_agent/config"

make_file "backend/achilles_agent/__init__.py"
make_file "backend/achilles_agent/graphs/__init__.py"
make_file "backend/achilles_agent/nodes/__init__.py"
make_file "backend/achilles_agent/tools/__init__.py"
make_file "backend/achilles_agent/prompts/__init__.py"
make_file "backend/achilles_agent/config/__init__.py"

make_file "backend/achilles_agent/graphs/light_monitoring.py"
make_file "backend/achilles_agent/graphs/deep_monitoring.py"
make_file "backend/achilles_agent/nodes/load_context.py"
make_file "backend/achilles_agent/nodes/analyze.py"
make_file "backend/achilles_agent/nodes/summarize.py"
make_file "backend/achilles_agent/nodes/persist.py"
make_file "backend/achilles_agent/tools/db_tools.py"
make_file "backend/achilles_agent/tools/api_tools.py"
make_file "backend/achilles_agent/prompts/system.txt"
make_file "backend/achilles_agent/config/agent_settings.py"

# achilles_migrations
make_dir "backend/achilles_migrations/versions"
make_file "backend/achilles_migrations/env.py"
make_file "backend/achilles_migrations/alembic.ini"
make_file "backend/achilles_migrations/versions/.gitkeep"

# backend tests + pyproject
make_dir "backend/tests/api"
make_dir "backend/tests/processing"
make_dir "backend/tests/agent"
make_file "backend/tests/__init__.py"
make_file "backend/tests/api/test_events.py"
make_file "backend/tests/processing/test_milestones.py"
make_file "backend/tests/agent/test_graphs.py"

make_file "backend/pyproject.toml"

########################################
# ADAPTERS
########################################

make_dir "adapters/mcp_cursor_adapter/handlers"
make_file "adapters/mcp_cursor_adapter/server.py"
make_file "adapters/mcp_cursor_adapter/handlers/__init__.py"
make_file "adapters/mcp_cursor_adapter/README.md"

make_dir "adapters/cli_tool/commands"
make_file "adapters/cli_tool/achilles"
chmod +x "$ROOT/adapters/cli_tool/achilles" 2>/dev/null || true
make_file "adapters/cli_tool/commands/__init__.py"
make_file "adapters/cli_tool/README.md"

make_dir "adapters/ci_cd_adapter"
make_file "adapters/ci_cd_adapter/ingest_tests.py"
make_file "adapters/ci_cd_adapter/ingest_build_logs.py"
make_file "adapters/ci_cd_adapter/README.md"

########################################
# DASHBOARD
########################################

make_dir "dashboard/web/pages"
make_dir "dashboard/web/components"
make_dir "dashboard/web/lib"
make_dir "dashboard/web/hooks"
make_dir "dashboard/web/public"
make_file "dashboard/web/package.json"
make_file "dashboard/web/README.md"

########################################
# INFRA
########################################

make_dir "infra/docker"
make_file "infra/docker/docker-compose.yml"
make_file "infra/docker/api.Dockerfile"
make_file "infra/docker/worker.Dockerfile"
make_file "infra/docker/agent.Dockerfile"
make_file "infra/docker/dashboard.Dockerfile"

make_dir "infra/k8s/deployments"
make_dir "infra/k8s/services"
make_dir "infra/k8s/configmaps"

make_dir "infra/terraform/modules"
make_dir "infra/terraform/environments"
make_file "infra/terraform/main.tf"

########################################
# SCRIPTS
########################################

make_dir "scripts"
make_file "scripts/dev_setup.zsh"
make_file "scripts/run_api.zsh"
make_file "scripts/run_worker.zsh"
make_file "scripts/run_agent_light.zsh"
make_file "scripts/run_agent_deep.zsh"
make_file "scripts/format.zsh"

########################################
# DOCS
########################################

make_dir "docs"
make_file "docs/REQUIREMENTS.md"
make_file "docs/TRACEABILITY.md"
make_file "docs/ARCHITECTURE.md"
make_file "docs/BUILD_PLAN.md"
make_file "docs/MODELS.md"

echo ""
echo "Achilles project structure created successfully."
