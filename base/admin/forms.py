# -*- encoding: utf-8 -*-
__author__ = 'maxim'
from django import forms
from django.utils.translation import ugettext_lazy as _
import autocomplete_light

from base.models import ItemCategory, ItemCategoryComment, Place, PurchaseItem, TransactionItem, Purchase, Transaction


class ItemCategoryCommentForm(autocomplete_light.ModelForm):
    class Meta:
        model = ItemCategoryComment
        exclude = []


class ItemCategoryForm(autocomplete_light.ModelForm):
    class Meta:
        model = ItemCategory
        exclude = []


class PlaceForm(autocomplete_light.ModelForm):
    class Meta:
        model = Place
        exclude = []


class PurchaseItemForm(autocomplete_light.ModelForm):
    class Meta:
        model = PurchaseItem
        exclude = ['_chunks']


class TransactionItemForm(autocomplete_light.ModelForm):
    class Meta:
        model = TransactionItem
        exclude = ['_chunks', 'purchase']
        autocomplete_fields = ('category', 'serial')

    def save(self, *args, **kwargs):
        ti = super(TransactionItemForm, self).save(*args, **kwargs)
        if ti.transaction.is_completed:
            ti.transaction.reset()
        return ti


class PurchaseForm(autocomplete_light.ModelForm):
    force_complete = forms.BooleanField(required=False, label=_("force complete"))

    class Meta:
        model = Purchase
        exclude = ['is_completed', 'is_prepared']

    def save(self, *args, **kwargs):
        p = super(PurchaseForm, self).save(*args, **kwargs)
        if self.cleaned_data['force_complete']:
            if p.is_completed:
                raise RuntimeError(_("already completed"))
            # try:
            p.complete()
            # except Exception, e:
            # raise forms.ValidationError(e)
        return p


class TransactionForm(autocomplete_light.ModelForm):
    force_complete = forms.BooleanField(required=False, label=_("force complete"))

    class Meta:
        model = Transaction
        exclude = ['comment_places', 'is_completed', 'is_prepared', 'is_negotiated_source',
                   'is_negotiated_destination', 'is_confirmed_source', 'is_confirmed_destination']
        autocomplete_fields = ('source', 'destination', 'items')

    def save(self, *args, **kwargs):
        t = super(TransactionForm, self).save(*args, **kwargs)
        if self.cleaned_data['force_complete']:
            if t.is_completed:
                raise RuntimeError(_("already completed"))
            # try:
            t.force_complete()
            # except Exception, e:
            # raise forms.ValidationError(e)
        return t

