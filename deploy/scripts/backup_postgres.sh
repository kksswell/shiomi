#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="$ROOT_DIR/backups/postgres"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
DATE_TAG="$(date +%Y-%m-%d_%H-%M-%S)"

mkdir -p "$BACKUP_DIR"
cd "$ROOT_DIR"

source .env

docker compose -f "$COMPOSE_FILE" exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists > "$BACKUP_DIR/${POSTGRES_DB}_${DATE_TAG}.sql"
gzip -9 "$BACKUP_DIR/${POSTGRES_DB}_${DATE_TAG}.sql"
find "$BACKUP_DIR" -type f -name '*.sql.gz' -mtime +14 -delete

echo "PostgreSQL backup created: $BACKUP_DIR/${POSTGRES_DB}_${DATE_TAG}.sql.gz"
