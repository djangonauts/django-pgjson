djorm-ext-pgjson
================

PostgreSQL native json field for Django.


Introduction
------------

Django by default, has a large collection of possible types that can be used to define the
model. But sometimes we need to use some more complex types offered by PostgreSQL. In this
case, we will look the integrating of PostgreSQL native json field with Django.

Quickstart
----------

**djorm-ext-pgjson** exposes a simple django model field `djorm_pgjson.fields.JSONField`.

This is a sample definition of model using a JSONField:

.. code-block:: python

    from django.db import models
    from djorm_pgjson.fields import JSONField
    from djorm_expressions.models import ExpressionManager

    class Register(models.Model):
        name = models.CharField(max_length=200)
        points = JSONField()
        objects = ExpressionManager()


.. note::

    After PostgreSQL 9.3 is releases, you can use **djorm-ext-expressions** for make
    complex lookups using PostgreSQL native query operators. PostgreSQL 9.2 only supports
    storing data on the field.


Creating objects
~~~~~~~~~~~~~~~~

This is a sample example of creating objects with array fields.

.. code-block:: pycon

    >>> Register.objects.create(points=[1,2,3,4])
    <Register: Register object>

    >>> Register.objects.create(points={"1":2, "3":4})
    <Register: Register object>


How install it?
---------------

You can clone the repo from github and install with simple python setup.py install
command. Or use a pip, for install it from Python Package Index.

.. code-block:: console

    pip install djorm-ext-pgjson

Additionally, you can install djorm-ext-expressions, that can help with complex queries
using json fields (see previous note).
