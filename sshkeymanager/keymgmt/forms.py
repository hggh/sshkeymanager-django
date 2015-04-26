from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from keymgmt.models import SSHAccount


class SSHAccountForm(forms.ModelForm):
    def clean_obj_id(self):
        return self.cleaned_data['obj_id']

    class Meta:
        model = SSHAccount
        fields = ['name', 'obj_id', 'obj_name']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': 'Account already exists.'
            }
        }
