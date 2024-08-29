# Netbox Docker Podman Ansible Collection
  

---
Netbox Docker Podman automatically installs Netbox-Docker for you, creates a superuser and Token for direct usage via ansible.

---
- direct ansible usage! no manual exec needed!
- automatic superuser creation
- automatic usertoken creation
- ip assignment
- multiple networks (can vary per container)
- waits until database migration has finished before config


## Usage

### use sudo and import the collection
```yaml 
- hosts: dcworkshop1
  gather_facts: no
  become: true
  become_method: sudo
  become_user: root
  collections:

    - ji.podhead.netbox_docker_podman 
```

### group vars
- rn all vars are required, but i will add the defaults in the future. Netbox-podman doesnt really require anything
- note that where are using 2 networks because i want to make the postgres ha
- you can add additionally overrides, but be aware of the formation and indent

```yaml 
  t- name: setup netbox
      vars:
#-----------------> REQUIRED <-----------------
          version: "4.0-2.9.1"
          cluster_index: 1
          platform: "podman" 
          compose_path: /home/worker/.local/bin/podman-compose
          allow_default_network: "yes" # not used yet, planned for adding default network without specifying ips manually
#----------------->  OPTIONAL <----------------- NOT YET! is on todolist
        # -------->   USER    <----------
          user: "admin"
          password: "admin"
          email: "admin@email.de"
        # -------->  NETWORK <----------
          networks: 
            - name: rest
              range: 192.168.10.30/25
              subnet: 192.168.10.0/24
              gateway: 192.168.10.0
        #           ------
            - name:  postgres
              range: 2.1.2.30/25
              subnet: 2.1.2.0/24
              gateway: 2.1.2.0
        # --------> container net <----------  
          postgres:
            hostname: postgres
            ip: 192.168.10.2
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
        # --------> overrides <----------
          overrides: 
            services:
              netbox:
                ports: 
                  - 8000:8080
```

### install - Fire The Collection!
- note that you dont need to init the folder (also pulls the repo) if you make changes
- you need however to delete the container data because compose wont let you the reuse the volumes
- be aware that this will also delete your postgress db, so you need to back it up before. 
- ***THIS IS NOT RESTORING YOUR DB***
  - im thinking of implementing this however
- you dont need to pull if you have done so before and your dependencies have not changed

```yaml
#----------------->  DEPLOYMENT <-----------------
      block:
        - name: init_netbox_folder (not required when updating)
          import_role:
            name: ji_podhead.netbox_docker_podman.init_netbox_folder
        - name: remove_container_data
          import_role:
            name: ji_podhead.netbox_docker_podman.remove_container_data
        - name: networksetbox-docker_netbox-worker_1 
          import_role:
            name: ji_podhead.netbox_docker_podman.networks
        - name: compose
          import_role:
            name: ji_podhead.netbox_docker_podman.compose
        - name: pull
          import_role:
            name: ji_podhead.netbox_docker_podman.pull
        - name: up
          import_role:
            name: ji_podhead.netbox_docker_podman.up
```

### create usertoken and superuser

```yaml
        # --------> optional <----------
        - name: superuser
          import_role:
            name: ji_podhead.netbox_docker_podman.superuser
       
        - name: create api token
          import_role:
            name: ji_podhead.netbox_docker_podman.create_token
          vars:
            port: 8000
          register: token_result
        - name: debug
          debug:
            var: token_result.json.key
```

### optional: update vault
- check out the return token_result we registered before. there are other values you may wanna make use of
```yaml
        - name: Update Vault secret
          delegate_to: localhost
          ansible.builtin.uri:
            url: "http://127.0.0.1:8200/v1/keyvalue/data/netbox/{{token_result.json.user.display}}/{{token_result.json.id}}"
            method: POST
            body_format: json
            force_basic_auth: true
            body:
              options:
                cas: 0
              data:
                token: "{{token_result.json.key}}"
                url: "{{token_result.json.url}}"
                expires: "{{token_result.json.expires}}"
            validate_certs: false
            status_code: 200
            return_content: yes
            headers:
              X-Vault-Token: "{{vault_token}}"

```

### optional: create an ip in netbox using our token

```yaml
    - name: Create IP address within NetBox with only required information
      netbox.netbox.netbox_ip_address:
        netbox_url: http://192.168.10.1
        netbox_token: "{{token_result.json.key}}"
        data:
          address: 192.168.10.1
        state: present
```

## TODO and Roadmap
- add docker-compose support
- back up and restare postgres
