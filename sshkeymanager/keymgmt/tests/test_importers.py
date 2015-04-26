from django.test import TestCase
from keymgmt.importer import *
from keymgmt.models import *


class ImportHostTests(TestCase):
    def test_split_line(self):
        self.assertEqual(ImportHost.split_line('web-server1,testing,192.168.0.1'), {'name': 'web-server1', 'env': 'testing', 'ip': '192.168.0.1'} )
        self.assertEqual(ImportHost.split_line('web-server1,testing,'), {'name': 'web-server1', 'env': 'testing', 'ip': None } )
        self.assertEqual(ImportHost.split_line('web-server1,testing'), {'name': 'web-server1', 'env': 'testing', 'ip': None } )
        self.assertEqual(ImportHost.split_line('web-server1'), {'name': 'web-server1', 'env': 'production', 'ip': None } )
        self.assertEqual(ImportHost.split_line('web-server1,'), {'name': 'web-server1', 'env': 'production', 'ip': None } )
        self.assertEqual(ImportHost.split_line(''), None )
        self.assertEqual(ImportHost.split_line('webserver,,12.23.34.32'), { 'name': 'webserver', 'env': 'production', 'ip': '12.23.34.32' } )

    def test_create_or_return_env(self):
        importer = ImportHost('tmp/foobar')
        
        self.assertIsNone(importer.create_or_return_env('foo###bar'))
        self.assertIsNotNone(importer.create_or_return_env('foobar'))

    def test_create_host(self):
        importer = ImportHost('tmp/foobar')
        env = Environment(name='bar')
        env.full_clean()
        env.save()
        self.assertEqual(None, importer.create_host('fsdf#dsafs', env, None))
        self.assertIsNotNone(importer.create_host('fsdfdsafs', env, None))


class ImportSSHKeyTests(TestCase):
    def test_check_option(self):
        """
        tests check option should return type
        """
        importer = ImportSSHKey('fsd')
        self.assertEqual(importer.check_option_mode('/tmp'), 'directory')
        self.assertEqual(importer.check_option_mode('/etc/passwd'), 'file')


class ImportSSHAccountAvailableTest(TestCase):   
    def test_import(self):
        importer = ImportSSHAccountAvailable(['jonas', '  bar', '##fdsfsd'])
        importer.import_names()
        self.assertEqual(importer.import_error, ['##fdsfsd'])
        self.assertEqual(importer.import_success, ['jonas', '  bar'])
        self.assertEqual(SSHAccountAvailable.objects.all().count(), 2)
