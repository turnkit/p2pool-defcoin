import os
import re
import shutil
import subprocess  # nosec B404


def _describe_from_git(root_dir):
    for executable in ('git', 'git.cmd'):
        command = shutil.which(executable)
        if command is None:
            continue
        try:
            return subprocess.check_output(  # noqa: S603  # nosec B603
                [command, 'describe', '--always', '--dirty'],
                cwd=root_dir,
                stderr=subprocess.DEVNULL,
            ).strip().decode('ascii')
        except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
            continue


def _read_git_head(git_dir):
    if not os.path.isdir(git_dir):
        return None

    with open(os.path.join(git_dir, 'HEAD'), encoding='utf-8') as head_file:
        head = head_file.read().strip()

    prefix = 'ref: '
    if not head.startswith(prefix):
        return head[:7]

    ref_path = head[len(prefix):]
    loose_ref = os.path.join(git_dir, *ref_path.split('/'))
    if os.path.exists(loose_ref):
        with open(loose_ref, encoding='utf-8') as ref_file:
            return ref_file.read().strip()[:7]

    packed_refs = os.path.join(git_dir, 'packed-refs')
    if os.path.exists(packed_refs):
        with open(packed_refs, encoding='utf-8') as packed_file:
            for line in packed_file:
                if line.startswith('#') or not line.strip():
                    continue
                sha, packed_ref = line.strip().split(' ', 1)
                if packed_ref == ref_path:
                    return sha[:7]

    return None


def _get_version():
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_root = os.path.dirname(package_root)
    root_dir = repo_root if os.path.exists(os.path.join(repo_root, '.git')) else package_root
    try:
        git_version = _describe_from_git(root_dir)
        if git_version is not None:
            return git_version

        git_dir = os.path.join(root_dir, '.git')
        git_head = _read_git_head(git_dir)
        if git_head is not None:
            return git_head

        dir_name = os.path.split(root_dir)[1]
        match = re.match('p2pool-([.0-9]+)', dir_name)
        if match:
            return match.groups()[0]

    except OSError as err:
        return f'unknown {str(err).encode("utf-8").hex()}'

    return f'unknown {os.path.split(root_dir)[1].encode("utf-8").hex()}'

__version__ = _get_version()

DEBUG = True
BENCH = False
