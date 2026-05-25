import importlib
import pkgutil

nets = dict((name, importlib.import_module('.' + name, __name__))
    for module_loader, name, ispkg in pkgutil.iter_modules(__path__))
for net_name, net in nets.items():
    net.NAME = net_name
