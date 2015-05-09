from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import simplejson

from keymgmt.key import KeyAccess
from keymgmt.forms import SSHAccountForm

from keymgmt.models import (
    Environment,
    SSHKey,
    Group,
    Host,
    SSHKeyring,
    SSHAccount,
    DeleteNotAllowed,
    SSHAccountAvailable,
    GroupRule
)


@csrf_exempt
@require_POST
def api_get_keys(request):
    if hasattr(settings, 'API_KEYS') is False:
        return HttpResponse('API_KEYS in settings not found.', status=401)
    access_token = request.POST.get('API_KEY',  None)
    if access_token is None:
        return HttpResponse('Please send your access token as parameter API_KEY!', status=401)
    if access_token not in settings.API_KEYS:
        return HttpResponse('API access token not found in configuration', status=401)

    filter_type  = request.POST.get('filter_type',  None)
    filter_value = request.POST.get('filter_value',  None)

    if filter_type is not None:
        if filter_value is None:
            return HttpResponse('add filter_value.', status=404)

    key_access = KeyAccess(filter_type=filter_type, filter_value=filter_value)
    hosts = {}
    for host in key_access.all():
        accounts = {}
        for name,keys in host.get_account_merged().items():
            account_keys = []
            for key in keys:
                account_keys.append(key.ssh_key_entry())
            accounts[name] = account_keys
        hosts[host.name] = {
                'ip': host.ipaddress,
                'environment': host.environment.name,
                'accounts': accounts
            }

    return HttpResponse(simplejson.dumps(hosts, sort_keys=True, indent=4))


class AuditKey2Access(TemplateView):
    template_name = 'AuditKey2Access.html'

    def get_context_data(self, **kwargs):
        keys = KeyAccess()
        return {
                'hosts': keys.all()
        }


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        return {
                'account_count': SSHAccount.objects.all().count(),
                'environment_count': Environment.objects.all().count(),
                'host_count': Host.objects.all().count(),
                'group_count': Group.objects.all().count(),
                'sshkey_count': SSHKey.objects.all().count(),
                'sshkeyring_count': SSHKeyring.objects.all().count()
        }


class SSHAccountAvailableList(ListView):
    template_name = 'SSHAccountAvailableList.html'

    def get_queryset(self):
        return SSHAccountAvailable.objects.all()


class SSHAccountAvailableDelete(DeleteView):
    template_name = 'SSHAccountAvailableDelete.html'
    model = SSHAccountAvailable
    success_url = reverse_lazy('sshaccountavailable_list')


    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.add_message(request, messages.INFO, self.object.name + ' was deleted successfully.')
        return HttpResponseRedirect(self.get_success_url())    


class EnvironmentList(ListView):
    template_name = 'EnvironmentList.html'

    def get_queryset(self):
        return Environment.objects.all()


class EnvironmentCreate(SuccessMessageMixin, CreateView):
    template_name = 'EnvironmentCreate.html'
    success_url = reverse_lazy('environment_list')
    success_message = "%(name)s was created successfully"
    model = Environment
    fields = ['name']


class EnvironmentUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'EnvironmentUpdate.html'
    success_url = reverse_lazy('environment_list')
    success_message = "%(name)s was updated successfully"
    model = Environment
    fields = ['name']


class EnvironmentDelete(DeleteView):
    template_name = 'EnvironmentDelete.html'
    model = Environment
    success_url = reverse_lazy('environment_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.add_message(request, messages.INFO, self.object.name + ' was deleted successfully.')
        except DeleteNotAllowed:
            messages.add_message(request, messages.ERROR, self.object.name + ' can not deleted because hosts use that ENV!')
        
        return HttpResponseRedirect(self.get_success_url())


class EnvironmentDetail(DetailView):
    template_name = 'EnvironmentDetail.html'
    model = Environment


class SSHKeyList(ListView):
    template_name = 'SSHKeyList.html'

    def get_queryset(self):
        return SSHKey.objects.all()


class SSHKeyUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'SSHKeyUpdate.html'
    model = SSHKey
    success_url = reverse_lazy('sshkey_list')
    success_message = "%(name)s was updated successfully"
    fields = ['name', 'sshkey']


class SSHKeyCreate(SuccessMessageMixin, CreateView):
    template_name = 'SSHKeyCreate.html'
    success_url = reverse_lazy('sshkey_list')
    success_message = "%(name)s was created successfully"
    model = SSHKey
    fields = ['name', 'sshkey']


class SSHKeyDelete(DeleteView):
    template_name = 'SSHKeyDelete.html'
    model = SSHKey
    success_url = reverse_lazy('sshkey_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.add_message(request, messages.INFO, self.object.name + ' was deleted successfully.')
        return HttpResponseRedirect(self.get_success_url())


class SSHKeyDetail(DetailView):
    template_name = 'SSHKeyDetail.html'
    model = SSHKey


class GroupRuleUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'GroupRuleUpdate.html'
    model = GroupRule
    success_message = "rule %(rule)s was updated successfully"
    fields = ['rule', 'group']


    def get_context_data(self, **kwargs):
        context = super(GroupRuleUpdate, self).get_context_data(**kwargs)
        context['group'] = Group.objects.get(pk=self.kwargs['group_pk'])
        return context


    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'pk': self.kwargs['group_pk']})

