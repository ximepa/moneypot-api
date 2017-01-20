# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from copy import deepcopy
from datetime import datetime

import autocomplete_light
from django import forms
from django.contrib.admin.helpers import ActionForm
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _, ugettext

from base.admin.validators import validate_place_name
from base.models import InvalidParameters, ItemCategory, ItemCategoryComment, Place, PurchaseItem, TransactionItem, \
    Purchase, Transaction, Unit, ItemSerial, FixCategoryMerge, FixPlaceMerge, Cell, Item, ItemChunk, Transmutation, \
    TransmutationItem, Warranty, Return, ReturnItem
from base.admin.functions import parse_serials_data

from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

PLACE_UNSORTED_ID = settings.APP_FILTERS['PLACE_UNSORTED_ID']
GROUP_WORKERS_ID = settings.APP_FILTERS['GROUP_WORKERS_ID']


class WorkersAdminAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form used in the admin app.
    """
    error_messages = {
        'invalid_login': _("Please enter the correct %(username)s and password "
                           "for a worker account. Note that both fields may be "
                           "case-sensitive."),
        'invalid_group': _("You have no access to workers group. Please contact "
                           "your administrator and ask him to grant you access. "),
    }
    required_css_class = 'required'

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )
        try:
            user.groups.get(pk=GROUP_WORKERS_ID)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                self.error_messages['invalid_group'],
                code='invalid_group',
                params={'username': self.username_field.verbose_name}
            )


class ItemCategoryCommentForm(autocomplete_light.ModelForm):
    class Meta:
        model = ItemCategoryComment
        exclude = []


class ItemCategoryForm(autocomplete_light.ModelForm):
    class Meta:
        model = ItemCategory
        exclude = []


class ItemChunkForm(autocomplete_light.ModelForm):
    class Meta:
        model = ItemChunk
        exclude = []


class ItemSerialForm(autocomplete_light.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ItemSerialForm, self).__init__(*args, **kwargs)
        if "purchase" in self.fields:
            self.fields["purchase"].required = True

    def clean_serial(self):
        serial = self.cleaned_data.get("serial", None)
        try:
            s = ItemSerial.objects.get(serial=serial)
        except ItemSerial.DoesNotExist:
            return serial
        else:
            raise forms.ValidationError("Serial not unique. Item: <%s>" % s.item)

    def clean_item(self):
        item = self.cleaned_data.get("item", None)
        if not item or not item.category.unit.unit_type == Unit.INTEGER:
            raise forms.ValidationError("this item category can not have serial")
        if item.quantity < 1:
            raise forms.ValidationError("item quantity not enough: %s" % item.quantity)
        return item

    def clean(self):
        purchase_item = self.cleaned_data.get("purchase", None)

        item = self.cleaned_data.get("item", None)
        serial = self.cleaned_data.get("serial", None)
        if not purchase_item or not item or not serial:
            raise forms.ValidationError("fill all required fields")
        purchase = purchase_item.purchase
        if not purchase_item.category == item.category:
            raise forms.ValidationError({"purchase": "invalid purchase for this item"})
        tis = TransactionItem.objects.filter(
            purchase=purchase,
            transaction__source=purchase.source,
            transaction__destination=purchase.destination,
            category_id=item.category_id,
            serial=None
        ).order_by('quantity')
        if not tis.count():
            raise forms.ValidationError("Can't find transaction to add serial!")
        else:
            setattr(self, 'ti', tis[0])
            setattr(self, 'pi', purchase_item)
        return self.cleaned_data

    def save(self, commit=True):
        if not hasattr(self, 'ti') or not hasattr(self, 'pi'):
            raise RuntimeError("Can't find transaction to add serial!")
        serial = super(ItemSerialForm, self).save(commit)
        if not commit:
            serial.save()

        ti = self.ti
        if ti.quantity == 1:
            ti.serial = serial
            ti.save()
        elif ti.quantity > 1:
            ti.quantity -= 1
            ti.save()
            data = dict(
                transaction=ti.transaction,
                purchase=ti.purchase,
                category=ti.category,
                quantity=1,
                serial=serial,
                destination=ti.transaction.destination,
                cell=serial.cell
            )
            TransactionItem.objects.create(**data)
        return serial

    class Meta:
        model = ItemSerial
        fields = ['item', 'purchase', 'serial', 'cell', 'comment']


class PlaceForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        return validate_place_name(name)

    def save(self, commit=True):
        instance = super(PlaceForm, self).save(commit=False)
        instance.parent_id = PLACE_UNSORTED_ID
        instance.save()
        return instance

    class Meta:
        model = Place
        fields = ('name', )


class TransactionItemForm(autocomplete_light.ModelForm):
    _serials = forms.CharField(required=False, label=_("serials"), widget=forms.Textarea(attrs={'cols': 80, 'rows': 1}))
    serials = []

    class Meta:
        model = TransactionItem
        fields = ['quantity']
        autocomplete_fields = ('category', 'serial', 'chunk', 'destination')

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
        except InvalidParameters as e:
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
                        category=category,
                        place=transaction.source if transaction else "<unknown place>"
                    )
                )})
            else:
                self.serials.append(sr)

        self.cleaned_data['_serials'] = self.serials

        # serial = cleaned_data.get("serial", None)
        # # if serial and not serial.item.place == transaction.source:
        # #     raise forms.ValidationError(({'serial': ugettext(
        # #         'serial not found: {}. It is in {}'.format(serial, serial.item.place)
        # #     )}))

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


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['comment', ]


class TransactionDestinationForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['comment', 'destination' ]


class ReturnItemForm(autocomplete_light.ModelForm):
    class Meta:
        model = ReturnItem
        fields = ['category', 'quantity', 'serial', 'source']
        autocomplete_fields = ('category', 'source')

    def clean(self):
        cleaned_data = dict(self.cleaned_data)
        serial = cleaned_data.get('serial', None)
        chunk = cleaned_data.get('chunk', None)
        quantity = cleaned_data.get('quantity', 0)

        if serial and not quantity == 1:
            raise forms.ValidationError({'quantity': "if serial is set, quantity = 1"})

        if chunk and quantity > chunk.chunk:
            raise forms.ValidationError({'quantity': "if chunk is set, quantity <= chunk length"})

        return self.cleaned_data


class ReturnForm(autocomplete_light.ModelForm):
    class Meta:
        model = Return
        exclude = ['comment_places', 'is_completed', 'is_prepared', 'is_negotiated_source',
                   'is_negotiated_destination', 'is_confirmed_source', 'is_confirmed_destination',
                   'source', 'destination', 'completed_at', 'created_at']
        autocomplete_fields = ('source', 'destination', 'items')

    def save(self, commit=False):
        t = super(ReturnForm, self).save(commit=False)
        t.created_at = datetime.now()
        return t
