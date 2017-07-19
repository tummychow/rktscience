import typing as t
import enum
import os

StrList = t.Sequence[t.Text]
StrMap = t.Mapping[t.Text, t.Text]
# TODO: this is the argument type of os.fspath
Path = t.Union[os.PathLike, t.Union[str, bytes]]

@enum.unique
class InsecureOptions(enum.Enum):
    NONE = 'none'
    HTTP = 'http'
    IMAGE = 'image'
    TLS = 'tls'
    PUBKEY = 'pubkey'
    CAPABILITIES = 'capabilities'
    PATHS = 'paths'
    SECCOMP = 'seccomp'
    ALL_FETCH = 'all-fetch'
    ALL_RUN = 'all-run'
    ALL = 'all'

@enum.unique
class PullPolicy(enum.Enum):
    NEW = 'new'
    NEVER = 'never'
    UPDATE = 'update'

@enum.unique
class In(enum.Enum):
    NULL = 'null'
    TTY = 'tty'
    STREAM = 'stream'

@enum.unique
class Out(enum.Enum):
    NULL = 'null'
    TTY = 'tty'
    STREAM = 'stream'
    LOG = 'log'

class Volume(t.NamedTuple):
    source: t.Optional[Path]
    read_only: t.Optional[bool] = None

    def opts(self) -> t.Text:
        if self.source is not None:
            ret = f'kind=host,source={self.source}'
        else:
            ret = 'kind=empty'
        if self.read_only is not None:
            ret += f',readOnly={str(self.read_only).lower()}'
        return ret

