#!/usr/bin/env bash
set -euo pipefail

echo "Installing quicktype (npm global) and datamodel-codegen (pip)..."

# npm install quicktype CLI (global)
if command -v npm >/dev/null 2>&1; then
  npm install -g quicktype
else
  echo "npm not found: please install Node.js to get quicktype"
fi

# Python tool
python3 -m pip install --user datamodel-code-generator "pydantic[dotenv]" jsonschema