class GroupRuleCreate(SuccessMessageMixin, CreateView):
    template_name = 'GroupRuleCreate.html'
    model = GroupRule  
    success_message = "rule %(rule)s was created successfully"
    fields = ['rule', 'group']


    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'pk': self.kwargs['pk']})

    def get_initial(self):
        group = get_object_or_404(Group, pk=self.kwargs.get('pk'))
        return {
            'group': group,
        }
    
    def get_context_data(self, **kwargs):
        context = super(GroupRuleCreate, self).get_context_data(**kwargs)
        context['group'] = Group.objects.get(pk=self.kwargs['pk'])
        return context


class GroupRuleDelete(DeleteView):
    template_name = 'GroupRuleDelete.html'
    model = GroupRule


    def get_success_url(self):
        return reverse_lazy('group_detail', kwargs={'pk': self.kwargs['group_pk']})


    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.add_message(request, messages.INFO, self.object.rule + ' was deleted successfully.')
        return HttpResponseRedirect(self.get_success_url())


class GroupList(ListView):
    template_name = 'GroupList.html'

    def get_queryset(self):
        return Group.objects.all()


class GroupCreate(SuccessMessageMixin, CreateView):
    template_name = 'GroupCreate.html'
    success_url = reverse_lazy('group_list')
    success_message = "%(name)s was created successfully"
    model = Group
    fields = ['name']


