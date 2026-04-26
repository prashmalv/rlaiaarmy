#!/usr/bin/env bash
# ── GCP Cloud Run Deployment Script ──────────────────────────────────────────
# Deploys both AI Dev Team and AI Marketing Team to Google Cloud Run
# Region: asia-south1 (Mumbai)
#
# Prerequisites:
#   1. gcloud CLI installed
#   2. Service account key at $KEY_FILE (set below or pass as first arg)
#   3. Service account has these roles:
#      - Artifact Registry Administrator
#      - Cloud Run Admin
#      - Service Account User
#      - Storage Admin
#      - Service Usage Admin (to enable APIs)
#      - Secret Manager Secret Accessor (optional, for secrets)
#
# Usage:
#   chmod +x deploy-gcp.sh
#   ./deploy-gcp.sh [/path/to/service-account-key.json]
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_ID="rlai-apr"
REGION="asia-south1"
REGISTRY_REPO="ai-army"
KEY_FILE="${1:-/tmp/rlai-deploy/rlai-key.json}"

# Cloud Run service names
DEV_BACKEND_SVC="ai-dev-team-backend"
DEV_FRONTEND_SVC="ai-dev-team-frontend"
MKT_BACKEND_SVC="ai-marketing-backend"
MKT_FRONTEND_SVC="ai-marketing-frontend"

# Image names
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REGISTRY_REPO}"
DEV_BACKEND_IMG="${REGISTRY}/${DEV_BACKEND_SVC}:latest"
DEV_FRONTEND_IMG="${REGISTRY}/${DEV_FRONTEND_SVC}:latest"
MKT_BACKEND_IMG="${REGISTRY}/${MKT_BACKEND_SVC}:latest"
MKT_FRONTEND_IMG="${REGISTRY}/${MKT_FRONTEND_SVC}:latest"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Helpers ───────────────────────────────────────────────────────────────────
log()  { echo -e "\n\033[1;34m▶ $*\033[0m"; }
ok()   { echo -e "\033[1;32m✓ $*\033[0m"; }
warn() { echo -e "\033[1;33m⚠ $*\033[0m"; }
die()  { echo -e "\033[1;31m✗ $*\033[0m"; exit 1; }

# ── Authenticate ──────────────────────────────────────────────────────────────
log "Authenticating with GCP..."
if [[ ! -f "$KEY_FILE" ]]; then
  die "Service account key not found at: $KEY_FILE"
fi
gcloud auth activate-service-account --key-file="$KEY_FILE" --quiet
gcloud config set project "$PROJECT_ID" --quiet
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
ok "Authenticated as $(gcloud config get-value account)"

# ── Enable required APIs ──────────────────────────────────────────────────────
log "Enabling required GCP APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  --project="$PROJECT_ID" --quiet
ok "APIs enabled"

# ── Create Artifact Registry repo ────────────────────────────────────────────
log "Ensuring Artifact Registry repository exists..."
if ! gcloud artifacts repositories describe "$REGISTRY_REPO" \
     --location="$REGION" --project="$PROJECT_ID" &>/dev/null; then
  gcloud artifacts repositories create "$REGISTRY_REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="AI Army Docker images" \
    --project="$PROJECT_ID" --quiet
  ok "Repository '$REGISTRY_REPO' created"
else
  ok "Repository '$REGISTRY_REPO' already exists"
fi

# ── Build & Push images ───────────────────────────────────────────────────────
log "Building and pushing AI Dev Team backend..."
docker build -t "$DEV_BACKEND_IMG" "${SCRIPT_DIR}/ai-dev-team/backend"
docker push "$DEV_BACKEND_IMG"
ok "Dev backend image pushed"

log "Building and pushing AI Dev Team frontend..."
docker build -t "$DEV_FRONTEND_IMG" "${SCRIPT_DIR}/ai-dev-team/frontend"
docker push "$DEV_FRONTEND_IMG"
ok "Dev frontend image pushed"

log "Building and pushing AI Marketing Team backend..."
docker build -t "$MKT_BACKEND_IMG" "${SCRIPT_DIR}/ai-marketing-team/backend"
docker push "$MKT_BACKEND_IMG"
ok "Marketing backend image pushed"

log "Building and pushing AI Marketing Team frontend..."
docker build -t "$MKT_FRONTEND_IMG" "${SCRIPT_DIR}/ai-marketing-team/frontend"
docker push "$MKT_FRONTEND_IMG"
ok "Marketing frontend image pushed"

# ── Deploy backends ───────────────────────────────────────────────────────────
# IMPORTANT: Set your actual API keys below, or export them as env vars before running.
# Required: ANTHROPIC_API_KEY
# Optional: OPENAI_API_KEY (for DALL-E image generation), PEXELS_API_KEY (fallback images)
: "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY env var must be set before running this script}"

