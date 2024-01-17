# hetzner-docker-registry
Setup a local docker registry or provision a Hetzner Cloud instance and create a docker registry there.

## Local
Docker registry can be setup locally through either `setup-registry.py --local` or `local.py`.
Inputs:
* `--debug`, default: `False`.
* `--registry-name`, name of the docker registry, default: `docker_registry_cache`.

## Cloud
Hetzner Cloud instance will be provisioned and the `local.py` script will run on it.
Inputs:
* `--heztner-token`, Hetzner API token used to create Hetzner Cloud instance, default: env var `HETZNER_TOKEN`. 
* `--registry-name`, name of the docker registry, default: `docker_registry_cache`.
* `--ssh-key-file`, SSH pub key file used to access the Hetzner Cloud instance, default: `~/.ssh/id_rsa.pub`.
* `--server-name`, Name of the Hetzner Cloud instance, default: `docker-registry`.
* `--server-type`, Type of the Hetzner Cloud instance, default: `cpx31`. Available server types <https://www.hetzner.com/cloud>, **ONLY x86 IS SUPPORTED**.  
* `--server-image`, Image of the Hetzner Cloud instance, default: `docker-ce`.
* `--server-location`, Location of the Hetzner Cloud instance, default: `ash`. Available server locations <https://docs.hetzner.com/cloud/general/locations/>

## Metrics
Docker registry metrics made available at `{ip}:5001/metrics`.
