import os
import platform

from twisted.internet import defer

from .. import data, helper
from p2pool.util import pack

SYMBOL = 'DFC'
POW_FUNC = lambda data: pack.IntType(256).unpack(__import__('ltc_scrypt').getPoWHash(data))
BLOCK_PERIOD = 150 # s
ADDRESS_VERSION = 30
ADDRESS_P2SH_VERSION = 50
HUMAN_READABLE_PART = 'dfc'

CONF_FILE_FUNC = lambda: os.path.join(
	os.path.join(os.environ['APPDATA'], 'Defcoin') if platform.system() == 'Windows' else
	os.path.expanduser('~/Library/Application Support/Defcoin/') if platform.system() == 'Darwin' else
	os.path.expanduser('~/.defcoin'),
'defcoin.conf')

P2P_PORT = 1337
LEGACY_P2P_PREFIX = bytes.fromhex('fbc0b6db')
NEW_P2P_PREFIX = bytes.fromhex('defc014e')
# MAGIC_BYTES_2026_LEGACY_KILL_SWITCH:
# Keep DEFCOIN_P2POOL_USE_NEW_MAGIC unset/0 while the local defcoind service is
# running legacy outbound magic. Set it to 1 when defcoind is switched to
# -usenewdefcoinmagic=1. Later, remove LEGACY_P2P_PREFIX from P2P_PREFIXES.
P2P_PREFIX = NEW_P2P_PREFIX if os.environ.get('DEFCOIN_P2POOL_USE_NEW_MAGIC', '').lower() in ('1', 'true', 'yes', 'on') else LEGACY_P2P_PREFIX
P2P_PREFIXES = (P2P_PREFIX, LEGACY_P2P_PREFIX) if P2P_PREFIX == NEW_P2P_PREFIX else (P2P_PREFIX, NEW_P2P_PREFIX)
RPC_PORT = 1335
RPC_CHECK = defer.inlineCallbacks(lambda bitcoind: defer.returnValue(
	(yield helper.check_block_header(bitcoind, '192047379f33ffd2bbbab3d53b9c4b9e9b72e48f888eadb3dcf57de95a6038ad')) and # genesis block
	(yield helper.check_block_header(bitcoind, '2226f88034369cf9d638b023739a54b42f3f51cd43f7859beb1041ba7d5d8cf4')) and # genesis block
	(yield bitcoind.rpc_getblockchaininfo())['chain'] != 'test'
))

BLOCK_EXPLORER_URL_PREFIX = 'https://defcoin.dc903.org/explorer/block/'
ADDRESS_EXPLORER_URL_PREFIX = 'https://defcoin.dc903.org/explorer/address/'
TX_EXPLORER_URL_PREFIX = 'https://defcoin.dc903.org/explorer/tx/'

SUBSIDY_FUNC = lambda height: 50*100000000 >> (height + 1)//840000
SUBSIDY_DECIMAL = 1e-8
DUST_THRESHOLD = 0.03e8
SANE_TARGET_RANGE = (2**256//1000000000 - 1, 2**256//1000 - 1)
DUMB_SCRYPT_DIFF = 2**16
