remove container data
=========

removes all volumes, containers and networks that are defined in the compose and orverride files using compose down command.
this is only required for uninstall and testing because of force recreate flag in compose up command.


example 
----------------
```yaml
- name: compose
  import_role:
    name: ji_podhead.netbox_docker_podman.remove_container_data
```

License
-------

BSD

Author Information
------------------
ji_podhead