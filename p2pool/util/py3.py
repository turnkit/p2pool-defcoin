import binascii


def ensure_bytes(value, encoding='latin1'):
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, str):
        return value.encode(encoding)
    raise TypeError('expected bytes-like value, got %s' % (type(value).__name__,))


def ensure_text(value, encoding='ascii'):
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode(encoding)
    raise TypeError('expected text-like value, got %s' % (type(value).__name__,))


def bchr(value):
    return bytes((value,))


def bord(value):
    if isinstance(value, int):
        return value
    if isinstance(value, (bytes, bytearray)):
        if len(value) != 1:
            raise ValueError('expected one byte')
        return value[0]
    return ord(value)


def hex_to_bytes(value):
    return binascii.unhexlify(ensure_bytes(value, 'ascii'))


def bytes_to_hex(value):
    return binascii.hexlify(ensure_bytes(value)).decode('ascii')
