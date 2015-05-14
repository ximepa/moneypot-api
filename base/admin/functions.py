# -*- encoding: utf-8 -*-
from django.contrib import admin


def create_model_admin(model_admin, model, name=None, v_name=None):
    v_name = v_name or name

    class Meta:
        proxy = True
        app_label = model._meta.app_label  # noqa
        verbose_name = v_name

    attrs = {'__module__': '', 'Meta': Meta}

    new_model = type(name, (model,), attrs)
    admin.site.register(new_model, model_admin)
    return model_admin
