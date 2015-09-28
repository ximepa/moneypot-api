# -*- encoding: utf-8 -*-
__author__ = 'maxim'
from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from copy import deepcopy
from .functions import parse_serials_data
import autocomplete_light
import re

from base.models import InvalidParameters, ItemCategory, ItemCategoryComment, Place, PurchaseItem, TransactionItem, Purchase, \
    Transaction, Unit, ItemSerial, FixCategoryMerge, Cell, CellItem


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

    def clean(self):

        cleaned_data = dict(self.cleaned_data)

        _serials = cleaned_data.get('_serials', "")
        category = cleaned_data.get('category', None)

        try:
            serials_data = parse_serials_data(_serials)
        except InvalidParameters, e:
            raise forms.ValidationError({'_serials': e})

        if len(serials_data) and category and category.unit.unit_type == Unit.DECIMAL:
            raise forms.ValidationError({'_serials': ugettext(
                'unit type `%s` can not have serials' % self.category.unit.name
            )})

        self.cleaned_data['_serials'] = ", ".join(serials_data)

        return self.cleaned_data


class TransactionItemForm(autocomplete_light.ModelForm):
    _serials = forms.CharField(required=False, label=_("serials"), widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}))
    serials = []

    class Meta:
        model = TransactionItem
        exclude = ['_chunks', 'purchase']
        autocomplete_fields = ('category', 'serial', 'destination')

    def clean(self):
        self.serials = []
        cleaned_data = dict(self.cleaned_data)

        _serials = cleaned_data.get('_serials', "")
        serial = cleaned_data.get('serial', None)

        if _serials and serial:
            raise forms.ValidationError({'serial': ugettext(
                "can't set serial when serial list not empty"
            )})

        quantity = cleaned_data.get('quantity', 0)
        category = cleaned_data.get('category', None)
        transaction = cleaned_data.get('transaction', None)

        try:
            serials_data = parse_serials_data(_serials)
        except InvalidParameters, e:
            raise forms.ValidationError({'_serials': e})

        if len(serials_data) and category and category.unit.unit_type == Unit.DECIMAL:
            raise forms.ValidationError({'_serials': ugettext(
                'unit type `%s` can not have serials' % self.category.unit.name
            )})

        self.cleaned_data['_serials'] = ", ".join(serials_data)

        if len(serials_data) and not quantity == len(serials_data):
            raise forms.ValidationError({'_serials': ugettext(
                u'serials count error: {count}≠{quantity}'.format(count=len(serials_data), quantity=quantity)
            )})

        for serial in serials_data:
            try:
                sr = ItemSerial.objects.get(serial=serial, item__category=category, item__place=transaction.source)
            except ItemSerial.DoesNotExist:
                raise forms.ValidationError({'_serials': ugettext(
                    u'serial <{serial}> <{category}> not found in <{place}>'.format(
                        serial=serial,
                        category=unicode(category),
                        place=unicode(transaction.source) if transaction else "<unknown place>"
                    )
                )})
            else:
                self.serials.append(sr)

        self.cleaned_data['_serials'] = self.serials
        return self.cleaned_data

    def save(self, *args, **kwargs):
        ti = super(TransactionItemForm, self).save(*args, **kwargs)
        if ti.transaction.is_completed:
            ti.transaction.reset()
        if self.serials:
            for serial in self.serials:
                nti = deepcopy(ti)
                nti.pk = None
                nti.quantity = 1
                nti.serial = serial
                nti.save()
            setattr(ti, "trash", True)
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


class FixCategoryMergeForm(autocomplete_light.ModelForm):
    class Meta:
        model = FixCategoryMerge
        exclude = []


class CellForm(autocomplete_light.ModelForm):
    class Meta:
        model = Cell
        exclude = []


class CellItemForm(autocomplete_light.ModelForm):
    class Meta:
        model = CellItem
        exclude = []