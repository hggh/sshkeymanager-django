# SSH Key Manager  [![Build Status](https://api.travis-ci.org/hggh/sshkeymanager-django.svg)](https://travis-ci.org/hggh/sshkeymanager-django)

Manage your public SSH Keys inside a web application and deploy them via your configuration management or via a script.
A easy to use SSH public key deployment to centrally manage your SSH public keys.

With SSH Key Manager you can group your servers and map accounts to the groups. You can also group a number of keys 
to a keyring and map this keyring to a account.


## Screenshots of the web application


see [README.screenshots.md](https://github.com/hggh/sshkeymanager-django/blob/master/README.screenshots.md)


## Features

 * environments
 * a host belongs to a Environment
 * groups of hosts
 * a host can be in member in n-groups
 * a group can have 'rules' (rules are regex)
 * while adding a new host, in background the group rules are processed and if hostname matches the rule. host will be added to group
   * rule: '^web[0-9]+' will match ``web10.example.com``.
 * Accounts are the SSH Accounts on the host.
 * a account can be child of:
   * environment
   * group
   * host
 * a account can have n-sshkeys
 * a account can have n-sshkeyrings
 * a sshkeyring can have n-sshkeys
 * import feature:
   * PuppetDB
     * Hosts + Environments can be imported via v4 API from PuppetDB
   * import command
     * Hosts + Environments can be imported from files
     * SSH Keys can be imported from files
 * export feature aka deployment:
   * easy to use API, you can write your own export to your cfg
   * Deployment via Puppet:
     * [sshkeymanager-puppet](https://forge.puppetlabs.com/hggh/sshkeymanager)
     * exports the configuration from the API to hiera json
     * sshkeymanager uses the hiera json export and copy it to the hosts
   * Deployment via script:
     * Python2/Python3 script fetches configuration from API and deploy it via ssh/rsync to the hosts
     * filter feature: only deploy host/group/environemnt
       * if your hosts are behind a firewall you can only deploy the keys for a specific host/group/environment
     * available with the [django app](https://github.com/hggh/sshkeymanager-django/tree/master/skm-deploy)

## Vagrant

Vagrant Box: https://github.com/hggh/sshkeymanager-vagrant

## Demo

You can have a look a my demo system. The database will be reseted every hour.

http://85.10.208.131:8080/

## TODO

* API client to use scp/rsync to deploy your keys
* add/remove hosts to groups
* display all accounts/servers on SSH Key page
* LDAP Auth / general auth system?

## Import feature

* import hosts/environments from file or PuppetDB
* import ssh public keys from file

see [README.IMPORT.md](https://github.com/hggh/sshkeymanager-django/blob/master/README.IMPORT.md)

## Export the configuration

There is a easy to use API with access tokens.

Configure the API access tokens inside the settings.py configuration:

    API_KEYS = [
      '0EppFIXru3Cq.',
      'iQifkhyNTsyTQ'
    ]


get the configuration for all hosts:

    curl -X POST -d 'API_KEY=foobar'  http://localhost:8000/api/getkeys/

get the configuration only for one environment:

    curl -X POST -d 'API_KEY=jonas&filter_type=environment&filter_value=staging'  http://localhost:8000/api/getkeys/


get the configuration only for one group:

    curl -X POST -d 'API_KEY=jonas&filter_type=group&filter_value=webserver'  http://localhost:8000/api/getkeys/

get the configuration only for one host:

    curl -X POST -d 'API_KEY=jonas&filter_type=host&filter_value=web1.example.com'  http://localhost:8000/api/getkeys/


### Puppet

You can use [sshkeymanager-puppet](https://github.com/hggh/sshkeymanager-puppet) to deploy your keys via Puppet.


### scp/rsync

You can use the API to loop through your servers and copy the keys to the servers.


## Requirements

* Python 3
* Django 1.8
* django-model-utils
* django-bootstrap3

## license/copyright

License: [GPL v2](https://github.com/hggh/sshkeymanager-django/blob/master/LICENSE.txt)

Copyright 2015 Jonas Genannt


## contact?

Jonas Genannt @hggh / jonas@brachium-system.net
