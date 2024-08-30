create_token
=========

a role that creates a netbox token using credentials

Requirements
------------

- created superuser
- netbox server is up and running

Role Variables
--------------
defaults:
```
user: "admin"
password: admin
port: 8000
ip: localhost
```

Example Playbook
----------------

```yaml
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

License
-------

BSD

Author Information
------------------

ji_podhead