class Application(t.NamedTuple):
    image: t.Text
    arguments: t.Optional[t.Sequence[t.Text]] = None

    debug: t.Optional[bool] = None
    dir: t.Optional[Path] = None
    local_config: t.Optional[Path] = None
    system_config: t.Optional[Path] = None
    user_config: t.Optional[Path] = None
    insecure_options: t.Optional[t.AbstractSet[InsecureOptions]] = None
    trust_keys_from_https: t.Optional[bool] = None

    name: t.Optional[t.Text] = None
    hostname: t.Optional[t.Text] = None
    pod_manifest: t.Optional[Path] = None
    exec: t.Optional[Path] = None
    user: t.Optional[t.Union[Path, t.Union[int, t.Text]]] = None
    group: t.Optional[t.Union[Path, t.Union[int, t.Text]]] = None
    no_overlay: t.Optional[bool] = None
    port: t.Optional[t.Mapping[t.Text, int]] = None
    private_users: t.Optional[bool] = None
    signature: t.Optional[Path] = None
    pull_policy: t.Optional[PullPolicy] = None
    uuid_save_file: t.Optional[Path] = None

    caps_remove: t.Optional[StrList] = None
    caps_retain: t.Optional[StrList] = None

    dns: t.Optional[StrList] = None # TODO: ip addresses, see resolv.conf "nameserver"
    dns_opt: t.Optional[StrList] = None # TODO: see resolv.conf "options"
    dns_search: t.Optional[StrList] = None # TODO: see resolv.conf "search"

    environment: t.Optional[StrMap] = None
    set_env: t.Optional[StrMap] = None
    set_env_file: t.Optional[Path] = None
    inherit_env: t.Optional[bool] = None

    interactive: t.Optional[bool] = None
    stdin: t.Optional[In] = None
    stdout: t.Optional[Out] = None
    stderr: t.Optional[Out] = None

    user_annotation: t.Optional[StrMap] = None
    user_label: t.Optional[StrMap] = None

    net: t.Optional[StrList] = None
    mds_register: t.Optional[bool] = None

    cpu: t.Optional[t.Text] = None # TODO: kube resource
    memory: t.Optional[t.Text] = None # TODO: kube resource

    volume: t.Optional[t.Mapping[t.Text, Volume]] = None
    mount: t.Optional[t.Mapping[t.Text, Path]] = None

    stage1_from_dir: t.Optional[t.Text] = None
    stage1_hash: t.Optional[t.Text] = None
    stage1_name: t.Optional[t.Text] = None
    stage1_path: t.Optional[Path] = None
    stage1_url: t.Optional[t.Text] = None # TODO: url?

    def args(self) -> t.List[str]:
        ret = [self.image]

        if self.debug is not None:
            ret.append(f'--debug={str(self.debug).lower()}')
        if self.dir is not None:
            ret.append(f'--dir={os.fspath(self.dir)}')
        if self.local_config is not None:
            ret.append(f'--local-config={os.fspath(self.local_config)}')
        if self.system_config is not None:
            ret.append(f'--system-config={os.fspath(self.system_config)}')
        if self.user_config is not None:
            ret.append(f'--user-config={os.fspath(self.user_config)}')
        if self.insecure_options is not None:
            ret.append(f'--insecure-options={",".join(map(lambda opt: opt.value, self.insecure_options))}')
        if self.trust_keys_from_https is not None:
            ret.append(f'--trust-keys-from-https={str(self.trust_keys_from_https).lower()}')

        if self.name is not None:
            ret.append(f'--name={self.name}')
        if self.hostname is not None:
            ret.append(f'--hostname={self.hostname}')
        if self.pod_manifest is not None:
            ret.append(f'--pod-manifest={os.fspath(self.pod_manifest)}')
        if self.exec is not None:
            ret.append(f'--exec={os.fspath(self.exec)}')
        if self.user is not None:
            if isinstance(self.user, int):
                ret.append(f'--user={self.user}')
            else:
                ret.append(f'--user={os.fspath(self.user)}')
        if self.group is not None:
            if isinstance(self.group, int):
                ret.append(f'--group={self.group}')
            else:
                ret.append(f'--group={os.fspath(self.group)}')
        if self.no_overlay is not None:
            ret.append(f'--no-overlay={str(self.no_overlay).lower()}')
        if self.port is not None:
            for k, v in self.port.items():
                ret.append(f'--port={k}:{v}')
        if self.private_users is not None:
            ret.append(f'--private-users={str(self.private_users).lower()}')
        if self.signature is not None:
            ret.append(f'--signature={os.fspath(self.signature)}')
        if self.pull_policy is not None:
            ret.append(f'--pull-policy={self.pull_policy.value}')
        if self.uuid_save_file is not None:
            ret.append(f'--uuid-save-file={os.fspath(self.uuid_save_file)}')

        if self.caps_remove is not None:
            ret.append(f'--caps-remove={",".join(self.caps_remove)}')
        if self.caps_retain is not None:
            ret.append(f'--caps-retain={",".join(self.caps_retain)}')

        if self.dns is not None:
            for v in self.dns:
                ret.append(f'--dns={v}')
        if self.dns_opt is not None:
            for v in self.dns_opt:
                ret.append(f'--dns-opt={v}')
        if self.dns_search is not None:
            for v in self.dns_search:
                ret.append(f'--dns-search={v}')

        if self.environment is not None:
            for k, v in self.environment.items():
                ret.append(f'--environment={k}={v}')
        if self.set_env is not None:
            for k, v in self.set_env.items():
                ret.append(f'--set-env={k}={v}')
        if self.set_env_file is not None:
            ret.append(f'--set-env-file={os.fspath(self.set_env_file)}')
        if self.inherit_env is not None:
            ret.append(f'--inherit-env={str(self.inherit_env).lower()}')

        if self.interactive is not None:
            ret.append(f'--interactive={str(self.interactive).lower()}')
        if self.stdin is not None:
            ret.append(f'--stdin={self.stdin.value}')
        if self.stdout is not None:
            ret.append(f'--stdout={self.stdout.value}')
        if self.stderr is not None:
            ret.append(f'--stderr={self.stderr.value}')

        if self.user_annotation is not None:
            for k, v in self.user_annotation.items():
                ret.append(f'--user-annotation={k}={v}')
        if self.user_label is not None:
            for k, v in self.user_label.items():
                ret.append(f'--user-label={k}={v}')

        if self.net is not None:
            ret.append(f'--net={",".join(self.net)}')
        if self.mds_register is not None:
            ret.append(f'--mds-register={str(self.mds_register).lower()}')

        if self.volume is not None:
            for k, v in self.volume.items():
                ret.append(f'--volume={k},{v.opts()}')
        if self.mount is not None:
            for k, v in self.mount.items():
                ret.append(f'--mount=volume={k},target={os.fspath(v)}')

        if self.stage1_from_dir is not None:
            ret.append(f'--stage1-from-dir={self.stage1_from_dir}')
        if self.stage1_hash is not None:
            ret.append(f'--stage1-hash={self.stage1_hash}')
        if self.stage1_path is not None:
            ret.append(f'--stage1-path={self.stage1_path}')
        if self.stage1_path is not None:
            ret.append(f'--stage1-path={os.fspath(self.stage1_path)}')
        if self.stage1_url is not None:
            ret.append(f'--stage1-url={self.stage1_url}')

        if self.arguments is not None:
            ret.append('--')
            ret.extend(self.arguments)
        return ret

def multi_args(*apps: Application) -> t.List[str]:
    if not apps:
        return []

    ret = apps[0].args()
    for app in apps[1:]:
        ret.append('---')
        ret.extend(app.args())
    return ret

def run(*apps: Application, extra_args: t.Sequence[str] = []) -> None:
    args = multi_args(*apps)
    args[0:0] = ['rkt', 'run']
    args.extend(extra_args)
    os.execvp('rkt', args)
