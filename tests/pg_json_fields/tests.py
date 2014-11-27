# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django
from django.contrib.admin import AdminSite, ModelAdmin

from django.test import TestCase
from django.core.serializers import serialize, deserialize
from django_pgjson.fields import JsonField, JsonBField

from .models import TextModel, TextModelB, TextModelWithDefault


class JsonFieldTests(TestCase):
    def setUp(self):
        self.model_class = TextModel
        self.model_class.objects.all().delete()

    def test_default_create(self):
        instance1 = TextModelWithDefault.objects.create()
        instance2 = TextModelWithDefault.objects.get(pk=instance1.pk)

        self.assertEqual(instance1.data, {})
        self.assertEqual(instance2.data, {})

    def test_empty_create(self):
        instance = self.model_class.objects.create(data={})
        instance = self.model_class.objects.get(pk=instance.pk)
        self.assertEqual(instance.data, {})

    def test_unicode(self):
        obj = self.model_class.objects.create(data={"list": ["Fóö", "Пример", "test"]})
        obj = self.model_class.objects.get(pk=obj.pk)
        self.assertEqual(obj.data["list"][1], "Пример")

    def test_array_serialization(self):
        obj = self.model_class.objects.create(data=["Fóö", "Пример", "test"])
        obj = self.model_class.objects.get(pk=obj.pk)
        self.assertEqual(obj.data[1], "Пример")

    def test_primitives_bool(self):
        obj = self.model_class.objects.create(data=True)
        obj = self.model_class.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, True)

    def test_primitives_str(self):
        obj = self.model_class.objects.create(data="Fóö")
        obj = self.model_class.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, "Fóö")

    def test_primitives_str_valid_json(self):
        obj = self.model_class.objects.create(data='["Fóö", 3.1415]')
        obj = self.model_class.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, ["Fóö", 3.1415])

    def test_primitives_int(self):
        obj = self.model_class.objects.create(data=3)
        obj = self.model_class.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, 3)

    def test_primitives_float(self):
        obj = self.model_class.objects.create(data=3.0)
        obj = self.model_class.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, 3.0)

    def test_primitives_null(self):
        obj = self.model_class.objects.create(data=None)
        obj = self.model_class.objects.get(pk=obj.pk)
        self.assertEqual(obj.data, None)

    def test_value_to_string_serializes_correctly(self):
        obj = self.model_class.objects.create(data={"a": 1})

        serialized_obj = serialize('json', self.model_class.objects.filter(pk=obj.pk))
        obj.delete()

        deserialized_obj = list(deserialize('json', serialized_obj))[0]

        obj = deserialized_obj.object
        obj.save()
        obj = obj.__class__.objects.get(pk=obj.pk)

        self.assertEqual(obj.data, {"a": 1})

    def test_to_python_serializes_xml_correctly(self):
        obj = self.model_class.objects.create(data={"a": 0.2})

        serialized_obj = serialize('xml', self.model_class.objects.filter(pk=obj.pk))

        obj.delete()
        deserialized_obj = list(deserialize('xml', serialized_obj))[0]

        obj = deserialized_obj.object
        obj.save()
        obj = obj.__class__.objects.get(pk=obj.pk)

        self.assertEqual(obj.data, {"a": 0.2})

    def test_can_override_formfield(self):
        model_field = JsonField()
        class FakeFieldClass(object):
            def __init__(self, *args, **kwargs):
                pass
        form_field = model_field.formfield(form_class=FakeFieldClass)
        self.assertIsInstance(form_field, FakeFieldClass)


if django.VERSION[:2] > (1, 6):
    class JsonLookupsFieldTests(TestCase):
        def setUp(self):
            self.model_class = TextModel
            self.model_class.objects.all().delete()

        def test_key_lookup(self):
            obj1 = self.model_class.objects.create(data={"name": "foo"})
            obj2 = self.model_class.objects.create(data={"name": "bar"})

            qs = self.model_class.objects.filter(data__at_name="foo")
            self.assertEqual(qs.count(), 1)

        def test_key_lookup2(self):
            obj1 = self.model_class.objects.create(data={"name": {"full": "foo"}})
            obj2 = self.model_class.objects.create(data={"name": {"full": "bar"}})
            qs = self.model_class.objects.filter(data__at_name={"full": "foo"})
            self.assertEqual(qs.count(), 1)

        def test_key_lookup3(self):
            obj1 = self.model_class.objects.create(data={"num": 2})
            obj2 = self.model_class.objects.create(data={"num": 3})
            qs = self.model_class.objects.filter(data__at_num=2)
            self.assertEqual(qs.count(), 1)

        def test_key_lookup4(self):
            obj1 = self.model_class.objects.create(data=[1,2,3,4])
            obj2 = self.model_class.objects.create(data=[5,6,7,8])

            qs = self.model_class.objects.filter(data__at_2=3)
            self.assertEqual(qs.count(), 1)

        def test_key_lookup5(self):
            obj1 = self.model_class.objects.create(data=[{"foo": 1}])
            obj2 = self.model_class.objects.create(data=[{"bar": 1}])

            qs = self.model_class.objects.filter(data__at_0={"foo": 1})
            self.assertEqual(qs.count(), 1)

        def test_array_length(self):
            obj1 = self.model_class.objects.create(data=[1,2,3])
            obj2 = self.model_class.objects.create(data=[5,6,7,8,9])

            qs = self.model_class.objects.filter(data__array_length=3)
            self.assertEqual(qs.count(), 1)


class JsonBFieldTests(JsonFieldTests):
    def setUp(self):
        self.model_class = TextModelB

    def test_jcontains_lookup1(self):
        obj1 = self.model_class.objects.create(data=[1, 2, [1, 3]])
        obj2 = self.model_class.objects.create(data=[4, 5, 6])

        qs = self.model_class.objects.filter(data__jcontains=[[1, 3]])
        self.assertEqual(qs.count(), 1)

        qs = self.model_class.objects.filter(data__jcontains=[4, 6])
        self.assertEqual(qs.count(), 1)

        qs = self.model_class.objects.filter(data__jcontains='[4, 6]')
        self.assertEqual(qs.count(), 1)

    def test_jcontains_lookup2(self):
        obj1 = self.model_class.objects.create(data={"title": "An action story", "tags": ["violent", "romantic"]})
        obj1 = self.model_class.objects.create(data={"title": "A sad story", "tags": ["sad", "romantic"]})
        obj2 = self.model_class.objects.create(data=[4, 5, 6])

        qs = self.model_class.objects.filter(data__jcontains={"tags": ["sad"]})
        self.assertEqual(qs.count(), 1)



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
#        model_admin = ModelAdmin(self.model_class, site)
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
