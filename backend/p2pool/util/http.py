from io import BytesIO

from twisted.internet import reactor
from twisted.web import client
from twisted.web.http_headers import Headers

from p2pool.util.py3 import ensure_bytes


def get_page(url, method=b'GET', postdata=None, timeout=None):
    url = ensure_bytes(url, 'ascii')
    method = ensure_bytes(method, 'ascii')

    headers = Headers({})
    body = None
    if postdata is not None:
        body = client.FileBodyProducer(BytesIO(ensure_bytes(postdata)))
        headers.addRawHeader(b'content-type', b'text/plain')

    d = client.Agent(reactor).request(method, url, headers, body)
    if timeout is not None:
        d.addTimeout(timeout, reactor)
    d.addCallback(client.readBody)
    return d
