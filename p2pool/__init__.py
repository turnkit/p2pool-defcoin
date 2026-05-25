import os
import re
import traceback
import subprocess

def _get_version():
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            return subprocess.check_output(['git', 'describe', '--always', '--dirty'], cwd=root_dir).strip().decode('ascii')  # noqa: S603
        except:
            pass
        try:
            return subprocess.check_output(['git.cmd', 'describe', '--always', '--dirty'], cwd=root_dir).strip().decode('ascii')  # noqa: S603
        except:
            pass
        
        git_dir = os.path.join(root_dir, '.git')
        if os.path.exists(git_dir):
            if os.path.isdir(git_dir):
                head = open(os.path.join(git_dir, 'HEAD')).read().strip()
                prefix = 'ref: '
                if head.startswith(prefix):
                    path = head[len(prefix):].split('/')
                    return open(os.path.join(git_dir, *path)).read().strip()[:7]
                else:
                    return head[:7]
        
        dir_name = os.path.split(root_dir)[1]
        match = re.match('p2pool-([.0-9]+)', dir_name)
        if match:
            return match.groups()[0]
        
        return 'unknown %s' % (dir_name.encode('utf-8').hex(),)
    except Exception as e:
        traceback.print_exc()
        return 'unknown %s' % (str(e).encode('utf-8').hex(),)

__version__ = _get_version()

DEBUG = True
BENCH = False
