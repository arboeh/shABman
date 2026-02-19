#!/bin/bash
# scripts/test-local.sh
set -e

VENV=".venv-test"

rm -rf "$VENV"
python3 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip -q
"$VENV/bin/pip" install -e ".[test]"
"$VENV/bin/pytest" tests/ -v --cov=custom_components.shabman --cov-report=term-missing
