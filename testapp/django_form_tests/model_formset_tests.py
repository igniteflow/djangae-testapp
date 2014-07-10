from django.test import TestCase
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from django.test.client import RequestFactory

from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import testbed

from testapp.models import TestModel


class ModelFormsetTest(TestCase):

    def setUp(self):
        super(ModelFormsetTest, self).setUp()
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_all_stubs()
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

    def test_reproduce_index_error(self):
        class TestModelForm(ModelForm):
            class Meta:
                model = TestModel

        test_model = TestModel.objects.create(field1='foo', field2='bar')
        TestModelFormSet = modelformset_factory(TestModel, form=TestModelForm, extra=0)
        test_model_formset = TestModelFormSet(queryset=TestModel.objects.filter(pk=test_model.pk))

        data = {
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 0,
            'form-TOTAL_FORMS': 0,
            'form-0-id': test_model.id,
            'form-0-field1': 'foo_1',
            'form-0-field2': 'bar_1',
        }
        factory = RequestFactory()
        request = factory.post('/', data=data)

        with self.assertRaises(IndexError):
            TestModelFormSet(request.POST, request.FILES)