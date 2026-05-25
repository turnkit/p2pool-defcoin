# Defcoin P2Pool Python 3 Resource Comparison

Date: 2026-05-25

This report records a live dc903 comparison between the saved Python 2 P2Pool
service and the Python 3 port. It is intended to document the operational
reason for moving to Python 3 and the observed runtime cost on the current
server.

## Method

- Host: dc903 Defcoin P2Pool deployment.
- Process measured: `p2pool-defcoin.service`.
- Python 2 sample:
  - Restored the saved Python 2 systemd service file.
  - Warmed up for about 90 seconds.
  - Took 30 samples, one every 30 seconds.
- Python 3 sample:
  - Restored the Python 3 systemd service file.
  - Warmed up for about 90 seconds.
  - Took 30 samples, one every 30 seconds.
- The service was restored to Python 3 after the comparison.
- CPU data uses `ps` process `%CPU`, which is a lifetime average since process
  start. This makes early startup cost visible and means CPU should be read as
  approximate, not as a precise steady-state benchmark.
- Memory data includes RSS from `ps` and `MemoryCurrent` from systemd cgroup
  accounting.

## Results

| Runtime | Version | Samples | Avg CPU | CPU Range | Avg RSS | RSS Range | Avg cgroup MemoryCurrent | Avg miners |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Python 2 | `dc1b4af-dirty` | 30 | 8.96% | 4.00% to 31.40% | 230,129 KB | 229,756 KB to 230,348 KB | 236,736 KB | 1.00 |
| Python 3 | `a85174d` | 30 | 9.30% | 3.90% to 33.40% | 202,083 KB | 200,416 KB to 202,548 KB | 188,193 KB | 1.87 |

Python 3 used about 28 MB less RSS and about 48 MB less cgroup-accounted
memory in this live sample. CPU was effectively similar within the quality of
this measurement; the Python 3 half had more miners connected on average and a
slightly different pool hash-rate window.

## Live Health Observations

After the comparison, the service was restored to Python 3 and verified:

- `p2pool-defcoin.service` was active and running.
- `/web/version` reported `a85174d`.
- Listening sockets were open on:
  - P2Pool peer port `1337`
  - Stratum port `13372`
- Both known miner addresses authorized after restart.
- No persistent Python traceback, `TypeError`, generic `Exception`, or `ERROR`
  lines were found in the reviewed journal window.

Observed issues to keep watching:

- A startup-only burst of `Error when requesting noncached value` lines appeared
  after the restart. This was not observed as a repeating runtime failure, but
  the previous log line did not include enough detail. The Python 3 branch now
  logs the cache key, exception type, message, and traceback to make any future
  recurrence actionable.
- The tiny current sharechain can show `Previous share's timestamp is ... old`
  warnings after restart or sparse share production. This is not by itself a
  Python 3 failure, but it is a useful reminder that Defcoin P2Pool currently
  has very few peers and miners.
- Self-peer detection is working and bans this node's own reflected P2Pool
  connection attempts.

## Security And Safety Conclusion

Even if CPU were only equal, Python 3 is materially better for security and
maintenance:

- Python 2.7 is end-of-life and no longer receives upstream security fixes.
- The Python 3 runtime dependencies were checked with `pip-audit`; no known
  vulnerabilities were reported for runtime, test, or development requirement
  files.
- `pip list --outdated` showed no current Python package updates in the local
  quality environment at the time of the check.
- Web static dependencies were checked with `retire`; no vulnerable web assets
  were reported after the dashboard dependency refresh.
- The Python 3 branch keeps the existing Defcoin P2Pool sharechain behavior
  while allowing modern dependency audits, linting, and security hardening.
