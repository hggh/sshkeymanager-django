from django.test import TestCase
from keymgmt.validators import *
from django.core.exceptions import ValidationError


SSH_KEY_RSA='ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDIsM1GrbmWR+3jzd2njnmimjrlmPcG5CDFIZMq/AHAckbhLD+ja5Kdw0SO8jxIKiojoqlwHBiMCKN/6MjXW/4O5h4KA0fyRSL1d1pT645Psf9FLWjThoYjGrac6eJ3uFYfDjeYvJZyPtADZtwfTCi7SyuRXfwK8OMsfK1QbZEIEDrLC7Yy5/mtXWIHwQjX2OyAz4YHlPe03L0ZdIJz6juKa4aei41G+tkWzx/O35CT5vXr2hXJWIeKDhu8jS7s7OcBiv2jq/HQt87CqoSrLL1gEErL10HJpF819iAOR79mHy+0DS7eN/jb7fi4lVhCpBnB9AtaUMc65CzP7yhUTgOJ Foo Bar'


class SSHKeyValitdatorTests(TestCase):
    def test_validate_sshkey(self):
        """
        test ssh key validator
        """
        self.assertEqual(validate_sshkey(SSH_KEY_RSA), None)
        with self.assertRaises(ValidationError):
            validate_sshkey('s  sh-rsa foobar Comm ent')
        with self.assertRaises(ValidationError):
            validate_sshkey(SSH_KEY_RSA + "\n" + SSH_KEY_RSA)


class GroupRuleRegexValidatorTests(TestCase):
    def test_validate_regex(self):
        self.assertIsNone(validate_regex('^web[0-9]+\.example.com$'))
        with self.assertRaisesMessage(ValidationError, 'Rule not valid'):
            validate_regex('^[fadsfsd')