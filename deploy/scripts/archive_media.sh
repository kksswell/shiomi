#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="$ROOT_DIR/backups/media"
DATE_TAG="$(date +%Y-%m-%d_%H-%M-%S)"
CONTAINER="${BACKEND_CONTAINER:-vania_sait_backend_prod}"

mkdir -p "$BACKUP_DIR"

docker cp "$CONTAINER:/app/media" "$BACKUP_DIR/media_${DATE_TAG}"
tar -czf "$BACKUP_DIR/media_${DATE_TAG}.tar.gz" -C "$BACKUP_DIR" "media_${DATE_TAG}"
rm -rf "$BACKUP_DIR/media_${DATE_TAG}"
find "$BACKUP_DIR" -type f -name 'media_*.tar.gz' -mtime +14 -delete

echo "Media archive created: $BACKUP_DIR/media_${DATE_TAG}.tar.gz"
