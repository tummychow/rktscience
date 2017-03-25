import subprocess
import tempfile
import json

class ACBuild:
    def __init__(self, output_path,
        dry_run=False,
        binary='acbuild',
        debug=False,
        history=True,
        work_path=None,
        insecure=False,
        build_mode='appc',
        initial_aci=None,
        overwrite=False,
    ):
        # global options
        self.dry_run = dry_run
        self.binary = binary
        self.debug = debug
        self.work_path = work_path
        self.history = history

        # begin/run options
        self.insecure = insecure

        # begin options
        self.build_mode = build_mode
        self.initial_aci = initial_aci

        # write options
        self.output_path = output_path
        self.overwrite = overwrite

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                self.write()
        finally:
            # TODO: what if end fails while we're in the middle
            # of another exception?
            self.end()
        # if we did not raise any exceptions, then resume
        # handling of the existing exception (if any)
        return False

    def _acinvoke(self, *args):
        cmd = [self.binary]
        if self.debug:
            cmd.append('--debug')
        if not self.history:
            cmd.append('--no-history')
        if self.work_path:
            cmd.append(f'--work-path={self.work_path}')
        cmd.extend(args)
        if self.dry_run:
            print(cmd)
        else:
            subprocess.run(cmd, check=True)

    def begin(self):
        args = ['begin']
        if self.build_mode != 'appc':
            args.append(f'--build-mode={self.build_mode}')
        if self.insecure:
            args.append('--insecure')
        if self.initial_aci:
            args.append(self.initial_aci)
        self._acinvoke(*args)

    def write(self):
        args = ['write']
        if self.overwrite:
            args.append('--overwrite')
        args.append(self.output_path)
        self._acinvoke(*args)
        # TODO: implement signing, since acbuild has
        # removed this from its write command

    def end(self):
        self._acinvoke('end')

    def annotation_add(self, name, val):
        self._acinvoke('annotation', 'add', name, val)

    def annotation_rm(self, name):
        self._acinvoke('annotation', 'remove', name)

    def copy(self, src, dst):
        self._acinvoke('copy', src, dst)

    def copy_to_dir(self, srcs, dst):
        self._acinvoke('copy-to-dir', *srcs, dst)

    def dep_add(self, img, img_id=None, size=None, labels={}):
        cmd = ['dependency', 'add']
        if img_id:
            cmd.append(f'--image-id={img_id}')
        if size:
            cmd.append(f'--size={size}')
        for label, value in labels.items():
            cmd.append(f'--label={label}={value}')
        cmd.append(img)
        self._acinvoke(*cmd)

    def dep_rm(self, img):
        self._acinvoke('dependency', 'remove', img)

    def env_add(self, name, value):
        self._acinvoke('environment', 'add', name, value)

    def env_rm(self, name):
        self._acinvoke('environment', 'remove', name)

    def isolator_add(self, name, obj):
        # TODO: if in dry_run, print the json and don't make the tmpfile
        with tempfile.NamedTemporaryFile(mode='w+t') as isolator:
            json.dump(obj, isolator)
            isolator.flush()
            self._acinvoke('isolator', 'add', name, isolator.name)

    def isolator_rm(self, name):
        self._acinvoke('isolator', 'remove', name)

    def label_add(self, name, value):
        self._acinvoke('label', 'add', name, value)

    def label_rm(self, name):
        self._acinvoke('label', 'remove', name)

    def layer(self):
        self._acinvoke('layer')

    def mount_add(self, name, path, ro=False):
        cmd = ['mount', 'add']
        if ro:
            cmd.append('--read-only')
        cmd.extend([name, path])
        self._acinvoke(*cmd)

    def mount_rm(self, name):
        self._acinvoke('mount', 'remove', name)

    def port_add(self, name, port, protocol='tcp', count=1, socket_activation=False):
        cmd = ['port', 'add', f'--count={count}']
        if socket_activation:
            cmd.append('--socket-activated')
        cmd.extend([name, protocol, port])
        self._acinvoke(*cmd)

    def port_rm(self, name):
        self._acinvoke('port', 'rm', name)

    def replace_manifest(self, obj):
        with tempfile.NamedTemporaryFile(mode='w+t') as manifest:
            json.dump(obj, manifest)
            manifest.flush()
            self._acinvoke('replace-manifest', manifest.name)

    def run(self, *cmd, work_dir=None, engine='systemd-nspawn'):
        args = ['run']
        if self.insecure:
            args.append('--insecure')
        if work_dir:
            args.append(f'--working-dir={work_dir}')
        if engine:
            args.append(f'--engine={engine}')
        args.append('--')
        args.extend(cmd)
        self._acinvoke(*args)

    def set_pre_start_handler(self, *cmd):
        self._acinvoke('set-event-handler', 'pre-start', '--', *cmd)

    def set_post_stop_handler(self, *cmd):
        self._acinvoke('set-event-handler', 'post-stop', '--', *cmd)

    def set_exec(self, *cmd):
        self._acinvoke('set-exec', '--', *cmd)

    def set_group(self, group):
        self._acinvoke('set-group', group)

    def set_name(self, name):
        self._acinvoke('set-name', name)

    def set_supp_groups(self, *groups):
        self._acinvoke('set-supp-groups', '--', *groups)

    def set_user(self, user):
        self._acinvoke('set-user', user)

    def set_work_dir(self, work_dir):
        self._acinvoke('set-working-directory', work_dir)
