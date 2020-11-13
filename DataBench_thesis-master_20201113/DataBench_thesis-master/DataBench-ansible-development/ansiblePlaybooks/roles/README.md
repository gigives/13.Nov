Role Name
=========

Ansible role that installs Leiningen.

Requirements
------------

A JDK must be pre-installed. This role only installs Leiningen.

Role Variables
--------------

Leiningen version to be installed.
```
lein_version: 2.7.1
```

Pre-installs leiningen on this user home directory.    
```
lein_user: root
```        

Dependencies
------------

None.

Example Playbook
----------------

- hosts: servers
      roles:
         - { role: yashible.lein }

License
-------

MIT