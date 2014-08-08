ansible-nested-connections
==========================

Experimental connection plugin for stacking some layers over other connection plugins

See discussion here: https://groups.google.com/forum/?utm_medium=email&utm_source=footer#!msg/ansible-project/snM7n1QGoAw/VV1KGJZQAooJ

Example usage:
some_chroot_host ansible_ssh_host=local;chroot=/path/to/chroot
