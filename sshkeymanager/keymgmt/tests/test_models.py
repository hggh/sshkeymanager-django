from django.test import TestCase
from django.core.exceptions import ValidationError
from keymgmt.models import *


SSH_KEY_RSA='ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDIsM1GrbmWR+3jzd2njnmimjrlmPcG5CDFIZMq/AHAckbhLD+ja5Kdw0SO8jxIKiojoqlwHBiMCKN/6MjXW/4O5h4KA0fyRSL1d1pT645Psf9FLWjThoYjGrac6eJ3uFYfDjeYvJZyPtADZtwfTCi7SyuRXfwK8OMsfK1QbZEIEDrLC7Yy5/mtXWIHwQjX2OyAz4YHlPe03L0ZdIJz6juKa4aei41G+tkWzx/O35CT5vXr2hXJWIeKDhu8jS7s7OcBiv2jq/HQt87CqoSrLL1gEErL10HJpF819iAOR79mHy+0DS7eN/jb7fi4lVhCpBnB9AtaUMc65CzP7yhUTgOJ Foo Bar'


class SSHAccountAvailableTests(TestCase):
    def test_clean_name(self):
        account_available = SSHAccountAvailable(name='  foobar   ')
        account_available.clean()
        account_available.full_clean()
        account_available.save()
        self.assertEqual(account_available.name, 'foobar')
        
        account_available = SSHAccountAvailable(name='barffa#+ö')
        account_available.clean()
        with self.assertRaisesMessage(ValidationError, "Enter a valid value."):
            account_available.full_clean()      


class EnvironmentTests(TestCase):
    def test_for_invalid_name(self):
        """
        test for invalid environment name
        """
        env = Environment(name='')
        with self.assertRaises(ValidationError):
            env.full_clean()

        env = Environment(name='on')
        with self.assertRaises(ValidationError):
            env.full_clean()

        env = Environment(name='one two')
        with self.assertRaises(ValidationError):
            env.full_clean()

        env = Environment(name='whitespace ')
        self.assertRaises(ValidationError, env.full_clean)
        
    def test_for_valid_name(self):
        """
        test for valid name of env
        """
        env = Environment(name='production')
        self.assertEqual(env.clean(), None)
        self.assertEqual(env.full_clean(), None)
        self.assertEqual(env.save(), None)


    def test_delete_if_hosts_exists(self):
        env = Environment(name='prod')
        self.assertIsNone(env.clean())
        self.assertIsNone(env.full_clean())
        self.assertIsNone(env.save())

        host = Host(name='web1.example.com', environment=env)
        self.assertIsNone(host.clean())
        self.assertIsNone(host.full_clean())
        self.assertIsNone(host.save())

        with self.assertRaisesMessage(DeleteNotAllowed, 'Can not delete env because of Hosts have this env.'):
            env.delete()

        self.assertIsNone(host.delete())
        self.assertIsNone(env.delete())


    def test_on_delete_delete_accounts(self):
        env = Environment(name='prod')
        self.assertIsNone(env.clean())
        self.assertIsNone(env.full_clean())
        self.assertIsNone(env.save())

        account = SSHAccount(name='root', obj_name='environment', obj_id=env.id)
        self.assertIsNone(account.clean())
        self.assertIsNone(account.full_clean())
        self.assertIsNone(account.save())

        self.assertEqual(len(SSHAccount.objects.all()), 1)
        self.assertIsNone(env.delete())
        self.assertEqual(len(SSHAccount.objects.all()), 0)


