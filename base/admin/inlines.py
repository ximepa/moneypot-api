# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from django.contrib import admin
from django.db import models
from django import forms
import autocomplete_light

from base.models import ItemCategoryComment, PurchaseItem, TransactionItem, Transaction, Place, TransmutationItem
from .forms import ItemCategoryCommentForm, PurchaseItemForm, TransactionItemForm, TransmutationItemForm
from .overrides import InlineReadOnly


class ItemCategoryCommentInline(admin.TabularInline):
    model = ItemCategoryComment
    form = ItemCategoryCommentForm
    extra = 10


class PurchaseItemInlineReadonly(InlineReadOnly):
    model = PurchaseItem
    form = PurchaseItemForm
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
    }

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(PurchaseItemInlineReadonly, self).get_readonly_fields(request, obj)
        readonly_fields.remove('_serials')
        return readonly_fields


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    form = PurchaseItemForm
    extra = 10
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60, '': 'disable'}
        )},
    }


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    form = TransactionItemForm
    extra = 10
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
        models.CharField: {'widget': forms.TextInput(
            attrs={'width': "120px"}
        )},
    }

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(TransactionItemInline, self).get_readonly_fields(request, obj))
        readonly_fields.append("cell_from")
        return readonly_fields


class TransmutationItemInline(admin.TabularInline):
    model = TransmutationItem
    form = TransmutationItemForm
    extra = 10
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(
            attrs={'width': "120px"}
        )},
    }

class TransactionItemInlineReadonly(InlineReadOnly):
    model = TransactionItem
    form = TransactionItemForm
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
    }

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(TransactionItemInlineReadonly, self).get_readonly_fields(request, obj)
        return readonly_fields


class TransmutationItemInlineReadonly(InlineReadOnly):
    model = TransmutationItem
    form = TransmutationItemForm
    extra = 0


class TransactionCommentPlaceInline(admin.TabularInline):
    model = Transaction.comment_places.through
    form = autocomplete_light.modelform_factory(Place, exclude=[])
    extra = 10
