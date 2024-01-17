#!/usr/bin/env python3
import sys
import datetime
import subprocess

from argparse import ArgumentParser, RawTextHelpFormatter

description = """Docker Registry setup service.

    Creates a docker registry locally.
"""


def argparser():
    """Command line argument parser."""
    parser = ArgumentParser(
        "Altinity Docker Registry setup service",
        description=description,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "--registry-name",
        action="store",
        help="Name of the docker registry, default: docker_registry_cache",
        default="docker_registry_cache",
        required=False,
    )

    return parser


class Action:
    """Action wrapper."""

    debug = False

    @staticmethod
    def timestamp():
        """Return timestamp string."""
        dt = datetime.datetime.now(datetime.timezone.utc)
        return dt.astimezone().strftime("%b %d,%Y %H:%M:%S.%f %Z")

    def __init__(self, name, ignore_fail=False):
        self.name = name
        self.ignore_fail = ignore_fail

    def __enter__(self):
        print(f"{self.timestamp()} \u270D  {self.name}")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value is not None:
            print(f"{self.timestamp()} \u274C Error", exc_value)
            if self.ignore_fail:
                return
            if self.debug:
                raise
            sys.exit(1)
        else:
            print(f"{self.timestamp()} \u2705 OK")


def shell(cmd, shell=True, check=True):
    """Execute command."""
    p = subprocess.run(
        cmd, shell=shell, stdout=sys.stdout, stderr=sys.stdout, check=check
    )
    return p.returncode


def registry(registry_name="docker_registry_cache"):
    """Setup the docker registry."""

    with Action("create docker-compose.yml"):
        shell("touch /root/docker-registry-config.yml")
        with open("/root/docker-registry-config.yml", "w") as file:
            file.write(
                "version: 0.1\n"
                "log:\n"
                "  level: debug\n"
                "  fields:\n"
                "    service: registry\n"
                "    environment: development\n"
                "storage:\n"
                "    delete:\n"
                "      enabled: true\n"
                "    cache:\n"
                "        blobdescriptor: inmemory\n"
                "    filesystem:\n"
                "        rootdirectory: /var/lib/registry\n"
                "    maintenance:\n"
                "        uploadpurging:\n"
                "            enabled: false\n"
                "http:\n"
                "    addr: :5000\n"
                "    debug:\n"
                "        addr: :5001\n"
                "        prometheus:\n"
                "            enabled: true\n"
                "            path: /metrics\n"
                "    headers:\n"
                "        X-Content-Type-Options: [nosniff]\n"
                "health:\n"
                "  storagedriver:\n"
                "    enabled: true\n"
                "    interval: 10s\n"
                "    threshold: 3\n"
                "proxy:\n"
                "  remoteurl: https://registry-1.docker.io\n"
                "  ttl: 96h\n"
            )

    with Action("create /etc/docker/daemon.json"):
        shell("touch /etc/docker/daemon.json")
        with open("/etc/docker/daemon.json", "w") as file:
            file.write("{" '  "registry-mirrors" : ["http://127.0.0.1:5000"]' "}")

    with Action("restart docker"):
        shell("systemctl restart docker")

    with Action("create /etc/systemd/system/docker_image_cache.service"):
        shell("touch /etc/systemd/system/docker_image_cache.service")
        with open("/etc/systemd/system/docker_image_cache.service", "w") as file:
            file.write(
                "# Based on https://blog.marcnuri.com/docker-container-as-linux-system-service\n"
                "[Unit]\n"
                "Description=Docker image registry cache\n"
                "After=docker.service\n"
                "Wants=network-online.target docker.socket\n"
                "Requires=docker.socket\n"
                "\n"
                "[Service]\n"
                "Restart=always\n"
                f'ExecStartPre=/bin/bash -c "/usr/bin/docker container inspect {registry_name} 2> /dev/null \\\n'
                "    || /usr/bin/docker \\\n"
                "        run \\\n"
                "        -d \\\n"
                f"        --name {registry_name} \\\n"
                "        -p 5000:5000 \\\n"
                "	-p 5001:5001 \\\n"
                "        -v /var/lib/registry:/var/lib/registry \\\n"
                "        -v /root/docker-registry-config.yml:/root/config.yml \\\n"
                "        distribution/distribution:2.8.3 \\\n"
                '        serve /root/config.yml"\n'
                f"ExecStart=/usr/bin/docker start -a {registry_name}\n"
                f"ExecStop=/usr/bin/docker stop -t 10 {registry_name}\n"
                "\n"
                "\n"
                "[Install]\n"
                "WantedBy=multi-user.target\n"
            )

    with Action("enable service"):
        shell("systemctl enable docker_image_cache.service")

    with Action("start service"):
        shell("systemctl daemon-reload")
        shell("systemctl start docker_image_cache.service")


if __name__ == "__main__":
    args = argparser().parse_args(None if sys.argv[1:] else ["-h"])

    registry(registry_name=args.registry_name)
