from django.core.exceptions import ValidationError
import re
import sre_constants


def validate_regex(value):
    if value:
        try:
            reg = re.compile(value)
        except sre_constants.error:
            raise ValidationError('Rule not valid')


def validate_sshkey(value):
    if value:
        value = value.strip().rstrip()
    if re.search(r'^(ecdsa-sha2-nistp256|ssh-dss|ssh-rsa)\s([^\s\n]+) [^\n]+$', value) is None:
        raise ValidationError('%s is not a valid SSH Public Key' % value)
