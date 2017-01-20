# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

import autocomplete_light
from django import forms
from django.contrib import admin
from django.db import models

from base.models import  TransactionItem,  Place, ReturnItem
from .forms import  TransactionItemForm, ReturnItemForm
from base.admin.overrides import InlineReadOnly


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    form = TransactionItemForm
    extra = 10
    fields = ['category', 'quantity', 'serial', 'chunk']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
        models.CharField: {'widget': forms.TextInput(
            attrs={'width': "120px"}
        )},
    }


class TransactionItemDestinationInline(admin.TabularInline):
    model = TransactionItem
    form = TransactionItemForm
    extra = 10
    fields = ['category', 'quantity', 'serial', 'chunk', 'destination']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
        models.CharField: {'widget': forms.TextInput(
            attrs={'width': "120px"}
        )},
    }


class TransactionItemInlineReadonly(InlineReadOnly):
    model = TransactionItem
    form = TransactionItemForm
    extra = 0
    fields = ['category', 'quantity', 'serial', 'chunk']
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
    }


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    form = ReturnItemForm
    extra = 10
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(
            attrs={'width': "120px"}
        )},
    }


class ReturnItemInlineReadonly(InlineReadOnly):
    model = ReturnItem
    form = ReturnItemForm
    extra = 0
