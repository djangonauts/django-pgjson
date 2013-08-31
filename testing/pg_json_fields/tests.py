# -*- coding: utf-8 -*-

from django.contrib.admin import AdminSite, ModelAdmin

from django.test import TestCase
from django.core.serializers import serialize, deserialize

from djorm_expressions.base import SqlExpression
from djorm_pgjson.fields import JSONField

from .models import TextModel


class JSONFieldTests(TestCase):
    def setUp(self):
        TextModel.objects.all().delete()

    def test_empty_create(self):
        instance = TextModel.objects.create(data={})
        instance = TextModel.objects.get(pk=instance.pk)
        self.assertEqual(instance.data, {})

    def test_unicode(self):
        obj = TextModel.objects.create(data=[u"Fóö", u"Пример", u"test"])
        obj = TextModel.objects.get(pk=obj.pk)

        self.assertEqual(obj.data[1], u"Пример")

    def test_correct_behavior_with_text(self):
        obj = TextModel.objects.create(data="hello")
        obj = TextModel.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, "hello")

    def test_correct_behavior_with_bool(self):
        obj = TextModel.objects.create(data=True)
        obj = TextModel.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, True)

    def test_correct_behavior_with_int(self):
        obj = TextModel.objects.create(data=1)
        obj = TextModel.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, 1)

    def test_correct_behavior_with_float_01(self):
        obj = TextModel.objects.create(data=1.4)
        obj = TextModel.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, 1.4)

    def test_correct_behavior_with_float_02(self):
        obj = TextModel.objects.create(data=0.4)
        obj = TextModel.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, 0.4)

    def test_value_to_string_serializes_correctly(self):
        obj = TextModel.objects.create(data=[1,2,3])

        serialized_obj = serialize('json', TextModel.objects.filter(pk=obj.pk))
        obj.delete()

        deserialized_obj = list(deserialize('json', serialized_obj))[0]

        obj = deserialized_obj.object
        obj.save()

        self.assertEqual(obj.data, [1,2,3])

    def test_to_python_serializes_xml_correctly(self):
        obj = TextModel.objects.create(data={"a": 0.2})

        serialized_obj = serialize('xml', TextModel.objects.filter(pk=obj.pk))

        obj.delete()
        deserialized_obj = list(deserialize('xml', serialized_obj))[0]

        obj = deserialized_obj.object
        obj.save()

        self.assertEqual(obj.data, {"a": 0.2})

    def test_can_override_formfield(self):
        model_field = JSONField()
        class FakeFieldClass(object):
            def __init__(self, *args, **kwargs):
                pass
        form_field = model_field.formfield(form_class=FakeFieldClass)
        self.assertIsInstance(form_field, FakeFieldClass)


#class ArrayFormFieldTests(TestCase):
#    def test_regular_forms(self):
#        form = IntArrayForm()
#        self.assertFalse(form.is_valid())
#        form = IntArrayForm({'data':u'[1,2]'})
#        self.assertTrue(form.is_valid())
#
#    def test_empty_value(self):
#        form = IntArrayForm({'data':u''})
#        self.assertTrue(form.is_valid())
#        self.assertEqual(form.cleaned_data['data'], [])
#
#    def test_admin_forms(self):
#        site = AdminSite()
#        model_admin = ModelAdmin(TextModel, site)
#        form_clazz = model_admin.get_form(None)
#        form_instance = form_clazz()
#
#        try:
#            form_instance.as_table()
#        except TypeError:
#            self.fail('HTML Rendering of the form caused a TypeError')
#
#    def test_invalid_error(self):
#        form = IntArrayForm({'data':1})
#        self.assertFalse(form.is_valid())
#        self.assertEqual(
#            form.errors['data'],
#            [u'Enter a list of values, joined by commas.  E.g. "a,b,c".']
#            )
