from ansible import constants as C
from ansible.errors import AnsibleError
from ansible.utils.plugins import connection_loader, PluginLoader


connection_layer_loader = PluginLoader(
    "ConnectionLayer",
    '',
    C.DEFAULT_CONNECTION_PLUGIN_PATH,
    'connection_plugins')


class Connection(object):
    """Connection class for wrapping ConnectionLayers around Connection"""
    has_pipelining = False  # TODO: should depend on Connection/layers

    def __init__(self, runner, host, *args, **kwargs):
        self.runner = runner
        self.host = host

        layers = []
        for raw_layer in host.split(';'):
            if '=' in raw_layer:
                layers.append(raw_layer.split('=', 1))
            else:
                layers.append((raw_layer, None))

        assert len(layers) > 1
        self.base_connection = connection_loader.get(
            layers[0][0],
            runner, layers[0][1], *args, **kwargs)

        self.connection_layers = []
        for plugin_name, layer_host in layers[1:]:
            layer = connection_layer_loader.get(
                plugin_name,
                runner, layer_host, *args, **kwargs)

            self.connection_layers.append(layer)

        # TODO: self.su_layer/self.sudo_layer

    def connect(self):
        self.base_connection.connect()
        return self

    def close(self):
        self.base_connection.close()

    def exec_command(self, command, tmp_path,
                     sudo_user=None, sudoable=False,
                     executable='/bin/sh', in_data=None,
                     su=None, su_user=None):

        if in_data:
            raise AnsibleError(
                "Internal Error: this module does not support pipelining")

        if sudoable:
            pass  # TODO: Add self.sudo_layer to layers
        if su:
            pass  # TODO: Add self.su_layer to layers

        for layer in self.connection_layers:
            command = layer.wrap_command(command)
            if tmp_path:
                tmp_path = layer.wrap_path(tmp_path)

        # TODO: what is that second returned value?
        rc, _, stdout, stderr = self.base_connection.exec_command(
            command,
            tmp_path,
            None, False, executable,
            None, None, None)

        for layer in reversed(self.connection_layers):
            rc, stdout, stderr = layer.unwrap_result(rc, stdout, stderr)

        return rc, '', stdout, stderr

    def put_file(self, local, remote):
        for layer in self.connection_layers:
            remote = layer.wrap_path(remote)

        return self.base_connection.put_file(local, remote)

    def fetch_file(self, remote, local):
        for layer in self.connection_layers:
            remote = layer.wrap_path(remote)

        return self.base_connection.fetch_file(remote, local)
