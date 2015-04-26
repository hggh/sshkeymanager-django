# Import

## Import from PuppetDB

add the PuppetDB configuration to your settings.py:

    PUPPETDB = {
        'HOST': '192.168.0.14',
        'PORT': 8080,
        'SSL_VERIFY': True,
        'SSL_KEY': None,
        'SSL_CERT': None,
        'TIMEOUT': 20
    }


run the import command

    ./manage.py puppetdb


## Import from files


### import SSH public keys from files


public keys should have a correct filename: {first_name}_{last_name}.pub

the filename will be the name of the key inside the key manager.

jonas_genannt.pub will be: ``Jonas Genannt``

import a complete directory ``/tmp/foobar``:

    ./manage.py import --sshkey /tmp/foobar

import a set of files:

    ./manage.py import --sshkey /tmp/jonas_genannt.pub /tmp/foo_bar.pub


### import hosts/environments from files

import a csv file. file should contain:

    hostname,environment,ip

you can leave environment and ip empty. if you do not add a environment, ``production`` will be used.
