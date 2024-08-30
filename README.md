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



### vars
- you dont need to specify any variables other than required
- be aware that this will use default network and credentials
- changing the django / db credentials might be challenging
- you can add networks for certain containers and use default for the rest
- you can have as many networks for each container as you want, but only one static ip in the compose file, however i left the option to use the override option for all of your other networks
- make sure the main static ip is the subnet of at least one of your networks, or atleast the default networks subnet
- use the `use_default_network` parameter if you dont want to define the network manually
- you can add additionally overrides, but be aware of the formation and indent


#### all vars
<table>
  <td>
  <table>
  <div align:"center">
  <tr>
    <th>Containers</th>
    <tr><td>netbox </td></tr>
    <tr><td>redis </td></tr>
    <tr><td>redis_cache </td></tr>
    <tr><td>netbox_housekeeping</td></tr>
    <tr><td>netbox_worker</td></tr>
    <tr><td>postgres</td></tr>
  </tr>
  </div>
  </table>
  </td>
  <td>
  <table>
  <tr>
    <th>
    <tr colspan="3"><b>Container values</b></tr>
    <tr>
    <td><b>name</b></td>
    <td><b>description</b></td>
    <td><b>type</b></td>
    </tr>
    </th>
  </tr>
  <tr>
    <td>network</td>
    <td>all networks this container uses</td>
    <td>list(strinngs)</td>
  </tr>
  <tr>
    <td>ip</td>
    <td>the main ip - must be in a subnet</td>
    <td>string</td>
  </tr>
  <tr>
    <td>hostname</td>
    <td>the containers hostname</td>
    <td>string</td>
  </tr>
  </table>
  </td>
  </>
  <td>
  <table>
  <tr>
    <th>
    <tr colspan="3"><b>Required</b></tr>
    <tr>
    <td><b>name</b></td>
    <td><b>description</b></td>
    <td><b>type</b></td>
    </tr>
    </th>
  </tr>
  <tr>
    <td>version</td>
    <td>postgres version</td>
    <td>string</td>
  </tr>
  <tr>
    <td>index</td>
    <td>index of the netbox node</td>
    <td>int</td>
  </tr>
  <tr>
    <td>platform</td>
    <td>compose platform: docker/podman</td>
    <td>string</td>
  </tr>
  <tr>
    <td>compose_path</td>
    <td>the path to docker/podman-compose</td>
    <td>string</td>
  </tr>
  <tr>
    <td>allow_default_network</td>
    <td>automatically add default network</td>
    <td>bool</td>
  </tr>
  </table>
  </td>
    <td>
  <table>
  <tr>
    <th>
    <tr colspan="3"><b>credentials</b></tr>
    <tr>
    <td><b>name</b></td>
    <td><b>description</b></td>
    <td><b>type</b></td>
    </tr>
    </th>
  </tr>
  <tr>
    <td>user</td>
    <td>database and netbox user</td>
    <td>string</td>
  </tr>
  <tr>
    <td>password</td>
    <td>userpassword</td>
    <td>string</td>
  </tr>
  <tr>
    <td>email</td>
    <td>useremail</td>
    <td>string</td>
  </tr>
</table>
  </td>
</table>

## Usage

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

#### most basic setup
- this is only using the required vars, but i will show more complex and complete manual scenarios later



```yaml
  - name: setup netbox
      vars:
          version: "4.0-2.9.1"
          cluster_index: 1
          platform: "podman" 
          compose_path: /home/worker/.local/bin/podman-compose
          allow_default_network: "yes" 
```
- note the the compose path variable: you can check that out by running which podman/docker-compose on your target machine


### Deploy
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
        # --------> optional <----------
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
### complete advanced example: overrides, networks and static ips
- we choose to add 2 additional networks
> both postgres and netbox have their own network and ip
> this way we can make postgres ha and fetch the netbox ip
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
          version: "4.0-2.9.1"
          index: 1
          platform: "podman" 
          compose_path: /home/worker/.local/bin/podman-compose
          use_default_network: "yes" 

        # -------->   USER    <----------
          user: "admin"
          password: "admin"
          email: "admin@email.de"
        # -------->  NETWORK <----------
          networks: 
            - name: netbox
              range: 192.168.10.30/25
              subnet: 192.168.10.0/24
              gateway: 192.168.10.0
        #           ------
            - name:  postgres
              range: 2.1.2.30/25
              subnet: 2.1.2.0/24
              gateway: 2.1.2.0
        # # --------> container net <----------  
          postgres:
            hostname: postgres
            ip: 192.168.10.2
            networks:
              - postgres
              - default
          netbox:
            hostname: netbox
            ip: 192.168.10.0
            networks:
              - netbox
              - default
        # --------> overrides <----------
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

        # --------> optional <----------
        - name: superuser
          import_role:
            name: ji_podhead.netbox_docker_podman.superuser
```
### full example: no default values, no default network
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
#-----------------> REQUIRED <-----------------
          version: "4.0-2.9.1"
          index: 1
          platform: "podman" 
          compose_path: /home/worker/.local/bin/podman-compose
          allow_default_network: false 
        # -------->   USER    <----------
          user: "ji_podhead"
          password: "ji_superpass"
          email: "ji@podhead.de"
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

        # --------> optional <----------
        - name: superuser
          import_role:
            name: ji_podhead.netbox_docker_podman.superuser
```


## Troubleshoot
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
- if you run into issues in the `up` role, check your formation and indents. you can check the /tmp/netbox-docker/docker-compose.yml in your container, this is where the `init netbox folder` role clones the repo and overrides the yaml files

## Contribution and Testing
- i have not tested with docker-compose yet, but should be pausible
- if you find some bugs, or something is not working for you, just let me know and feel free to open an issue 


## TODO and Roadmap
- back up and restore postgres
- improve error handling

## Intention thoughts and thanks
### why
someone from the oh so beloved homelab discord channel came up with netbox and i was about to build my own network manager, so i thought: lets give this a try.
- unfortunately the official netbox ansible docs dont explain how to automate the entire process, so its required to manually exec into the deployed container instance to create superuser and therefore also the token.
- i noticed though that its somehow possible, but i ran in a bunch of issues with compose and ansible, so i thought i make this a collection, so others may profit from this

### thanks

- huge thanks for help goes out to homelab discord for helping me out 
- huge thanks goes out to https://github.com/bvierra for giving me some nice hints and reviewing my codebase




