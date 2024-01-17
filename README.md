# Hetzner Docker Registry
Setup a local docker registry or provision a Hetzner Cloud instance and create a docker registry there. The docker registry is setup as a service using the `distribution/distribution:2.8.3` image. Uses 5000 and 5001 ports.

## Local
Docker registry can be setup locally through either `docker-registry.py --local` or `local.py`.  
Inputs:
* `--debug`, default: `False`.
* `--registry-name`, name of the docker registry, default: `docker_registry_cache`.

## Cloud
Docker registry can be setup remotely through `docker-registry.py --cloud`. This will provision a Hetzner Cloud instance, upload `local.py` script as `docker-local-registry.py`, and executed on it on the instance.  
Inputs:
* `--heztner-token`, Hetzner API token used to create Hetzner Cloud instance, default: env var `HETZNER_TOKEN`.  
* `--registry-name`, Name of the docker registry, default: `docker_registry_cache`.  
* `--ssh-key-file`, SSH pub key file used to access the Hetzner Cloud instance, default: `~/.ssh/id_rsa.pub`.  
* `--server-name`, Name of the Hetzner Cloud instance, default: `docker-registry`.  
* `--server-type`, Type of the Hetzner Cloud instance, default: `cpx31`. Available server types <https://www.hetzner.com/cloud>, **ONLY x86 IS SUPPORTED**.  
* `--server-image`, Image of the Hetzner Cloud instance, default: `docker-ce`. It is assumed that docker is installed. Images without docker installation will not work.  
* `--server-location`, Location of the Hetzner Cloud instance, default: `ash`. Available server locations <https://docs.hetzner.com/cloud/general/locations/>  

## Metrics
Docker registry metrics are made available at `{ip}:5001/metrics`.
