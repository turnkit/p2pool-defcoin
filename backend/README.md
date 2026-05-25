# Defcoin P2Pool Backend

This directory contains the Python P2Pool backend, Defcoin network parameters,
share validation, Stratum work generation, P2P protocol code, tests, and helper
scripts.

## Install

From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
python -m pip install -e backend/litecoin_scrypt
```

## Run

Use the root compatibility launcher unless you have a specific reason to call
the backend launcher directly:

```bash
python run_p2pool.py --net defcoin --help
```

The default web UI is loaded from `frontend/web-static`. A custom UI can be
provided with:

```bash
python run_p2pool.py --net defcoin --web-static /path/to/web-static ...
```

## Test and audit

```bash
python backend/dev/python3_port_compile_check.py
ruff check --select E9,F63,F7,F82 backend/p2pool backend/run_p2pool.py run_p2pool.py
cd backend && python -m twisted.trial p2pool.test.test_data p2pool.test.test_node p2pool.test.bitcoin.test_data
python backend/dev/cache_benchmark.py
pip-audit -r backend/requirements.txt
pip-audit -r backend/conf/requirements-testing.txt
pip-audit -r backend/conf/requirements-development.txt
bandit --severity-level medium -r backend/p2pool backend/run_p2pool.py run_p2pool.py -x backend/p2pool/test
```

See `../docs/TECHNICAL_GUIDE.md` for the fuller test, audit, and deployment notes.
