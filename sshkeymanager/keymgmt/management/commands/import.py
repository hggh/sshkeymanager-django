from django.core.management.base import BaseCommand
from keymgmt.importer import ImportSSHKey, ImportHost, ImportSSHAccountAvailable
import os

HELP_SSHKEY=[
    '  ==== Import SSH Keys ====',
    'Easy import SSH Keys from the filesystem.',
    'You can add as arguments files or directories.',
    'If you import a complete directory, SSH Keys should have the file suffix .pub',
    'The name of the Key will be extracted from the filename.',
    'jonas_genannt.pub will get as name: Jonas Genannt',
    'example:',
    '  ./manage.py import --sshkey /tmp/all_keys',
    '  ./manage.py import --sshkey /home/hggh/.ssh/id_rsa.pub'
]


HELP_HOST=[
    '  ==== Import Hosts ====',
    'Easy import Hosts with environments from a file.',
    'Please add as argument for --host a CSV file.',
    'The csv file should have the following format:',
    'hostname,environment,ip',
    '',
    'The ipaddress is not mandatory, you can omit it.',
    'If you do not enter the environment, the default env production is used',
    'file formats:',
    '',
    'hostname,,ip',
    'hostname',
    'hostname,env',
    'hostname,env,ip'    
]

HELP_SSHACCOUNTAVAILABLE=[
    '  ==== Import available SSH Accounts ====',
    'These import commands imports only SSH Account names that will be available for',
    'autocompletion on the SSH Account page.',
    'You can import multipli account names at once:',
    './manage.py import --sshaccountavailable root jonas bar ...'
]


class Command(BaseCommand):
    help = 'Import SSH Keys and Hosts from Command Line'
    
    
    def add_arguments(self, parser):
        parser.add_argument('--sshkey',
                    nargs='+',
                    default=False,
                    help='Import SSH Keys. For more information use ./manage.py import --sshkey help'
                )
        parser.add_argument('--host',
                    default=False,
                    help='Import Hosts. For more information use ./manage.py --host help',
                )
        parser.add_argument('--sshaccountavailable',
                    nargs='+',
                    default=False,
                    help='Import available SSH Accounts. For more inforation use ./manage.py import --sshaccountavailable help'
                    
                )


    def sshaccountavailable(self, options):
        if ''.join(options['sshaccountavailable']) == 'help':
            print ("\n".join(HELP_SSHACCOUNTAVAILABLE))
            exit(1)
        importer = ImportSSHAccountAvailable(options['sshaccountavailable'])
        importer.import_names()
        
        if len(importer.import_success) > 0:
            print("new names added to the database:")
            for key in importer.import_success:
                print("   " + key)

        if len(importer.import_error) > 0:
            print("Import Errors with the names:")
            for key in importer.import_error:
                print("   " + key)

        if len(importer.import_already) > 0:
            print("Already present in the database")
            for key in importer.import_already:
                print("   " + key)



    def sshkey(self, options):
        if ''.join(options['sshkey']) == 'help':
            print ("\n".join(HELP_SSHKEY))
            exit(1)
        importer = ImportSSHKey(options['sshkey'])
        importer.add_keys_to_db()
            
        if len(importer.sshkeys_added_errors) > 0:
            print("Import Error with keys:")
            for key in importer.sshkeys_added_errors:
                print("    " + key)
            
        if len(importer.sshkeys_added_already) > 0:
            print("Already present in the database:")
            for key in importer.sshkeys_added_already:
                print("    " + key)
            
        if len(importer.sshkeys_added) > 0:
            print("new keys added to the database:")
            for key in importer.sshkeys_added:
                print("    " + key)


    def host(self, options):
        if options['host'] == 'help':
            print("\n".join(HELP_HOST))
            exit(1)
        if os.path.isfile(options['host']) and os.access(options['host'], os.R_OK):
            print("==== Starting import of hosts from: ", options['host'])
            importer = ImportHost(options['host'])
            importer.read_file()
            importer.import_host()
            #print(importer.content)
            print("Import Host OK:")
            for key in importer.import_ok:
                print("   ", key)
            print("Import Host Errors:")
            for key in importer.import_errors:
                print("   ", key)
            print("Already available at database:")
            for key in importer.import_already:
                print("   ", key)
        else:
            print("The filename " , options['host'], " is not available or not readable")
            exit(1)

    def handle(self, *args, **options):
        
        if options['sshkey']:
            self.sshkey(options)
        elif options['host']:
            self.host(options)
        elif options['sshaccountavailable']:
            self.sshaccountavailable(options)
        else:
            print("Please see --help for more information")
            exit(1)