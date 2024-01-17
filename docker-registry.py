#!/usr/bin/env python3
import os
import sys

from argparse import ArgumentParser, RawTextHelpFormatter

from scripts.local import Action, registry
from scripts.cloud import cloud

description = """Docker Registry setup service.

    Script that creates a docker registry either locally or creates a Hetzner Cloud instance with a docker registry.
"""


def argparser():
    """Command line argument parser."""
    parser = ArgumentParser(
        "Altinity Docker Registry setup service",
        description=description,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debugging mode, default: False",
        default=False,
        required=False,
    )

    parser.add_argument(
        "--hetzner-token",
        action="store",
        help="Hetzner API token used to create Hetzner Cloud instance, default: env var HETZNER_TOKEN",
        default=os.getenv("HETZNER_TOKEN"),
        required=False,
    )

    parser.add_argument(
        "--registry-name",
        action="store",
        help="Name of the docker registry, default: docker_registry_cache",
        default="docker_registry_cache",
        required=False,
    )

    parser.add_argument(
        "--ssh-key-file",
        action="store",
        help="SSH pub key file used to access the Hetzner Cloud instance, default: ~/.ssh/id_rsa.pub",
        default=os.path.expanduser("~/.ssh/id_rsa.pub"),
        required=False,
    )

    parser.add_argument(
        "--server-name",
        action="store",
        help="Name of the Hetzner Cloud instance, default: docker-registry",
        default="docker-registry",
        required=False,
    )

    parser.add_argument(
        "--server-type",
        action="store",
        help="Type of the Hetzner Cloud instance, default: cpx31",
        default="cpx31",
        required=False,
    )

    parser.add_argument(
        "--server-image",
        action="store",
        help="Image of the Hetzner Cloud instance, default: docker-ce",
        default="docker-ce",
        required=False,
    )

    parser.add_argument(
        "--server-location",
        action="store",
        help="Location of the Hetzner Cloud instance, default: ash",
        default="ash",
        required=False,
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--local",
        action="store_true",
        help="create docker registry locally",
        default=False,
    )

    group.add_argument(
        "--cloud",
        action="store_true",
        help="create a docker registry on a Hetzner Cloud instance",
        default=False,
    )

    return parser


if __name__ == "__main__":
    args = argparser().parse_args(None if sys.argv[1:] else ["-h"])

    if args.debug:
        Action.debug = True

    if args.local:
        registry(registry_name=args.registry_name)

    if args.cloud:
        assert (
            args.hetzner_token is not None
        ), "hetzner-token must be provided or HETZNER_TOKEN env var must be set"
        cloud(
            hetzner_token=args.hetzner_token,
            registry_name=args.registry_name,
            ssh_key_file=args.ssh_key_file,
            server_name=args.server_name,
            server_type=args.server_type,
            server_image=args.server_image,
            server_location=args.server_location,
        )
