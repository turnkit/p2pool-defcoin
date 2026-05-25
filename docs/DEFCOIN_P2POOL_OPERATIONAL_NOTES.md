# Defcoin P2Pool Operational Notes

## Server fee wallet

The dc903 P2Pool server fee wallet is configured in the systemd service, not in
`p2pool/networks/defcoin.py`.

On the server, inspect it with:

```bash
systemctl cat p2pool-defcoin
```

The active service command is:

```bash
/usr/bin/python2.7 /home/dfcpool/p2pool-defcoin/run_p2pool.py --net defcoin --allow-obsolete-bitcoind -a DBbKV7upy41hV42dU895m4NcXn9AvHXUz9 -n 50.116.19.40 --bitcoind-p2p-port 10332 --fee 1.5
```

For this deployment:

- `-a DBbKV7upy41hV42dU895m4NcXn9AvHXUz9` sets the node operator/default payout
  address.
- `--fee 1.5` sets the public worker fee to 1.5%.
- In `p2pool/work.py`, the worker fee is applied by occasionally assigning a
  worker share to the node operator address instead of the miner-submitted
  username address.
- The worker fee can be checked from the web/API endpoint:

```bash
curl http://127.0.0.1:13372/fee
```

This server fee is separate from P2Pool's legacy `DONATION_SCRIPT` / developer
donation output. The legacy donation-script issue is a share-template and
coinbase-compatibility issue; changing `-a` or `--fee` does not remove that dust
output.

## Version 36 donation dust fix

Old Defcoin P2Pool shares inherited JP's P2Pool developer donation script. In
this fork it resolves to the Defcoin address
`DQ8AwqR2XJE9G5dSEfspJYH7Spre85dj6L`. The private key for that historical
destination is not available, so the one-satoshi rounding outputs are effectively
lost.

This repository fixes the issue with Defcoin P2Pool share version `36`.

- `p2pool/data.py` adds `DonationDustFixedShare`, keeps old shares verifiable,
  removes the spendable legacy donation output from new share templates, and
  adds a zero-value OP_RETURN padding output so P2Pool's coinbase hashlink still
  has a stable tail.
- `p2pool/work.py` stops recording author-donation weight once the active share
  type no longer pays the legacy donation output.
- `p2pool/data.py:get_expected_payouts` stops showing the lost-key donation
  address as the expected destination once the best share is version `36`.

This is not a Defcoin blockchain hard fork. It is a P2Pool share-template and
share-version change. Operators sharing the same Defcoin P2Pool network should
coordinate a restart/update window so their P2Pool nodes agree on version `36`.
The parent-chain Defcoin blocks remain ordinary Defcoin blocks.

Suggested operator note:

```text
I am updating the Defcoin P2Pool fork to remove the old JP P2Pool developer
donation script from newly mined templates. The on-chain address affected is
DQ8AwqR2XJE9G5dSEfspJYH7Spre85dj6L. This is not a Defcoin hard fork; it is a
P2Pool share-template/share-version update. Please pull the version that adds
DonationDustFixedShare in p2pool/data.py, restart your pool during the same
window, and keep your Defcoin parent-chain node in dual-magic compatibility mode
until older wallets have mostly upgraded.
```

## P2Pool peer handshake logging

The P2Pool peer network is separate from the Defcoin Core parent-chain peer network. A small Defcoin sharechain may have only one or two useful P2Pool peers, so peer safety is more important than aggressively reducing connection attempts.

The peer handshake logging policy is:

- Keep accepting sockets long enough to read the P2Pool `version` message and peer nonce.
- Do not reject a peer only because another connection from the same IP address already exists.
- Keep the normal established-peer log line because it records the live peer set.
- Log invalid handshakes such as too-old protocol versions, repeated version messages, or self-connections.
- For duplicate peer nonces, disconnect the duplicate after identification and rate-limit the log message to one line per host per five minutes, with suppressed-message counts summarized on the next emitted line.

This keeps useful abnormal events visible while preventing normal duplicate-connection churn from filling logs. It also avoids accidentally isolating a valid P2Pool peer on a very small network.
