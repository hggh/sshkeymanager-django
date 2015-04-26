from django.db import models
from django.apps import apps
import re
from collections import OrderedDict
import itertools

from django.utils.translation import ugettext as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField
from keymgmt.validators import validate_sshkey, validate_regex
from django.core.validators import MinLengthValidator, MaxLengthValidator, validate_slug, RegexValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class DeleteNotAllowed(Exception):
    pass


class SSHAccountGroupManager(models.Manager):

    def get_queryset(self):
        return super(SSHAccountGroupManager, self).get_queryset().filter(obj_name='group')


class SSHAccountHostManager(models.Manager):

    def get_queryset(self):
        return super(SSHAccountHostManager, self).get_queryset().filter(obj_name='host')


class SSHAccountEnvironmentManager(models.Manager):

    def get_queryset(self):
        return super(SSHAccountEnvironmentManager, self).get_queryset().filter(obj_name='environment')


class SSHAccountAvailable(models.Model):
    """
    AccountAvailable model.
    This model holds default accounts available on servers. This table
    is filled on installation with the root account.
    If you are using PuppetDB you can use ./manage.py to import
    all known accounts from PuppetDB to the AccountAvailable table.
    This provides a typeahead feature on creating an Account inside the Webapp.
    """
    name = models.CharField(_('account name'), unique=True, null=False, max_length=100, blank=False,
                            validators=[
                                    MinLengthValidator(3),
                                    MaxLengthValidator(100),
                                    RegexValidator(regex='^[0-9A-Za-z_.-]+$')
                                ])

    class Meta:
        ordering = ['name']

    def clean(self):
        self.name = self.name.strip()

    def __str__(self):
        return self.name

    def all_as_array():
        all = []
        for key in SSHAccountAvailable.objects.all():
            all.append(key.name)
        return all


class Environment(models.Model):
    """
    Environment model.
    """
    name = models.CharField(_('environment name'), unique=True, null=False, max_length=100, blank=False,
                            validators=[
                                        MinLengthValidator(3),
                                        MaxLengthValidator(100),
                                        validate_slug
                                ])
    created = AutoCreatedField(_('created'))
    updated = AutoLastModifiedField(_('updated'))


    class Meta:
        ordering = ['name']

    def clean(self):
        self.name = self.name.strip()

    def id_str(self):
        """ a hack for form.obj_id.value because .value seems to be a string """
        return str(self.id)

    def get_accounts(self):
        return SSHAccount.environment_objects.filter(obj_id=self.id)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('environment_detail', kwargs={'pk': self.pk})

    def delete(self, using=None):
        if self.host_set.all().count() > 0:
            raise DeleteNotAllowed('Can not delete env because of Hosts have this env.')
        else:
            SSHAccount.objects.all().filter(obj_name='environment').filter(obj_id=self.id).delete()
            super(Environment, self).delete(using=using)


class Host(models.Model):
    """
    Host model.
    """
    name = models.CharField(_('Host Name'), unique=True, null=False, max_length=155, blank=False,
                            validators=[
                                        MinLengthValidator(3),
                                        MaxLengthValidator(155),
                                        RegexValidator(regex='^[0-9A-Za-z_.-]+$', message=_('Hostname is not valid.'))
                                    ])
    ipaddress = models.GenericIPAddressField(_('IP Address'), protocol='both', null=True, blank=True)
    environment = models.ForeignKey(Environment)
    created = AutoCreatedField(_('created'))
    updated = AutoLastModifiedField(_('updated'))


    def get_account_merged(self):
        """
            merge all accounts from Environments,Groups and the Host
            return as dict with array of the keys for that account
        """
        accounts = {}
        for acc in self.get_accounts():
            if acc.name not in accounts:
                accounts[acc.name] = []
            accounts[acc.name].append(acc.get_all_keys())

        for acc in self.environment.get_accounts():
            if acc.name not in accounts:
                accounts[acc.name] = []
            accounts[acc.name].append(acc.get_all_keys())

        for group in self.group_set.all():
            for acc in group.get_accounts():
                if acc.name not in accounts:
                    accounts[acc.name] = []
                accounts[acc.name].append(acc.get_all_keys())

        accounts_merged = {}
        for account,keys in accounts.items():
            accounts_merged[account] = []
            merged = list(itertools.chain(*keys))
            accounts_merged[account] = list(OrderedDict.fromkeys(merged))
        return accounts_merged

    def id_str(self):
        """ a hack for form.obj_id.value because .value seems to be a string """
        return str(self.id)

    class Meta:
        ordering = ['name']

    def save(self, force_insert=False, force_update=False, using=None):
        """ override default save to check if host.name matches a groupRule and add it to Group """
        super(Host, self).save(force_insert=force_insert, force_update=force_update, using=using)
        rules = GroupRule.objects.all()
        for rule in rules:
            if rule.rule_match_host(self.name):
                rule.group.hosts.add(self)

    def get_accounts(self):
        return SSHAccount.host_objects.filter(obj_id=self.id)

    def clean(self):
        self.name = self.name.strip()
        if self.ipaddress:
            self.ipaddress = self.ipaddress.strip()

    def __str__(self):
        return self.name

    def delete(self, using=None):
        SSHAccount.objects.all().filter(obj_name='host').filter(obj_id=self.id).delete()
        super(Host, self).delete(using=using)


