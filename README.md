# Netbox Docker Podman Ansible Collection
  
| [vars](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#vars) | [usage](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#usage) | [complete example](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#complete-examples) | [all variables](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#all-variables) | [troubleshoot](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#troubleshoot) | 

---

<div align="center">
  <table>
  <tr>
    <th>Ansible Galaxy Collection</th>
    <td><a href="https://galaxy.ansible.com/ui/repo/published/ji_podhead/netbox_docker_podman/">
      ji_podhead.netbox_docker_podman
  </a></td>
  </tr>
  <tr>
    <th>Install</th>
    <td><code>ansible-galaxy collection install ji_podhead.netbox_docker_podman</code></td>
  </tr>
</table>
</div>

---

### features
<b>Netbox Docker Podman automatically installs Netbox-Docker for you, creates a superuser and Token for direct usage via ansible.</b>
- direct ansible usage! no manual exec needed!
- automatic superuser creation
- automatic usertoken creation
- ip assignment
- multiple networks (can vary per container)
- waits until database migration has finished before config

> uses [Netbox-Docker](https://github.com/netbox-community/netbox-docker), so pls head over there and give them a star!

---

## vars

> ***please see the `all variables` section for a complet list, description and types of all variables used in this collection***

- you dont need to specify any variables other than required
- be aware that this will use default network and credentials
- changing the django / db credentials might be challenging
- you can add networks for some containers only and use default for the rest
- you can have as many networks for each container as you want, but only one static ip in the compose file, <br> however i left the option to use override to config all of your other networks on the host
- you can add additionally overrides, but be aware of the formation and indent
- make sure the main static ip is in the subnet of at least one of your networks, or at least in the default networks subnet
- use the `use_default_network` parameter if you dont want to define the network manually


---


## usage

### use sudo and import the collection

```yaml 
- hosts: <your hosts>
  gather_facts: no
  become: true
  become_method: sudo
  become_user: root
  collections:

    - ji.podhead.netbox_docker_podman 
```

### most basic setup

- this is only using the required vars, but i will show more complex and complete manual scenarios in the `complete examples` section

```yaml
  - name: setup netbox
      vars:
          version: "4.0-2.9.1"
          cluster_index: 1
          platform: "podman" 
          compose_path: /home/worker/.local/bin/podman-compose
          allow_default_network: "yes" 
```
- note the the compose path variable!
- you can find your docker/podman-compose path on the host by running:

```bash 
which podman/docker-compose 
```


### deploy

- note that you dont need to init the folder (also pulls the repo) if you make changes
- ***THIS IS NOT RESTORING YOUR DB***
- be aware that recreating the containers will also delete your postgress db, so you need to back it up before. 
  - im thinking of implementing this however
- you dont need to pull if you have done so before and your dependencies have not changed


```yaml
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

        - name: pull
          import_role:
            name: ji_podhead.netbox_docker_podman.pull

        - name: up
          import_role:
            name: ji_podhead.netbox_docker_podman.up
```

### create usertoken and superuser

- note that for the token you have to have the netbox ip and a network, or use default network . 

```yaml
#     --------> optional <----------
        - name: superuser
          import_role:
            name: ji_podhead.netbox_docker_podman.superuser
       
        - name: create api token
          import_role:
            name: ji_podhead.netbox_docker_podman.create_token
          vars:
            port: 8000
            ip: localhost
            user: admin
            password: admin
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

---

## complete examples

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

---


## All Variables
<table>
  <tr>
    <th>
    <tr>
    <td><b>Containers</b></td>
    <td> < </td> <td><b>Container Values</b></td>  <td> > </td>
    <td> < </td> <td><b> Networks </b></td>        <td> > </td>
    <td> < </td> <td><b> Required </b></td>        <td> > </td>
    <td> < </td> <td><b> credentials </b></td>     <td> > </td>
    <td><b>override</b></td>
    </tr>
    <tr>
    <td><b>name</b></td>
    <td><b>name</b></td>
    <td><b>description</b></td>
    <td><b>type</b></td>
    <td><b>name</b></td>
    <td><b>description</b></td>
    <td><b>type</b></td>
    <td><b>name</b></td>
    <td><b>description</b></td>
    <td><b>type</b></td>
    <td><b>name</b></td>
    <td><b>description</b></td>
    <td><b>type</b></td>
    <td><b>info</b></td>
    </tr>
    </th>
  </tr>
  <tr>
  <td>
    <tr>
      <td>netbox </td>
      <td><b>ip</b></td>
      <td>the main ip - must be in a subnet</td>
      <td>string</td>
      <td><b>name</b></td>
      <td>name of the network</td>
      <td>string</td>
      <td><b>index</b></td>
      <td>index of the netbox node</td>
      <td>int</td>
      <td><b>user</b></td>
      <td>database and netbox user</td>
      <td>string</td>
      <td rowspawn="6">
  overrides for the docker-compose.overrides.yaml. needs to be in yaml format.
  </td>
    </tr>
    <tr>
      <td>redis </td>
      <td><b>hostname</b></td> 
      <td>the containers hostname</td> 
      <td>string</td>
      <td><b>subnet</b></td>
      <td>the networks subnet</td>
      <td>string</td>
      <td><b>platform</b></td>
      <td>compose platform: docker/podman</td>
      <td>string</td>
      <td><b>password</b></td>
      <td>userpassword</td>
      <td>string</td>
      <td>x</td>
    </tr>
    <tr>
      <td>redis_cache</td>
      <td><b>network</b></td>
      <td>all networks this container uses</td>
      <td>list(strings)</td>
      <td><b>gateway</b></td>
       <td>the gateway ip of the network</td>
       <td>string</td>
       <td><b>compose_path</b></td>
      <td>the path to docker/podman-compose</td>
      <td>string</td>
      <td><b>email</b></td>
      <td>useremail</td>
      <td>string</td>
      <td>x</td>
    </tr>
    <tr>
      <td>netbox_housekeeping</td>
       <td>x</td>
      <td>x</td>
      <td>x</td>
      <td><b>iprange</b></td>
      <td>the networks ip range</td>
      <td>string</td>
      <td><b>version</b></td>
      <td>postgres version</td>
      <td>string</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
    </tr>
    <tr>
      <td>netbox_worker</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td><b>allow_default_network</b></td>
      <td>automatically add default network</td>
      <td>bool</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
    </tr>
    <tr>
      <td>postgres</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      </tr>
  </td>
  </tr>
</table>
  
---

## troubleshoot
- i had issues with the container modules, so you might need to import them like this:

```yaml
- hosts: <your hosts>
  gather_facts: no
  become: true
  become_method: sudo
  become_user: root
  collections:
    - containers.podman.podman_network
    - containers.podman.podman_container
    - containers.podman.podman_compose
    - ji.podhead.netbox_docker_podman 
```

- if you have used another postgres version in the past, you might need to pull again
- if you run into issues in the `up` role, check your formation and indents. <br> you can check the /tmp/netbox-docker/docker-compose.yml in your container, <br> this is where the `init netbox folder` role clones the repo and overrides the yaml files

---

## contribution and testing
- i have not tested with docker-compose yet, but should be working
- if you find some bugs, or something is not working for you, just let me know and feel free to open an issue 

---

## intention thoughts and thanks
### why
someone from the oh so beloved homelab discord channel came up with netbox and i was about to build my own network manager, so i thought: lets give this a try.
- unfortunately the official netbox ansible docs dont explain how to automate the entire process, so its required to manually exec into the deployed container instance to create superuser and therefore also the token.
- i noticed though that its somehow possible, but i ran in a bunch of issues with compose and ansible, so i thought i make this a collection, so others may profit from this

### thanks

- huge thanks goes out to [homelab discord](https://discord.gg/homelab) for helping me out  ♥
- huge thanks goes out to [@bvierra](https://github.com/bvierra) for giving me some nice hints and reviewing my codebase  ♥

---

## todo and roadmap
- back up and restore postgres
- improve error handling

---

| [vars](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#vars) | [usage](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#usage) | [complete example](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#complete-examples) | [all variables](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#all-variables) | [troubleshoot](https://github.com/the-pod-shop/netbox_docker_podman_collection/tree/main?tab=readme-ov-file#troubleshoot) | 


