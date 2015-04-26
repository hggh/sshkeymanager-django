# SSH Key Manager

Manage your public SSH Keys inside a Django web application and deploy the SSH keys via Puppet or via scp/rsync.


## Screenshots of the web application


[screenshots](https://github.com/hggh/sshkeymanager-django/blob/master/README.screenshots.md)


## Features

 * environments
 * a host belongs to a Environment
 * groups of hosts
 * a host can be in member in n-groups
 * a group can have 'rules'
 * then adding a new host, in background the group rules are processed and if hostname matches the rule. host will be added to group
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


## Export the configuration

There is a easy to use API with access tokens.

Configure the API access tokens inside the settings.py configuration:

    API_KEYS = [
      '0EppFIXru3Cq.',
      'iQifkhyNTsyTQ'
    ]


Deployment via Puppet: https://github.com/hggh/sshkeymanager-puppet


## Requirements

* Python 3
* Django 1.8
* django-model-utils
* simplejson
* django-bootstrap3

