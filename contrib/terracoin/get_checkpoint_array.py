#!/usr/bin/env python3
from json import loads, dumps
from sys import exit, argv
import requests

if len(argv) < 3:
    print('Arguments: <rpc_username> <rpc_password> [<rpc_port>]')
    exit(1)

### START FROM ELECTRUM

def bits_to_target(bits):
    bitsN = (bits >> 24) & 0xff
    if not (0x03 <= bitsN <= 0x1e):
        raise BaseException("First part of bits should be in [0x03, 0x1e]")
    bitsBase = bits & 0xffffff
    if not (0x8000 <= bitsBase <= 0x7fffff):
        raise BaseException("Second part of bits should be in [0x8000, 0x7fffff]")
    return bitsBase << (8 * (bitsN-3))

bfh = bytes.fromhex

def bh2u(x: bytes) -> str:
    """
    str with hex representation of a bytes-like object

    >>> x = bytes((1, 2, 10))
    >>> bh2u(x)
    '01020A'
    """
    return x.hex()

def rev_hex(s: str) -> str:
    return bh2u(bfh(s)[::-1])


def int_to_hex(i: int, length: int=1) -> str:
    """Converts int to little-endian hex string.
    `length` is the number of bytes available
    """
    if not isinstance(i, int):
        raise TypeError('{} instead of int'.format(i))
    range_size = pow(256, length)
    if i < -(range_size//2) or i >= range_size:
        raise OverflowError('cannot convert int {} to hex ({} bytes)'.format(i, length))
    if i < 0:
        # two's complement
        i = range_size + i
    s = hex(i)[2:].rstrip('L')
    s = "0"*(2*length - len(s)) + s
    return rev_hex(s)

def serialize_header(header_dict: dict) -> str:
    s = int_to_hex(header_dict['version'], 4) \
        + rev_hex(header_dict['prev_block_hash']) \
        + rev_hex(header_dict['merkle_root']) \
        + int_to_hex(int(header_dict['timestamp']), 4) \
        + int_to_hex(int(header_dict['bits']), 4) \
        + int_to_hex(int(header_dict['nonce']), 4)
    return s

### END FROM ELECTRUM

def jsontoheader(header_json: dict, height: int) -> dict:
    h = {}
    h['version'] = header_json['version']
    h['prev_block_hash'] = header_json['previousblockhash']
    h['merkle_root'] = header_json['merkleroot']
    h['timestamp'] = header_json['time']
    h['bits'] = int(header_json['bits'], 16)
    h['nonce'] = header_json['nonce']
    h['block_height'] = height
    return h

def rpc(_session, method, *params):
    _headers = {'content-type': 'application/json'}
    _payload = dumps({ "jsonrpc": "2.0", "method": method, "params": list(params) })
    tries = 5
    hadConnectionFailures = False

    username = argv[1]
    password = argv[2]
    port = 13332
    if len(argv) > 3:
        port = argv[3]
    url = f'http://{username}:{password}@127.0.0.1:{port}/'
    while True:
        try:
            response = _session.post(url, headers=_headers, data=_payload)
        except requests.exceptions.ConnectionError:
            tries -= 1
            if tries == 0:
                raise Exception('Failed to connect for remote procedure call.')
            hadFailedConnections = True
            print(f'Couldn\'t connect for remote procedure call, will sleep for five seconds and then try again ({tries} more tries)')
            time.sleep(10)
        else:
            if hadConnectionFailures:
                print('Connected for remote procedure call after retry.')
            break
    if not response.status_code in (200, 500):
        raise Exception(f'RPC connection failure: {str(response.status_code)} {response.reason}')
    responseJSON = response.json()
    if 'error' in responseJSON and responseJSON['error'] != None:
        reserror = str(responseJSON['error'])
        raise Exception(f'Error in RPC call: {reserror}')
    return responseJSON['result']

# Electrum checkpoints are blocks 2015, 2015 + 2016, 2015 + 2016*2, ...
i = 2015
INTERVAL = 2016

checkpoints = []
_session = requests.Session()
block_count = int(rpc(_session, 'getblockcount'))
print('Blocks: {}'.format(block_count))
while True:
    h = rpc(_session, 'getblockhash', i)
    block = rpc(_session, 'getblock', h)

    prevblocks = []
    for p in range(25):
        p = i - p
        ph = rpc(_session, 'getblockhash', p)
        phdr = jsontoheader(rpc(_session, 'getblockheader', ph), p)
        prevblocks.append([
            p,
            serialize_header(phdr)
        ])

    checkpoints.append([
        block['hash'],
        bits_to_target(int(block['bits'], 16)),
        prevblocks
    ])

    i += INTERVAL
    if i > block_count:
        print('Done.')
        break

with open('checkpoints_output.json', 'w+') as f:
    f.write(dumps(checkpoints, indent=4, separators=(',', ':')))