class HostTests(TestCase):
    def test_for_invalid_name(self):
        """
        test for invalid host name
        """
        env = Environment(name='production')
        env.full_clean()
        env.save()
        host = Host(name='', environment=env)
        with self.assertRaises(ValidationError):
            host.full_clean()
        host = Host(name='fds##dfsda', environment=env)
        with self.assertRaisesMessage(ValidationError, 'Hostname is not valid.'):
            host.full_clean()
        host = Host(name='web01.example-foobar.com', environment=env)
        self.assertIsNone(host.full_clean())
        self.assertIsNone(host.save())


    def test_empty_env(self):
        host = Host(name='foobar.com')
        with self.assertRaisesMessage(ValidationError, "environment': ['This field cannot be null."):
            host.clean()
            host.full_clean()


    def test_ip_could_empty(self):
        env = Environment(name='production')
        env.full_clean()
        env.save()
        host = Host(name='fobar', environment=env)
        self.assertIsNone(host.clean())
        self.assertIsNone(host.full_clean())
        self.assertIsNone(host.save())


    def test_on_host_delete_delete_accounts(self):
        env = Environment(name='prod')
        self.assertIsNone(env.clean())
        self.assertIsNone(env.full_clean())
        self.assertIsNone(env.save())
        
        host = Host(name='foobar.com', environment=env)
        self.assertIsNone(host.clean())
        self.assertIsNone(host.full_clean())
        self.assertIsNone(host.save())

        account = SSHAccount(name='root', obj_name='host', obj_id=host.id)
        self.assertIsNone(account.clean())
        self.assertIsNone(account.full_clean())
        self.assertIsNone(account.save())

        self.assertEqual(len(SSHAccount.objects.all()), 1)
        self.assertIsNone(host.delete())
        self.assertEqual(len(SSHAccount.objects.all()), 0)



class GroupTests(TestCase):
    def test_group_create(self):
        group = Group(name='Webservers Foobar')
        self.assertIsNone(group.clean())
        self.assertIsNone(group.full_clean())
        self.assertIsNone(group.save())


    def test_group_fail(self):
        group = Group(name='jdld#+343')
        with self.assertRaises(ValidationError):
            group.clean()
            group.full_clean()
            group.save()

    def test_on_group_delete_delete_accounts(self):
        group = Group(name='prod')
        self.assertIsNone(group.clean())
        self.assertIsNone(group.full_clean())
        self.assertIsNone(group.save())

        account = SSHAccount(name='root', obj_name='group', obj_id=group.id)
        self.assertIsNone(account.clean())
        self.assertIsNone(account.full_clean())
        self.assertIsNone(account.save())

        self.assertEqual(len(SSHAccount.objects.all()), 1)
        self.assertIsNone(group.delete())
        self.assertEqual(len(SSHAccount.objects.all()), 0)

        

class GroupRuleTests(TestCase):
    def test_group_rule_check(self):
        group = Group(name='Foobar Example')
        self.assertIsNone(group.clean())
        self.assertIsNone(group.full_clean())
        self.assertIsNone(group.save())

        grouprule = GroupRule(group=group, rule='^web[0-9]+.foobar.com')
        self.assertIsNone(grouprule.clean())
        self.assertIsNone(grouprule.full_clean())
        self.assertIsNone(grouprule.save())

        self.assertFalse(grouprule.rule_match_host('web-test.foobar.com'))
        self.assertTrue(grouprule.rule_match_host('web10.foobar.com'))


    def test_invalid_rule(self):
        group = Group(name='Foobar Example')
        self.assertIsNone(group.clean())
        self.assertIsNone(group.full_clean())
        self.assertIsNone(group.save())

        grouprule = GroupRule(group=group, rule='^web[0-9+.foobar.com')
        with self.assertRaisesMessage(ValidationError, 'Rule not valid'):
            grouprule.clean()
            grouprule.full_clean()
            grouprule.save()