log "Deploying AI Dev Team backend..."
gcloud run deploy "$DEV_BACKEND_SVC" \
  --image="$DEV_BACKEND_IMG" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=900 \
  --concurrency=10 \
  --min-instances=0 \
  --max-instances=3 \
  --set-env-vars="ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY},OUTPUT_DIR=/tmp/generated_projects,REPORTS_DIR=/tmp/reports_output,ALLOWED_ORIGINS=https://${DEV_FRONTEND_SVC}-placeholder.run.app" \
  --project="$PROJECT_ID" --quiet

DEV_BACKEND_URL=$(gcloud run services describe "$DEV_BACKEND_SVC" \
  --region="$REGION" --project="$PROJECT_ID" \
  --format="value(status.url)")
ok "Dev backend live at: $DEV_BACKEND_URL"

log "Deploying AI Marketing Team backend..."
OPENAI_KEY="${OPENAI_API_KEY:-}"
PEXELS_KEY="${PEXELS_API_KEY:-}"

gcloud run deploy "$MKT_BACKEND_SVC" \
  --image="$MKT_BACKEND_IMG" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=600 \
  --concurrency=20 \
  --min-instances=0 \
  --max-instances=3 \
  --set-env-vars="ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY},OPENAI_API_KEY=${OPENAI_KEY},PEXELS_API_KEY=${PEXELS_KEY},ALLOWED_ORIGINS=https://${MKT_FRONTEND_SVC}-placeholder.run.app" \
  --project="$PROJECT_ID" --quiet

MKT_BACKEND_URL=$(gcloud run services describe "$MKT_BACKEND_SVC" \
  --region="$REGION" --project="$PROJECT_ID" \
  --format="value(status.url)")
ok "Marketing backend live at: $MKT_BACKEND_URL"

# ── Deploy frontends (with BACKEND_URL wired in) ──────────────────────────────
log "Deploying AI Dev Team frontend..."
gcloud run deploy "$DEV_FRONTEND_SVC" \
  --image="$DEV_FRONTEND_IMG" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1 \
  --timeout=60 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=5 \
  --set-env-vars="PORT=8080,BACKEND_URL=${DEV_BACKEND_URL}" \
  --project="$PROJECT_ID" --quiet

DEV_FRONTEND_URL=$(gcloud run services describe "$DEV_FRONTEND_SVC" \
  --region="$REGION" --project="$PROJECT_ID" \
  --format="value(status.url)")
ok "Dev frontend live at: $DEV_FRONTEND_URL"

log "Deploying AI Marketing Team frontend..."
gcloud run deploy "$MKT_FRONTEND_SVC" \
  --image="$MKT_FRONTEND_IMG" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1 \
  --timeout=60 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=5 \
  --set-env-vars="PORT=8080,BACKEND_URL=${MKT_BACKEND_URL}" \
  --project="$PROJECT_ID" --quiet

MKT_FRONTEND_URL=$(gcloud run services describe "$MKT_FRONTEND_SVC" \
  --region="$REGION" --project="$PROJECT_ID" \
  --format="value(status.url)")
ok "Marketing frontend live at: $MKT_FRONTEND_URL"

# ── Fix CORS: update backends with actual frontend URLs ───────────────────────
log "Updating backend CORS settings with actual frontend URLs..."

gcloud run services update "$DEV_BACKEND_SVC" \
  --region="$REGION" \
  --update-env-vars="ALLOWED_ORIGINS=${DEV_FRONTEND_URL}" \
  --project="$PROJECT_ID" --quiet
ok "Dev backend CORS updated"

gcloud run services update "$MKT_BACKEND_SVC" \
  --region="$REGION" \
  --update-env-vars="ALLOWED_ORIGINS=${MKT_FRONTEND_URL}" \
  --project="$PROJECT_ID" --quiet
ok "Marketing backend CORS updated"

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  DEPLOYMENT COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  AI Dev Team"
echo "  ├── Frontend:  $DEV_FRONTEND_URL"
echo "  └── Backend:   $DEV_BACKEND_URL"
echo ""
echo "  AI Marketing Team"
echo "  ├── Frontend:  $MKT_FRONTEND_URL"
echo "  └── Backend:   $MKT_BACKEND_URL"
echo ""
echo "  Region: $REGION (Mumbai)"
echo "  Project: $PROJECT_ID"
echo "════════════════════════════════════════════════════════════"
echo ""
warn "Note: Cloud Run uses ephemeral storage (/tmp)."
warn "Generated files and DB are lost on container restart."
warn "For persistence, add Cloud SQL (Postgres) and Cloud Storage."
echo ""
