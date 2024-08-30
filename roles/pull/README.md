pull
=========

this role pulls the dependencies defined in docker-compose.yaml.
if they dont have changes and you have pulled allready, you dont need to do this again.

example
----------------

```yaml
- name: pull
  import_role:
    name: ji_podhead.netbox_docker_podman.pull
```

License
-------

BSD

Author Information
------------------

ji_podhead