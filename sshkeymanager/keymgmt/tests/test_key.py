from django.test import TestCase
from keymgmt.importer import *
from keymgmt.models import *
from keymgmt.key import *

class KeyAccessTests(TestCase):
    def test_filters(self):
        with self.assertRaisesMessage(ExceptionFilterTypeIncorret, 'filter type not allowed'):
            key = KeyAccess(filter_type='foobar')
        with self.assertRaisesMessage(ExceptionFilterValueMissing, 'please add filter value'):
            key = KeyAccess(filter_type='group')