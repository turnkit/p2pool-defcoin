# Defcoin P2Pool Frontend

This directory contains web assets served by the backend.

- `web-static/` is the active bundled UI.
- `web-static-orig/` preserves the stock P2Pool UI for reference.
- `p2pool-ui-punchy/` is retained as a reference/staging source for alternate
  UI work.

The backend can serve a completely different static frontend:

```bash
python run_p2pool.py --net defcoin --web-static /path/to/custom/web-static ...
```

A custom frontend should treat the backend HTTP/API endpoints as the contract.
The bundled UI is useful as a working example, but it is not required for the
pool backend to mine shares or serve Stratum miners.
