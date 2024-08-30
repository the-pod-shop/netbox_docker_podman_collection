compose
=========

creates a docker-compose.yml and docker-compose.override.yml in the /tmp/netbox-docker folder on the host

Requirements
------------
- initialized netbox-folder
- created the networks (if not only using default)


Role Variables
--------------
defaults:
```
---
use_default_network: true
networks:
  - name: default

# --------> container net <----------  
postgres:
  networks:
    - default
netbox:
  networks:
    - default
redis:
  networks:
    - default
redis_cache:
  networks:
    - default
netbox_housekeeping:
  networks:
    - default
netbox_worker:
  networks:
    - default
# --------> overrides <----------
overrides: 
  services:
    netbox:
      ports: 
        - 8000:8080
```

Examples
----------------

### overrides, static ips, default- and 2 additional networks
> both postgres and netbox have their own network and ip <br>
> this way we can make postgres ha and fetch the netbox ip <br>
> all the other containers use the default network and get an ip from podman, or docker <br>
> we also override the netbox port

```yaml

- hosts: <your hosts>
  gather_facts: no
  become: true
  become_method: sudo
  become_user: root
  collections:
    - ji.podhead.netbox_docker_podman 
    - name: setup netbox
      vars:
#         --------> Required <----------
          version: "4.0-2.9.1"
          index: 1
          platform: "podman" 
          compose_path: /home/worker/.local/bin/podman-compose
          use_default_network: "yes" 
#         --------> Credentials <----------
          user: "admin"
          password: "admin"
          email: "admin@email.de"
#         ---------->  Network <-----------
          networks: 
            - name: netbox
              range: 192.168.10.30/25
              subnet: 192.168.10.0/24
              gateway: 192.168.10.0
#                  ------
            - name:  postgres
              range: 2.1.2.30/25
              subnet: 2.1.2.0/24
              gateway: 2.1.2.0
#         -------> Container Values <--------  
          postgres:
            hostname: postgres
            ip: 2.1.2.0
            networks:
              - postgres
              - default
          netbox:
            hostname: netbox
            ip: 192.168.10.0
            networks:
              - netbox
              - default
#         --------> Overrides <----------
          overrides: 
            services:
              netbox:
                ports: 
                  - 8000:8880
#----------------->  DEPLOYMENT <-----------------
      block:
        - name: init_netbox_folder (not required when updating)
          import_role:
            name: ji_podhead.netbox_docker_podman.init_netbox_folder
        - name: networksetbox-docker_netbox-worker_1 
          import_role:
            name: ji_podhead.netbox_docker_podman.networks
        - name: compose
          import_role:
            name: ji_podhead.netbox_docker_podman.compose
        - name: up
          import_role:
            name: ji_podhead.netbox_docker_podman.up
#         --------> optional <----------
        - name: superuser
          import_role:
            name: ji_podhead.netbox_docker_podman.superuser
```
---

###  no defaults: overwriting all vars
```yaml
- hosts: <your host>
  gather_facts: no
  become: true
  become_method: sudo
  become_user: root
  collections:
    - ji.podhead.netbox_docker_podman 
    - name: setup netbox

  - name: setup netbox
      vars:
          version: "4.0-2.9.1"
          index: 1
          platform: "podman" 
          compose_path: /home/worker/.local/bin/podman-compose
          allow_default_network: false 
          user: "ji_podhead"
          password: "ji_superpass"
          email: "ji@podhead.de"
          networks: 
            - name: rest
              range: 192.168.10.30/25
              subnet: 192.168.10.0/24
              gateway: 192.168.10.0
            - name:  postgres
              range: 2.1.2.30/25
              subnet: 2.1.2.0/24
              gateway: 2.1.2.0
          postgres:
            hostname: postgres
            ip: 2.1.2.1
            networks:
              - postgres
              - rest
          netbox:
            hostname: netbox
            ip: 192.168.10.0
            networks:
              - rest
          redis:
            hostname: redis
            ip: 192.168.10.3
            networks:
              - rest
          redis_cache:
            hostname: redis_cache
            ip: 192.168.10.4
            networks:
              - rest
              - postgres
          netbox_housekeeping:
            hostname: netbox_housekeeping
            ip: 192.168.10.5
            networks:
              - rest
          netbox_worker:
            hostname: netbox_worker
            ip: 192.168.10.6
            networks:
              - rest
              - postgres
          overrides: 
            services:
              netbox:
                ports: 
                  - 8000:8880
      block:
        - name: init_netbox_folder (not required when updating)
          import_role:
            name: ji_podhead.netbox_docker_podman.init_netbox_folder
        - name: networksetbox-docker_netbox-worker_1 
          import_role:
            name: ji_podhead.netbox_docker_podman.networks
        - name: compose
          import_role:
            name: ji_podhead.netbox_docker_podman.compose
        - name: up
          import_role:
            name: ji_podhead.netbox_docker_podman.up
        - name: superuser
          import_role:
            name: ji_podhead.netbox_docker_podman.superuser
```

License
-------

BSD

Author Information
------------------

ji_podhead