#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCHEMA_DIR="${ROOT_DIR}/schemas"
OUT_TS="${ROOT_DIR}/ts"
OUT_PY="${ROOT_DIR}/py/shared_models"


# Tools (assume available on PATH):
# - quicktype (npm)  -> generates TypeScript
# - datamodel-codegen -> generates pydantic models for Python

mkdir -p "${OUT_TS}"
mkdir -p "${OUT_PY}"


echo "Generating TypeScript models (quicktype)..."
for schema in "${SCHEMA_DIR}"/*.json; do
  base="$(basename "${schema%.schema.json}")"   # e.g. user
  out_file="${OUT_TS}/${base}.ts"
  echo "  - ${schema} -> ${out_file}"
  quicktype --lang typescript --src "${schema}" -o "${out_file}" --just-types
done

echo "Generating Python Pydantic models (datamodel-codegen)..."
for schema in "${SCHEMA_DIR}"/*.json; do
  base="$(basename "${schema%.schema.json}")"
  out_file="${OUT_PY}/${base}.py"
  echo "  - ${schema} -> ${out_file}"
  # Use globally installed datamodel-codegen (installed via pip in Dockerfile)
  datamodel-codegen --input "${schema}" --input-file-type jsonschema \
      --output "${out_file}" --use-default --force \
      --output-model-type pydantic_v2.BaseModel
done


cd "${OUT_PY}" || exit 1


echo "Formatting outputs (optional):"
# if you want to run formatting tools
command -v prettier >/dev/null 2>&1 && prettier --write "${OUT_TS}"/*.ts || true
command -v black >/dev/null 2>&1 && black "${OUT_PY}" || true

echo "Done. Generated files are in ${OUT_TS} and ${OUT_PY}"
