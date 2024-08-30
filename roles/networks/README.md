networks
=========

a role that setup your networks, since the compose and netbox requires the networks to exist before compose up command.


Role Variables
--------------
a list of networks with the following parameters:
- name
- range
- subnet
- gateway

example
--------------

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
          networks: 
            - name: netbox
              range: 192.168.10.30/25
              subnet: 192.168.10.0/24
              gateway: 192.168.10.0
            - name:  postgres
              range: 2.1.2.30/25
              subnet: 2.1.2.0/24
              gateway: 2.1.2.0
  - name: networks
    import_role:
      name: ji_podhead.netbox_docker_podman.networks
```

License
-------

BSD

Author Information
------------------

ji_podhead