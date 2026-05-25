

import json
from io import BytesIO
import weakref

from twisted.internet import defer, reactor
from twisted.protocols import basic
from twisted.python import failure, log
from twisted.web import client, error
from twisted.web.http_headers import Headers

from p2pool.util import deferral, deferred_resource, memoize
from p2pool.util.py3 import ensure_bytes, ensure_text

class Error(Exception):
    def __init__(self, code, message, data=None):
        if type(self) is Error:
            raise TypeError("can't directly instantiate Error class; use Error_for_code")
        if not isinstance(code, int):
            raise TypeError('code must be an int')
        #if not isinstance(message, unicode):
        #    raise TypeError('message must be a unicode')
        self.code, self.message, self.data = code, message, data
    def __str__(self):
        return '%i %s' % (self.code, self.message) + (' %r' % (self.data, ) if self.data is not None else '')
    def _to_obj(self):
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data,
        }

@memoize.memoize_with_backing(weakref.WeakValueDictionary())
def Error_for_code(code):
    class NarrowError(Error):
        def __init__(self, *args, **kwargs):
            Error.__init__(self, code, *args, **kwargs)
    return NarrowError


class Proxy(object):
    def __init__(self, func, services=None):
        self._func = func
        self._services = [] if services is None else services
    
    def __getattr__(self, attr):
        if attr.startswith('rpc_'):
            return lambda *params: self._func('.'.join(self._services + [attr[len('rpc_'):]]), params)
        elif attr.startswith('svc_'):
            return Proxy(self._func, self._services + [attr[len('svc_'):]])
        else:
            raise AttributeError('%r object has no attribute %r' % (self.__class__.__name__, attr))

@defer.inlineCallbacks
def _handle(data, provider, preargs=(), response_handler=None):
        id_ = None
        
        try:
            try:
                try:
                    req = json.loads(data)
                except Exception:
                    raise Error_for_code(-32700)('Parse error')
                
                if 'result' in req or 'error' in req:
                    response_handler(req['id'], req['result'] if 'error' not in req or req['error'] is None else
                        failure.Failure(Error_for_code(req['error']['code'])(req['error']['message'], req['error'].get('data', None))))
                    defer.returnValue(None)
                
                id_ = req.get('id', None)
                method = req.get('method', None)
                if not isinstance(method, str):
                    raise Error_for_code(-32600)('Invalid Request')
                params = req.get('params', [])
                if not isinstance(params, list):
                    raise Error_for_code(-32600)('Invalid Request')
                
                for service_name in method.split('.')[:-1]:
                    provider = getattr(provider, 'svc_' + service_name, None)
                    if provider is None:
                        raise Error_for_code(-32601)('Service not found')
                
                method_meth = getattr(provider, 'rpc_' + method.split('.')[-1], None)
                if method_meth is None:
                    raise Error_for_code(-32601)('Method not found')
                
                result = yield method_meth(*list(preargs) + list(params))
                error = None
            except Error:
                raise
            except Exception:
                log.err(None, 'Squelched JSON error:')
                raise Error_for_code(-32099)('Unknown error')
        except Error as e:
            result = None
            error = e._to_obj()
        
        defer.returnValue(json.dumps(dict(
            jsonrpc='2.0',
            id=id_,
            result=result,
            error=error,
        )))

# HTTP

@defer.inlineCallbacks
def _http_do(url, headers, timeout, method, params):
    id_ = 0
    payload = ensure_bytes(json.dumps({
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
        'id': id_,
    }), 'utf-8')
    request_headers = dict(headers, **{'Content-Type': 'application/json'})
    agent_headers = Headers(dict(
        (ensure_bytes(k, 'ascii'), [ensure_bytes(v, 'ascii')])
        for k, v in request_headers.items()
    ))
    
    try:
        agent = client.Agent(reactor)
        response = yield agent.request(
            b'POST',
            ensure_bytes(url, 'ascii'),
            agent_headers,
            client.FileBodyProducer(BytesIO(payload)),
        )
        data = yield client.readBody(response)
    except error.Error as e:
        try:
            resp = json.loads(e.response)
        except:
            raise e
    else:
        resp = json.loads(ensure_text(data, 'utf-8'))
    
    if resp['id'] != id_:
        raise ValueError('invalid id')
    if 'error' in resp and resp['error'] is not None:
        raise Error_for_code(resp['error']['code'])(resp['error']['message'], resp['error'].get('data', None))
    defer.returnValue(resp['result'])
HTTPProxy = lambda url, headers={}, timeout=5: Proxy(lambda method, params: _http_do(url, headers, timeout, method, params))

class HTTPServer(deferred_resource.DeferredResource):
    def __init__(self, provider):
        deferred_resource.DeferredResource.__init__(self)
        self._provider = provider
    
    @defer.inlineCallbacks
    def render_POST(self, request):
        data = yield _handle(request.content.read(), self._provider, preargs=[request])
        assert data is not None
        request.setHeader('Content-Type', 'application/json')
        data = ensure_bytes(data, 'utf-8')
        request.setHeader('Content-Length', str(len(data)))
        request.write(data)

class LineBasedPeer(basic.LineOnlyReceiver):
    delimiter = b'\n'
    
    def __init__(self):
        #basic.LineOnlyReceiver.__init__(self)
        self._matcher = deferral.GenericDeferrer(max_id=2**30, func=lambda id, method, params: self.sendLine(ensure_bytes(json.dumps({
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': id,
        }), 'utf-8')))
        self.other = Proxy(self._matcher)
    
    def lineReceived(self, line):
        _handle(line, self, response_handler=self._matcher.got_response).addCallback(
            lambda line2: self.sendLine(ensure_bytes(line2, 'utf-8')) if line2 is not None else None)
