from p2pool.bitcoin import networks

#############################################
###  choose what network you are joining  ###
#***  listed rates are not hard set yet  ***#
#############################################

##### CPU pool is for future use for slower miners when network is larger #####
###### pool 0, CPU, <1mh
#WORKER_PORT = 13370
#BOOTSTRAP_ADDRS = ['135.148.43.187']

# pool 1, USB, 1mh to 50mh
#WORKER_PORT = 13371
#BOOTSTRAP_ADDRS = ['135.148.43.188']

# pool 2, ASIC, >50mh
WORKER_PORT = 13372
BOOTSTRAP_ADDRS = ['135.148.43.189']

BLOCK_EXPLORER_URL_PREFIX = 'https://defcoin.dc903.org/explorer/block/'
ADDRESS_EXPLORER_URL_PREFIX = 'https://defcoin.dc903.org/explorer/address/'
TX_EXPLORER_URL_PREFIX = 'https://defcoin.dc903.org/explorer/tx/'

PARENT = networks.nets['defcoin']
P2P_PORT = 1337
SHARE_PERIOD = 45 # seconds
CHAIN_LENGTH = 24*60*60//10 # shares
REAL_CHAIN_LENGTH = 24*60*60//10 # shares
TARGET_LOOKBEHIND = 15 # shares
SPREAD = 42 # blocks
MIN_TARGET = 0
MAX_TARGET = 2**256//2**20 - 1
VERSION_CHECK = lambda v: None if 160002 <= v else 'Defcoin Core version out of date. Upgrade to a compatible Defcoin Core release.'
VERSION_WARNING = lambda v: None
BLOCK_MAX_SIZE = 4000000
BLOCK_MAX_WEIGHT = 4000000
ANNOUNCE_CHANNEL = '#p2pool-dfc' #irc plugin?
IDENTIFIER = bytes.fromhex('b032d5a8c6923410')
PREFIX = bytes.fromhex('1389c1ad3ef0b9b5')

#PERSIST = True # SET THIS TO FALSE UNTIL THE SHARE CHAIN IS BOOTSTRAPPED
PERSIST = False

SOFTFORKS_REQUIRED = set(['bip65', 'csv', 'segwit'])
SEGWIT_ACTIVATION_VERSION = 15
NEW_MINIMUM_PROTOCOL_VERSION = 3301
