superuser
=========

creates a superuser and password

- since this is waiting for the migration, it can take a while for this to succeed. 
- if it fails you should look at the container logs and might increase the max tries or delay in the role.

Requirements
------------
- up and running netbox-docker using  the compose and up roles

Role Variables
--------------
defaults:
```yaml
user: "admin"
password: "admin"
email: "admin@email.de"
index: 1
```
those are just the db creadentials and user account

License
-------

BSD

Author 
------------------
ji-podhead