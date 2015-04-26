from keymgmt.models import Host, Environment, SSHAccount, Group

class ExceptionFilterValueMissing(Exception):
    pass


class ExceptionFilterTypeIncorret(Exception):
    pass


class KeyAccess:
    FILTER_TYPES = [ 'environment', 'group', 'host']
    def __init__(self, filter_type=None, filter_value=None):
        self.hosts = Host.objects.all()
        if filter_type is not None:
            if filter_type not in self.FILTER_TYPES:
                raise ExceptionFilterTypeIncorret('filter type not allowed')
            if filter_value is None:
                raise ExceptionFilterValueMissing('please add filter value')
            
            if filter_type == 'environment':
                self.hosts = self.hosts.filter(environment__name=filter_value)

            if filter_type == 'group':
                self.hosts = self.hosts.filter(group__name=filter_value)

            if filter_type == 'host':
                self.hosts = self.hosts.filter(name=filter_value)

    def all(self):
        return self.hosts