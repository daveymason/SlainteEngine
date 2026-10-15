#!/usr/bin/env bash
# =============================================================================
# SLAINTE-ENGINE: END-TO-END PIPELINE VERIFICATION TEST RUNNER
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "================================================================="
echo "  SLAINTE-ENGINE: Autonomous Clinical AI Interoperability Appliance"
echo "  Running End-to-End Pipeline Verification..."
echo "================================================================="

cd "${ROOT_DIR}"

# Ensure virtualenv or system python is available
PYTHON_BIN="python3"
if [ -f "${ROOT_DIR}/../Patient-Dashboard-htmx-python-fhir/.venv/bin/python" ]; then
    PYTHON_BIN="${ROOT_DIR}/../Patient-Dashboard-htmx-python-fhir/.venv/bin/python"
elif [ -f "${ROOT_DIR}/../OCR2FHIR/.venv/bin/python" ]; then
    PYTHON_BIN="${ROOT_DIR}/../OCR2FHIR/.venv/bin/python"
fi

echo "Using Python executable: ${PYTHON_BIN}"
"${PYTHON_BIN}" "${SCRIPT_DIR}/test_pipeline.py"

echo ""
echo "================================================================="
echo "  VERIFICATION TEST COMPLETED SUCCESSFULLY!"
echo "================================================================="
