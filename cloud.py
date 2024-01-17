import time
import base64
import hashlib

from hcloud import Client
from hcloud.ssh_keys.domain import SSHKey
from hcloud.server_types.domain import ServerType
from hcloud.locations.domain import Location
from hcloud.servers.client import BoundServer
from hcloud.images.domain import Image

from scripts.local import Action, shell


def wait_ready(server: BoundServer, timeout: float, action: Action = None):
    """Wait for server to be ready."""
    start_time = time.time()

    while True:
        status = server.status
        if action:
            action.note(f"{server.name} {status}", stacklevel=4)
        if status == server.STATUS_RUNNING:
            break
        if time.time() - start_time >= timeout:
            raise TimeoutError("waiting for server to start running")
        time.sleep(1)
        server.reload()


def ip_address(server: BoundServer):
    """Return IPv4 address of the server."""
    return server.public_net.primary_ipv4.ip


def wait_ssh(server: BoundServer, timeout: float):
    """Wait until SSH connection is ready."""
    ip = ip_address(server=server)

    attempt = -1
    start_time = time.time()

    while True:
        attempt += 1
        with Action(
            f"Trying to connect to {server.name}@{ip}...{attempt}",
            ignore_fail=True,
        ):
            returncode = ssh(server, "hostname", check=False)
            if returncode == 0:
                break
        if time.time() - start_time >= timeout:
            ssh(server, "hostname")
        else:
            time.sleep(5)


def ssh_command(server: BoundServer):
    """Return ssh command."""
    ip = ip_address(server=server)
    return f'ssh -q -o "StrictHostKeyChecking no" -o UserKnownHostsFile=/dev/null root@{ip}'


def ssh(server: BoundServer, cmd: str, *args, **kwargs):
    """Execute command over SSH."""
    return shell(
        f"{ssh_command(server=server)} {cmd}",
        *args,
        **kwargs,
    )


def fingerprint(ssh_key):
    """Calculate fingerprint of a public SSH key."""
    encoded_key = base64.b64decode(ssh_key.strip().split()[1].encode("utf-8"))
    md5_digest = hashlib.md5(encoded_key).hexdigest()

    return ":".join(a + b for a, b in zip(md5_digest[::2], md5_digest[1::2]))


def cloud(
    hetzner_token,
    registry_name,
    ssh_key_file,
    server_name,
    server_type,
    server_image,
    server_location,
    timeout=60,
):
    """Create Hetzner Cloud instance and make docker registry on it."""
    client = Client(token=hetzner_token)

    with open(ssh_key_file, "r", encoding="utf-8") as ssh_key_file:
        public_key = ssh_key_file.read()

    ssh_key = SSHKey(
        name=hashlib.md5(public_key.encode("utf-8")).hexdigest(),
        public_key=public_key,
        fingerprint=fingerprint(public_key),
    )

    existing_ssh_key = client.ssh_keys.get_by_fingerprint(
        fingerprint=ssh_key.fingerprint
    )

    with Action(f"Creating server {server_name}"):
        response = client.servers.create(
            name=server_name,
            server_type=ServerType(name=server_type),
            location=Location(name=server_location),
            image=Image(name=server_image),
            ssh_keys=[existing_ssh_key],
        )
        server: BoundServer = response.server

    with Action(f"Waiting for server {server.name} to be ready") as action:
        wait_ready(server=server, timeout=timeout, action=action)

    with Action(f"Wait for SSH connection to {server.name} to be ready"):
        wait_ssh(server=server, timeout=timeout)

    with Action("upload script to server"):
        shell(
            f"scp -o UserKnownHostsFile=/dev/null scripts/local.py root@{ip_address(server=server)}:/root/setup-local-registry.py"
        )

    with Action(f"execute registry setup on {server.name}"):
        ssh(
            server,
            f"python3 /root/setup-local-registry.py --registry-name {registry_name}",
        )