class GroupDelete(DeleteView):
    template_name = 'GroupDelete.html'
    model = Group
    success_url = reverse_lazy('group_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.add_message(request, messages.INFO, self.object.name + ' was deleted successfully.')
        return HttpResponseRedirect(self.get_success_url())


class GroupDetail(DetailView):
    template_name = 'GroupDetail.html'
    model = Group


class HostList(ListView):
    template_name = 'HostList.html'

    def get_queryset(self):
        return Host.objects.all()


class HostCreate(SuccessMessageMixin, CreateView):
    template_name = 'HostCreate.html'
    success_url = reverse_lazy('host_list')
    success_message = "%(name)s was created successfully"
    model = Host
    fields = ['name', 'ipaddress', 'environment']


class HostDetail(DetailView):
    template_name = 'HostDetail.html'
    model = Host


class HostUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'HostUpdate.html'
    model = Host
    success_message = "%(name)s was updated successfully"
    fields = ['name', 'environment', 'ipaddress']

    def get_success_url(self):
        return reverse_lazy('host_detail', kwargs={'pk': self.kwargs['pk']})


class HostDelete(DeleteView):
    template_name = 'HostDelete.html'
    model = Host
    success_url = reverse_lazy('host_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.add_message(request, messages.INFO, self.object.name + ' was deleted successfully.')
        return HttpResponseRedirect(self.get_success_url())


class SSHKeyringList(ListView):
    template_name = 'SSHKeyringList.html'

    def get_queryset(self):
        return SSHKeyring.objects.all()


class SSHKeyringCreate(SuccessMessageMixin, CreateView):
    template_name = 'SSHKeyringCreate.html'
    success_url = reverse_lazy('sshkeyring_list')
    success_message = "%(name)s was created successfully"
    model = SSHKeyring
    fields = ['name']

    def get_context_data(self, **kwargs):
        context = super(SSHKeyringCreate, self).get_context_data(**kwargs)
        context['sshkeys'] = simplejson.dumps(SSHKey.all_as_array())
        return context

    def post(self, request, *args, **kwargs):
        post = super(SSHKeyringCreate, self).post(self, request, *args, **kwargs)
        sshkeys = request.POST.get('keys', '')
        if self.object:
            self.object.add_keys(sshkeys)
        return post


class SSHKeyringUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'SSHKeyringUpdate.html'
    model = SSHKeyring
    success_url = reverse_lazy('sshkeyring_list')
    success_message = "%(name)s was updated successfully"
    fields = ['name']
    
    def get_context_data(self, **kwargs):
        context = super(SSHKeyringUpdate, self).get_context_data(**kwargs)
        context['sshkeys'] = simplejson.dumps(SSHKey.all_as_array())
        return context

    def post(self, request, *args, **kwargs):
        post = super(SSHKeyringUpdate, self).post(self, request, *args, **kwargs)
        self.object = self.get_object()
        sshkeys = request.POST.get('keys', '')
        self.object.add_keys(sshkeys)
        return post



class SSHKeyringDelete(DeleteView):
    template_name = 'SSHKeyringDelete.html'
    model = SSHKeyring
    success_url = reverse_lazy('sshkeyring_list')


    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.add_message(request, messages.INFO, self.object.name + ' was deleted successfully.')
        return HttpResponseRedirect(self.get_success_url())


class SSHKeyringDetail(DetailView):
    template_name = 'SSHKeyringDetail.html'
    model = SSHKeyring


class SSHAccountList(TemplateView):
    template_name = 'SSHAccountList.html'

    def get_context_data(self, **kwargs):
        return {
                'object_list_group': SSHAccount.group_objects.all(),
                'object_list_host': SSHAccount.host_objects.all(),
                'object_list_environment': SSHAccount.environment_objects.all()
        }


class SSHAccountDetail(DetailView):
    template_name = 'SSHAccountDetail.html'
    model = SSHAccount


class SSHAccountKeyUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'SSHAccountKeyUpdate.html'
    model = SSHAccount
    fields = []
    success_message = "SSH Keys and SSH Keyrings were updated successfully"

    def post(self, request, *args, **kwargs):
        post = super(SSHAccountKeyUpdate, self).post(self, request, *args, **kwargs)
        self.object = self.get_object()
        keyrings = request.POST.get('keyrings', '')
        self.object.update_keyrings(keyrings)
        keys = request.POST.get('keys', '')
        self.object.update_keys(keys)

        return post

    def get_success_url(self):
        return reverse_lazy('sshaccount_detail', kwargs={'pk': self.kwargs['pk']})


    def get_context_data(self, **kwargs):
        context = super(SSHAccountKeyUpdate, self).get_context_data(**kwargs)
        context['sshkeys'] = simplejson.dumps(SSHKey.all_as_array())
        context['sshkeyrings'] = simplejson.dumps(SSHKeyring.all_as_array())
        return context


class SSHAccountUpdate(SuccessMessageMixin, UpdateView):
    success_url = reverse_lazy('sshaccount_list')
    template_name = 'SSHAccountUpdate.html'
    model = SSHAccount
    form_class = SSHAccountForm
    success_message = "%(name)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super(SSHAccountUpdate, self).get_context_data(**kwargs)
        context['environment_list'] = Environment.objects.all()
        context['group_list'] = Group.objects.all()
        context['host_list'] = Host.objects.all()
        context['sshaccount_available'] = SSHAccountAvailable.all_as_array()
        return context
   

class SSHAccountCreate(SuccessMessageMixin, CreateView):
    model = SSHAccount
    template_name = 'SSHAccountCreate.html'
    form_class = SSHAccountForm
    success_message = "%(name)s was created successfully"

    def get_success_url(self):
        return reverse_lazy('sshaccount_key_update', kwargs={'pk': self.object.id})
    
    def get_context_data(self, **kwargs):
        context = super(SSHAccountCreate, self).get_context_data(**kwargs)
        context['environment_list'] = Environment.objects.all()
        context['group_list'] = Group.objects.all()
        context['host_list'] = Host.objects.all()
        context['create_type'] = self.create_type
        context['sshaccount_available'] = SSHAccountAvailable.all_as_array()
        return context


class SSHAccountCreateEnvironment(SSHAccountCreate):
    create_type = 'environment'
    pass


class SSHAccountCreateHost(SSHAccountCreate):
    create_type = 'host'
    pass


class SSHAccountCreateGroup(SSHAccountCreate):
    create_type = 'group'
    pass


class SSHAccountDelete(DeleteView):
    template_name = 'SSHAccountDelete.html'
    model = SSHAccount
    success_url = reverse_lazy('sshaccount_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.add_message(request, messages.INFO, self.object.name + ' was deleted successfully.')
        return HttpResponseRedirect(self.get_success_url())
