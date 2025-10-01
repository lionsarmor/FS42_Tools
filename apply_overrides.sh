#!/bin/bash
# apply_overrides.sh
# Copy override files back into the official FieldStation42 repo

set -e

BASE_DIR="$(dirname "$0")"
TARGET_DIR="$BASE_DIR/FieldStation42"

echo "[*] Applying overrides to FieldStation42..."

# field_player.py
if [ -f "$BASE_DIR/overrides/field_player.py" ]; then
  cp "$BASE_DIR/overrides/field_player.py" "$TARGET_DIR/field_player.py"
  echo "  -> Applied override: field_player.py"
fi

# fs42/osd/main.py
if [ -f "$BASE_DIR/overrides/fs42/osd/main.py" ]; then
  cp "$BASE_DIR/overrides/fs42/osd/main.py" "$TARGET_DIR/fs42/osd/main.py"
  echo "  -> Applied override: fs42/osd/main.py"
fi

echo "[*] Done. Overrides applied."
