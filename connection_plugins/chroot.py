import pipes
import os


class ConnectionLayer(object):
    def __init__(self, runner, host, *args, **kwargs):
        self.runner = runner
        self.chroot = host

    def wrap_command(self, command):
        """Wraps the command in chroot"""
        return 'chroot {path} /bin/sh -c {command}'.format(
            path=pipes.quote(self.chroot),
            command=pipes.quote(command))

    def unwrap_result(self, rc, stdout, stderr):
        """Takes whatever the wrapped command returned
        after being run by the base connection plugin,
        and returns a new tuple of (rc, stdout, stderr)"""
        # TODO: tell the difference between chroot failing and command failing
        return rc, stdout, stderr

    def wrap_path(self, path):
        """Takes a path inside container/chroot/jail and translates
        it into host path."""
        assert path.startswith('/'), "TODO: relative paths"
        return os.path.join(self.chroot, path[1:])
