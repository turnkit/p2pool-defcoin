# Defcoin P2Pool Provenance and Technical Comparison Report

Date: 2026-05-22

## Executive Summary

The live `defcoin.dc903.org` p2pool service has two different provenance layers:

1. Direct Git source for the server checkout: the server's `.git/config` points at the old `charlesrocket/p2pool-defcoin` URL, which GitHub now redirects to the canonical `hellbyte/p2pool-defcoin` repository.
2. Older upstream code lineage: that Defcoin p2pool repository appears to be derived from the Python 2 / `jtoomim/p2pool` era of P2Pool, based on protocol/share-version markers and module layout.

The live server checkout identifies its immediate upstream remote as:

- Upstream Defcoin fork: `https://github.com/charlesrocket/p2pool-defcoin`
- GitHub redirect/current owner: `https://github.com/hellbyte/p2pool-defcoin`
- Upstream commit used by the server checkout: `dc1b4af980cb6d662069fd302651b50997a8aa8c`
- Commit subject: `cleared up CPU pool instructions to use USB`
- Upstream default branch: `master`
- Upstream tags: none found in the server checkout

That repository is not marked by GitHub as a formal fork, so GitHub cannot prove a formal fork relationship to `jtoomim/p2pool`. By code lineage, however, it is a Defcoin adaptation of the P2Pool Python 2 lineage and most closely matches the `jtoomim/p2pool` era rather than the current `p2pool/p2pool` tree. The strongest version markers are:

- P2Pool protocol version: `3501`
- Current share format: `PaddingBugfixShare.VERSION = 35`
- SegWit share support: `SegwitMiningShare.VERSION = 34`
- Live server p2pool sub-version style: `/P2Pool:dc1b4af-dirty/` before these changes are committed

For GitHub traceability, `turnkit/p2pool-defcoin` is intended to carry the current dc903 live-server implementation as a normal fork-style repository. The first Turnkit commit after the upstream baseline records the live server changes plus this report, so GitHub can show the difference between the original Defcoin p2pool code and the currently deployed dc903 implementation without asking the archived/original upstream to accept a pull request.

## Lineage Block Overview

### 1. Original P2Pool Lineage

`p2pool/p2pool` is the original project lineage for peer-to-peer mining pool software. It provides the core architecture: a decentralized p2pool sharechain, peer protocol, share validation, work generation, and a small web/status UI.

### 2. jtoomim-Era Python 2 P2Pool

The Defcoin fork's core files align much more closely with `jtoomim/p2pool` than with the current `p2pool/p2pool` repository. The matching markers include protocol version `3501`, share versions `35/34/33/32/17`, SegWit-aware share handling, and the same broad module layout. This is a code-lineage finding, not the server's direct Git remote.

### 3. hellbyte/charlesrocket Defcoin Fork

`hellbyte/p2pool-defcoin` adds Defcoin as both:

- a parent blockchain network in `p2pool/bitcoin/networks/defcoin.py`
- a p2pool sharechain network in `p2pool/networks/defcoin.py`

It changes coin/network constants, ports, block explorer links, bootstrap nodes, and worker port selection for Defcoin mining.

### 4. dc903 Live Server Branch

The dc903 live branch adds operational fixes and the 2026 Defcoin network transition work:

- dual legacy/new p2pool magic support
- per-peer reply magic selection
- Defcoin Core Nu `getblocktemplate` rule negotiation compatibility
- current `defcoin.dc903.org` explorer links
- selected ASIC worker pool settings
- pidfile guard in `run_p2pool.py`
- a small p2pool bug fix in ban-score decay
- customized web UI assets

## Detailed Modular Overview

### Repository and Versioning

The upstream Defcoin p2pool repository does not use a semantic release tag. Runtime versioning comes from `p2pool.__version__`, which calls `git describe --always --dirty`. On the live server, local changes make the runtime identify as `dc1b4af-dirty` until those changes are committed.

The committed Turnkit tree is intended to remove that ambiguity: it records the live server changes and lets future builds identify by a real repository commit hash instead of an untracked dirty state.

### Parent Blockchain Network: `p2pool/bitcoin/networks/defcoin.py`

This module teaches p2pool how to talk to Defcoin Core / defcoind as the parent blockchain.

Defcoin-specific behavior from upstream Defcoin fork:

- `SYMBOL = 'DFC'`
- scrypt proof-of-work through `ltc_scrypt.getPoWHash`
- `BLOCK_PERIOD = 150`
- address version `30`
- P2SH version `50`
- default p2p port `1337`
- default RPC port `1335`
- Defcoin genesis/block-header checks
- Defcoin subsidy and difficulty constants

Current dc903 additions:

- Defines `LEGACY_P2P_PREFIX = fbc0b6db`.
- Defines `NEW_P2P_PREFIX = defc014e`.
- Selects preferred outbound p2pool magic through `DEFCOIN_P2POOL_USE_NEW_MAGIC`.
- Accepts both legacy and new prefixes during the transition.
- Updates block/address/transaction explorer links to `https://defcoin.dc903.org/explorer/...`.

### P2Pool Sharechain Network: `p2pool/networks/defcoin.py`

This module defines the Defcoin p2pool sharechain rules and public mining endpoints.

Defcoin-specific behavior from upstream Defcoin fork:

- parent network is `defcoin`
- p2pool peer port is `1337`
- share period is `45` seconds
- chain length is one day of shares
- Defcoin p2pool identifier and prefix
- SegWit-related share rules
- optional pool tiers for CPU, USB, and ASIC miners

Current dc903 additions:

- Enables the ASIC worker port `13372`.
- Uses bootstrap address `135.148.43.189`.
- Points explorer URLs at `defcoin.dc903.org`.

### P2P Wire Protocol: `p2pool/util/p2protocol.py`

This is the generic packet framing layer used by p2pool peers.

Upstream behavior:

- One network prefix is expected.
- Incoming stream scanning waits for exactly that prefix.
- Replies naturally use that same configured prefix.

Current dc903 addition:

- The protocol can accept a tuple/list of prefixes.
- On inbound data, it detects which accepted prefix was actually used by the peer.
- It stores that prefix as the active per-connection `_message_prefix`.
- Replies on that connection are serialized with the same prefix the peer used.

This is important because accepting both old and new magic is not enough. A legacy peer must receive legacy replies, while a new Defcoin-magic peer must receive new Defcoin-magic replies.

### Parent Chain P2P: `p2pool/bitcoin/p2p.py`

This module handles p2pool's direct connection to the parent daemon's p2p interface. The dc903 changes are minimal but support the multi-prefix behavior by passing the parent network prefix configuration into the generic protocol layer.

### Parent Chain Work RPC: `p2pool/bitcoin/helper.py`

This module requests parent-chain work from Defcoin Core / defcoind.

Current dc903 addition:

- Calls `getblocktemplate` with both `segwit` and `mweb` in the rule list.

Plain English impact: this does not activate a new consensus rule or hard fork Defcoin. It only acknowledges rule names the modern Defcoin Core Nu daemon may include in `getblocktemplate`, preventing the old P2Pool code from failing against the newer backend.

### Share Data and Serialization: `p2pool/data.py`

The Defcoin server remains on the jtoomim-era share formats:

- current/padding bugfix share: version `35`
- SegWit mining share: version `34`
- new share: version `33`
- pre-SegWit share: version `32`
- legacy share: version `17`

Current dc903 addition:

- Documents and patches the legacy donation-script situation. Share version `36`
  removes the spendable lost-key donation-address output from newly mined
  templates while preserving validation for older shares.

### Peer Management: `p2pool/p2p.py`

Current dc903 bug fix:

- Corrects `forgive_transgressions()` from `self.banscore` to `self.banscores`.

Plain English impact: the old code referenced the wrong attribute while decaying peer ban scores. The fix makes ban-score forgiveness operate on the actual dictionary used elsewhere in the class.

### Launcher: `run_p2pool.py`

Current dc903 operational addition:

- Adds `/tmp/p2pool.pid` guard.
- Refuses to start a second copy when the pidfile exists.
- Removes the pidfile on normal exit through `finally`.

Plain English impact: the systemd service is less likely to accidentally run duplicate p2pool workers against the same sharechain and ports.

### Web UI: `web-static/`, `web-static-orig/`, and `p2pool-ui-punchy/`

The live server replaces the stock p2pool web files with a customized UI.

Current dc903 UI changes include:

- preserving original stock files under `web-static-orig/`
- replacing `web-static/index.html`
- adding Bootstrap/Highcharts-style assets under `web-static/css/`, `web-static/js/`, and `web-static/img/`
- adding `p2pool-ui-punchy/` as a staged UI source/reference directory
- deleting old stock `graphs.html`, `share.html`, and bundled `d3.v2.min.js` from the active web root

Plain English impact: the p2pool web surface is operator-facing and customized for the Defcoin pool rather than stock P2Pool.

## Technical Comparison Summary

| Area | Original/jtoomim P2Pool | hellbyte Defcoin fork | dc903 live branch |
| --- | --- | --- | --- |
| Parent chain | Bitcoin/Litecoin/etc. adapters | Adds Defcoin parent adapter | Updates Defcoin explorer links and magic migration behavior |
| Mining network | General p2pool sharechain networks | Adds Defcoin sharechain constants and pool tiers | Enables ASIC worker port and dc903 bootstrap behavior |
| Wire magic | Single configured prefix | Defcoin legacy prefix `fbc0b6db` | Dual prefix support: `fbc0b6db` and `defc014e` |
| Per-peer reply magic | Not needed with one prefix | Not implemented | Replies with the same prefix the peer used |
| Work RPC | Legacy `getblocktemplate` rules | Legacy `getblocktemplate` rules | Declares `segwit` and `mweb` rules for Defcoin Core Nu compatibility |
| Version identity | Dynamic git hash | `dc1b4af` upstream hash | Previously dirty on server; branch commit documents changes |
| Web UI | Stock P2Pool UI | Some Defcoin README/UI references | Customized active UI with preserved stock backup |
| Runtime guard | Direct run script | Direct run script | pidfile guard against duplicate process starts |

## What Is Not Changed

The dc903 p2pool branch does not change Defcoin consensus rules. It does not
change Defcoin block validation, transaction validation, or wallet rules. It
does change P2Pool share-template behavior in version `36` by removing the
legacy donation-address dust output, so cooperating Defcoin P2Pool operators
should update together.

## Evidence Captured

Local comparison artifacts were used to prepare this report and are intentionally
not published in the repository.

Server source path used for comparison:

- `/home/dfcpool/p2pool-defcoin`
