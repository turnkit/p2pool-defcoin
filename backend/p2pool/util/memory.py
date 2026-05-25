import os
import platform

_scale = {'kB': 1024, 'mB': 1024*1024,
    'KB': 1024, 'MB': 1024*1024}

def resident():
    if platform.system() == 'Windows':
        from wmi import WMI
        w = WMI('.')
        # Bandit B608: pid is process-local integer data, not user input.
        result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % int(os.getpid()))  # nosec B608
        return int(result[0].WorkingSet)
    try:
        with open('/proc/%d/status' % os.getpid()) as f:
            v = f.read()
    except OSError:
        import resource
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if platform.system() == 'Darwin':
            return rss
        return rss * 1024

    i = v.index('VmRSS:')
    v = v[i:].split(None, 3)
    #assert len(v) == 3, v
    return float(v[1]) * _scale[v[2]]
