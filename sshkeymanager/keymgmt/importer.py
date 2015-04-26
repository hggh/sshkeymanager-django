from keymgmt.models import SSHKey, Environment, Host, SSHAccountAvailable
import os
import requests
import glob
from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings


class ImportPuppetdb:
    def __init__(self):
        self.settings = self.get_settings()

    def get_settings(self):
        if hasattr(settings, 'PUPPETDB') is False:
            raise Exception("Could not find configuration PUPPETDB in settings")
        return settings.PUPPETDB

    def users(self):
        users = []
        puppetdb_users = self._get('/resources/User')
        for user in puppetdb_users:
            users.append(user['title'])
        users = list(OrderedDict.fromkeys(users))
        return users

    def nodes(self):
        nodes = []
        puppetdb_nodes = self._get('/nodes')
        for node in puppetdb_nodes:
            nodes.append(
                {
                    'name': node["certname"],
                    'ip': self.node_ipaddress(node["certname"]),
                    'env': node["catalog-environment"]
                 }
            )
        return nodes

    def node_ipaddress(self, node):
        ip = None
        try:
            result = self._get('/nodes/' + node + '/facts/ipaddress')
            ip = result[0]["value"]
        except:
            """ we don't care if we found no ip address """
            pass
        return ip

    def _url(self):
        if self.settings['SSL_KEY'] is None and self.settings['SSL_CERT'] is None:
            proto = 'http'
        else:
            proto = 'https'
        return proto + '://' + self.settings['HOST'] + ':' + str(self.settings['PORT']) + '/v4'

    def _get(self, query, params=None):
        headers = {
            'Content-Type': 'application/json'
        }
        url = self._url() + query
        try:
            req = requests.get(url,
                        params=params,
                        headers=headers,
                        verify=self.settings['SSL_VERIFY'],
                        cert=(self.settings['SSL_CERT'], self.settings['SSL_KEY']),
                        timeout=self.settings['TIMEOUT']
                    )
            body = req.json()
            if body is not None:
                return body
            else:
                raise Exception("no body returned by query: " + url)
        except:
            print("Error: with connecting to PuppetDB")
            raise


class ImportSSHAccountAvailable:
    def __init__(self, accounts):
        self.accounts = accounts
        self.import_success = []
        self.import_already = []
        self.import_error = []

    def import_names(self):
        for account in self.accounts:
            self.create_accountavailable(account)

    def create_accountavailable(self, name):
        try:
            SSHAccountAvailable.objects.get(name=name)
            self.import_already.append(name)
            return
        except ObjectDoesNotExist:
            try:
                account = SSHAccountAvailable(name=name)
                account.clean()
                account.full_clean()
                account.save()
                self.import_success.append(name)
            except ValidationError:
                self.import_error.append(name)


class ImportHost:
    def __init__(self, file):
        self.filename = file
        self.content = []
        self.import_errors = []
        self.import_ok = []
        self.import_already = []

    def import_host(self):
        for host in self.content:
            env = self.create_or_return_env(host['env'])
            if env is not None:
                try:
                    Host.objects.get(name=host['name'])
                    self.import_already.append(host['name'])
                    continue
                except:
                    pass
                chost = self.create_host(host['name'], env, host['ip'])
                if chost is not None:
                    self.import_ok.append(host['name'])
                else:
                    self.import_errors.append(host['name'])
            else:
                self.import_errors.append(host['name'])

    def create_host(self, hostname, env, ip):
        try:
            host = Host(name=hostname, environment=env, ipaddress=ip)
            host.clean()
            host.full_clean()
            host.save()
            return host
        except ValidationError:
            pass

    def create_or_return_env(self, envname):
        try:
            env = Environment.objects.get(name=envname)
        except ObjectDoesNotExist:
            env = Environment(name=envname)
            try:
                env.clean()
                env.full_clean()
                env.save()
            except ValidationError:
                env = None
        return env

    def split_line(line):
        host = {
                'env': 'production',
                'ip': None
                }
        line = line.strip().rstrip()
        arr = line.split(',', maxsplit=2)

        if len(arr) == 0 or line == '':
            return None

        host['name'] = arr[0].strip()

        try:
            if arr[1].strip() != '':
                host['env'] = arr[1].strip()
        except IndexError:
            pass

        try:
            if arr[2].strip() != '':
                host['ip'] = arr[2].strip()
        except IndexError:
            pass

        return host

    def read_file(self):
        with open(self.filename) as f:
            for line in f:
                self.content.append(ImportHost.split_line(line))


class ImportSSHKey:
    def __init__(self, options):
        self.option_with_errors = []
        self.sshkeys = []
        self.sshkeys_added = []
        self.sshkeys_added_already = []
        self.sshkeys_added_errors = []
        self.parse_option(options)
        self.make_uniq()

    def add_keys_to_db(self):
        for key in self.sshkeys:
            sshkey_basename = os.path.basename(key)
            name = SSHKey.filename2name(sshkey_basename)
            try:
                SSHKey.objects.get(name=name)
                self.sshkeys_added_already.append(key)
                continue
            except ObjectDoesNotExist:
                skey = SSHKey(name=name, sshkey=ImportSSHKey.ssh_read_key(key))

            try:
                skey.clean()
                skey.full_clean()
                skey.save()
                self.sshkeys_added.append(key)
            except ValidationError:
                self.sshkeys_added_errors.append(key)

    def parse_option(self, options):
        for option in options:
            ftype = self.check_option_mode(option)
            if ftype == 'directory':
                self.check_directory(option)
            elif ftype == 'file':
                self.sshkeys.append(option)
            else:
                self.option_with_errors.append(option)

    def ssh_read_key(filename):
        content = open(filename).read()
        return content

    def check_option_mode(self, option):
        """
        returns type of option: directory or file
        """
        if os.path.isdir(option) and os.access(option, os.R_OK):
            return 'directory'
        elif os.path.isfile(option) and os.access(option, os.R_OK):
            return 'file'

    def check_directory(self, directory):
        for file in glob.glob(os.path.join(directory, '*.pub')):
            if self.check_option_mode(file):
                self.sshkeys.append(file)
            else:
                self.option_with_errors.append(file)

    def make_uniq(self):
        self.sshkeys = list(OrderedDict.fromkeys(self.sshkeys))
        self.option_with_errors = list(OrderedDict.fromkeys(self.option_with_errors))
