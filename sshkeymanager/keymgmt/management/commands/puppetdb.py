from django.core.management.base import BaseCommand
from django.conf import settings
from keymgmt.importer import ImportPuppetdb
from keymgmt.models import Host, Environment, SSHAccountAvailable
from django.core.exceptions import ObjectDoesNotExist, ValidationError
 

class Command(BaseCommand):
    help = 'Import environments and hosts from PuppetDB'


    def handle(self, *args, **options):
        print("Import hosts and environments from PuppetDB")
        
        importer = ImportPuppetdb()
        print("Connecting to: " + importer._url() )
        print("Import Nodes:")
        print("============================")
        nodes = importer.nodes()
        for node in nodes:
            try:
                env = Environment.objects.get(name=node['env'])
            except ObjectDoesNotExist:
                env = Environment(name=node['env'])
                try:
                    env.clean()
                    env.full_clean()
                    env.save()
                except ValidationError:
                    print("Error: could not create environment: " + node['env'])
                    next
            
            try:
                host = Host.objects.get(name=node['name'])
                print("Info: Host " + node['name'] +  " already at database")
                next
            except ObjectDoesNotExist:
                host = Host(name=node['name'], environment=env, ipaddress=node['ip'])
                try:
                    host.clean()
                    host.full_clean()
                    host.save()
                    print("Info: Host " + node['name'] +  " saved into database")
                except ValidationError:
                    print("Error: Host " + node['name'] +  " could not saved to database")

        print("Import SSHAccountAvailable:")
        print("============================")
        users = importer.users()
        for user in users:
            try:
                account = SSHAccountAvailable.objects.get(name=user)
                print("Info: Account " + user + " already at database")
                next
            except ObjectDoesNotExist:
                account = SSHAccountAvailable(name=user)
                try:
                    account.clean()
                    account.full_clean()
                    account.save()
                    print("Info: Account " + user + " saved into database")
                except ValidationError:
                    print("Error: Account "+ user + " could not saved to database")
                    