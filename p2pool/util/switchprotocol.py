from twisted.internet import protocol

class FirstByteSwitchProtocol(protocol.Protocol):
    p = None
    def dataReceived(self, data):
        if self.p is None:
            if not data: return
            serverfactory = self.factory.first_byte_to_serverfactory.get(data[0], self.factory.default_serverfactory)
            self.p = serverfactory.buildProtocol(self.transport.getPeer())
            self.p.makeConnection(self.transport)
        self.p.dataReceived(data)
    def connectionLost(self, reason):
        if self.p is not None:
            self.p.connectionLost(reason)

class FirstByteSwitchFactory(protocol.ServerFactory):
    protocol = FirstByteSwitchProtocol
    
    def __init__(self, first_byte_to_serverfactory, default_serverfactory):
        self.first_byte_to_serverfactory = dict(
            (self._normalize_first_byte(first_byte), serverfactory)
            for first_byte, serverfactory in first_byte_to_serverfactory.items())
        self.default_serverfactory = default_serverfactory

    @staticmethod
    def _normalize_first_byte(first_byte):
        if isinstance(first_byte, int):
            return first_byte
        if isinstance(first_byte, bytes):
            if len(first_byte) != 1:
                raise ValueError('first-byte switch keys must be exactly one byte')
            return first_byte[0]
        if isinstance(first_byte, str):
            if len(first_byte) != 1:
                raise ValueError('first-byte switch keys must be exactly one character')
            return ord(first_byte)
        raise TypeError('unsupported first-byte switch key type: %s' % (type(first_byte).__name__,))
    
    def startFactory(self):
        for f in list(self.first_byte_to_serverfactory.values()) + [self.default_serverfactory]:
            f.doStart()
    
    def stopFactory(self):
        for f in list(self.first_byte_to_serverfactory.values()) + [self.default_serverfactory]:
            f.doStop()