class SSHKeyTests(TestCase):
    def test_name(self):
        key = SSHKey(name='fsdf#+fds ', sshkey=SSH_KEY_RSA)
        with self.assertRaises(ValidationError):
            key.clean()
            key.full_clean()
            key.save()

    def test_ssh_key_entry(self):
        key = SSHKey(name='Foo Bar ', sshkey=SSH_KEY_RSA)
        self.assertIsNone(key.clean())
        self.assertIsNone(key.full_clean())
        self.assertIsNone(key.save())
        self.assertEqual(key.ssh_key_entry(),  SSH_KEY_RSA + ' Foo Bar')
        

    def test_filename2name(self):
        """
        test filename2name
        """
        self.assertEqual(SSHKey.filename2name('jonas_genannt.pub'), 'Jonas Genannt')
        self.assertEqual(SSHKey.filename2name('jonas-genannt.pub'), 'Jonas Genannt')
        self.assertEqual(SSHKey.filename2name('jonas.genannt.pub'), 'Jonas Genannt')
        self.assertEqual(SSHKey.filename2name('foobar.pub'), 'Foobar')
        self.assertEqual(SSHKey.filename2name('fooBar.pub'), 'Foobar')



class SSHKeyringTests(TestCase):
    def test_name(self):
        keyring = SSHKeyring(name='fsdf#+fdsf')
        with self.assertRaises(ValidationError):
            keyring.clean()
            keyring.full_clean()
            keyring.save()

        keyring = SSHKeyring(name='All Web Devs')
        self.assertIsNone(keyring.clean())
        self.assertIsNone(keyring.full_clean())
        self.assertIsNone(keyring.save())
        
class SSHAccountTests(TestCase):
    def test_name(self):
        group = Group(name='webservers')
        self.assertIsNone(group.clean())
        self.assertIsNone(group.full_clean())
        self.assertIsNone(group.save())

        account = SSHAccount(name='root', obj_name='group', obj_id=group.id)
        self.assertIsNone(account.clean())
        self.assertIsNone(account.full_clean())
        self.assertIsNone(account.save())

        account = SSHAccount(name='r#+oot', obj_name='group', obj_id=group.id)
        with self.assertRaises(ValidationError):
            account.clean()
            account.full_clean()
            account.save()


    def test_obj_id_host(self):
        env = Environment(name='production')
        self.assertIsNone(env.clean())
        self.assertIsNone(env.full_clean())
        self.assertIsNone(env.save())

        account = SSHAccount(name='root', obj_name='host', obj_id=12)
        with self.assertRaisesMessage(ValidationError, 'parent Host not found'):
            account.clean()
            account.full_clean()
            account.save()

        host = Host(name='web1.foobar.com', environment=env)
        self.assertIsNone(host.clean())
        self.assertIsNone(host.full_clean())
        self.assertIsNone(host.save())

        account = SSHAccount(name='root', obj_name='host', obj_id=host.id)
        self.assertIsNone(account.clean())
        self.assertIsNone(account.full_clean())
        self.assertIsNone(account.save())


    def test_obj_id_environment(self):
        account = SSHAccount(name='root', obj_name='environment', obj_id=12)
        with self.assertRaisesMessage(ValidationError, 'parent Environment not found'):
            account.clean()
            account.full_clean()
            account.save()

        env = Environment(name='production')
        self.assertIsNone(env.clean())
        self.assertIsNone(env.full_clean())
        self.assertIsNone(env.save())

        account = SSHAccount(name='root', obj_name='environment', obj_id=env.id)
        self.assertIsNone(account.clean())
        self.assertIsNone(account.full_clean())
        self.assertIsNone(account.save())


    def test_obj_id_goup(self):
        account = SSHAccount(name='root', obj_name='group', obj_id=12)
        with self.assertRaisesMessage(ValidationError, 'parent Group not found'):
            account.clean()
            account.full_clean()
            account.save()

        group = Group(name='production')
        self.assertIsNone(group.clean())
        self.assertIsNone(group.full_clean())
        self.assertIsNone(group.save())

        account = SSHAccount(name='root', obj_name='group', obj_id=group.id)
        self.assertIsNone(account.clean())
        self.assertIsNone(account.full_clean())
        self.assertIsNone(account.save())