class Group(models.Model):
    """
    Group model.
    """
    name = models.CharField(_('Group Name'), unique=True, null=False, max_length=32, blank=False,
                            validators=[
                                        MinLengthValidator(3),
                                        MaxLengthValidator(32),
                                        RegexValidator(regex='^[0-9A-Za-z\s_.-]+$', message=_('Only A-Za-z0-9\s_-. are allowed!'))
                                    ])
    created = AutoCreatedField(_('created'))
    updated = AutoLastModifiedField(_('updated'))
    hosts = models.ManyToManyField(Host)


    class Meta:
        ordering = ['name']

    def id_str(self):
        """ a hack for form.obj_id.value because .value seems to be a string """
        return str(self.id)

    def clean(self):
        self.name = self.name.strip()

    def __str__(self):
        return self.name

    def get_accounts(self):
        return SSHAccount.group_objects.filter(obj_id=self.id)

    def get_absolute_url(self):
        return reverse('group_detail', kwargs={'pk': self.pk})

    def delete(self, using=None):
        SSHAccount.objects.all().filter(obj_name='group').filter(obj_id=self.id).delete()
        super(Group, self).delete(using=using)

class GroupRule(models.Model):
    """
    Group Rule model.
    """
    rule = models.CharField(_('Group Rule'), null=False, max_length=32, blank=False, validators=[validate_regex])
    group = models.ForeignKey(Group)
    created = AutoCreatedField(_('created'))
    updated = AutoLastModifiedField(_('updated'))


    def rule_match_host(self, hostname):
        if re.search(r'%s' % self.rule, hostname):
            return True
        return False

    def __str__(self):
        return self.rule


class SSHKey(models.Model):
    """
    SSH Key model.
    """
    name = models.CharField(_('SSH Key Name'), unique=True, null=False, max_length=32, blank=False,
                            validators=[
                                        MinLengthValidator(3),
                                        MaxLengthValidator(32),
                                        RegexValidator(regex='^[0-9A-Za-z\s_.-]+$', message=_('Only A-Za-z0-9\s_-. are allowed!'))
                                    ])
    sshkey = models.TextField(_('SSH Key'), null=False, validators=[validate_sshkey])
    created = AutoCreatedField(_('created'))
    updated = AutoLastModifiedField(_('updated'))


    class Meta:
        ordering = ['name']

    def clean(self):
        self.name = self.name.strip()
        if self.sshkey:
            self.sshkey = self.sshkey.strip().rstrip()

    def ssh_key_entry(self):
        return self.sshkey + " " + self.name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('sshkey_detail', kwargs={'pk': self.pk})

    def sshkey_short(self):
        return self.sshkey[0:30]

    def all_as_array():
        all = []
        for key in SSHKey.objects.all():
            all.append(key.name)
        return all

    def filename2name(filename):
        """
        This method is used for import of SSH Keys from the Filesystem.
        It will return a useful clear name to insert it into DB from
        the filename of the Key.
         """
        filename = filename.strip()
        filename = re.sub(r'\.pub$', '', filename)
        name = re.sub(r'(-|_|\.)', ' ', filename)
        return name.title()


class SSHKeyring(models.Model):
    """
    SSH Keyring model.
    """
    name = models.CharField(_('SSH Keyring'), unique=True, null=False, max_length=32, blank=False,
                            validators=[
                                        MinLengthValidator(3),
                                        MaxLengthValidator(32),
                                        RegexValidator(regex='^[0-9A-Za-z\s_.-]+$', message=_('Only A-Za-z0-9\s_-. are allowed!'))
                                    ])
    created = AutoCreatedField(_('created'))
    updated = AutoLastModifiedField(_('updated'))
    keys = models.ManyToManyField(SSHKey)

    class Meta:
        ordering = ['name']

    def add_keys(self, sshkeys):
        for key in self.keys.all():
            self.keys.remove(key)
        for key in sshkeys.split(','):
            try:
                sshkey = SSHKey.objects.get(name=key)
                self.keys.add(sshkey)
            except ObjectDoesNotExist:
                pass

    def clean(self):
        self.name = self.name.strip()

    def get_absolute_url(self):
        return reverse('sshkeyring_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def all_as_array():
        all = []
        for key in SSHKeyring.objects.all():
            all.append(key.name)
        return all


class SSHAccount(models.Model):
    """
    SSHAcount model.
    This model holds the account and links to the objects (environment,Host, Group)
    """
    name = models.CharField(_('SSH Account Name'), null=False, max_length=100, blank=False,
                            validators=[
                                        MinLengthValidator(3),
                                        MaxLengthValidator(100),
                                        RegexValidator(regex='^[0-9A-Za-z_.-]+$')
                                        ])
    obj_name = models.CharField(_('Object Name'), null=False, max_length=100, blank=False,
                            validators=[
                                        MinLengthValidator(3),
                                        RegexValidator(regex='^(environment|host|group)$')
                                    ])
    obj_id = models.IntegerField(_('Object Id'), null=False, blank=False)
    keys = models.ManyToManyField(SSHKey)
    keyrings = models.ManyToManyField(SSHKeyring)

    objects = models.Manager()
    group_objects = SSHAccountGroupManager()
    host_objects = SSHAccountHostManager()
    environment_objects = SSHAccountEnvironmentManager()


    class Meta:
        unique_together = ('name', 'obj_name', 'obj_id')
        ordering = ['name']


    def clean(self):
        self.name = self.name.strip()
        if self.obj_id is not None and self.obj_name is not None:
            if self.obj_name == 'environment':
                try:
                    Environment.objects.get(pk=self.obj_id)
                except:
                    raise ValidationError('parent Environment not found')
            elif self.obj_name == 'host':
                try:
                    Host.objects.get(pk=self.obj_id)
                except:
                    raise ValidationError('parent Host not found')
            elif self.obj_name == 'group':
                try:
                    Group.objects.get(pk=self.obj_id)
                except:
                    raise ValidationError('parent Group not found')
            else:
                raise ValidationError('obj_name is not valid.')

    def __str__(self):
        return self.name

    def get_all_keys(self):
        keys = []
        keys.append(self.keys.all())
        for ring in self.keyrings.all():
            keys.append(ring.keys.all())
        keys_merged = list(itertools.chain(*keys))
        return list(OrderedDict.fromkeys(keys_merged))

    def get_object(self):
        klass = apps.get_model(app_label='keymgmt', model_name=self.obj_name.capitalize())
        return klass.objects.get(pk=self.obj_id)

    def update_keyrings(self, sshkeyrings):
        for ring in self.keyrings.all():
            self.keyrings.remove(ring)

        for ring in sshkeyrings.split(','):
            try:
                sshkeyring = SSHKeyring.objects.get(name=ring)
                self.keyrings.add(sshkeyring)
            except ObjectDoesNotExist:
                pass

    def update_keys(self, keys):
        for key in self.keys.all():
            self.keys.remove(key)

        for key in keys.split(','):
            try:
                sshkey = SSHKey.objects.get(name=key)
                self.keys.add(sshkey)
            except ObjectDoesNotExist:
                pass