# -*- encoding: utf-8 -*-
__author__ = 'maxim'
from copy import deepcopy

from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.admin.helpers import ActionForm
import autocomplete_light

from .functions import parse_serials_data
from base.models import InvalidParameters, ItemCategory, ItemCategoryComment, Place, PurchaseItem, TransactionItem, Purchase, \
    Transaction, Unit, ItemSerial, FixCategoryMerge, FixPlaceMerge, Cell, Item, ItemChunk


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
            p.complete(pending=True)
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
            t.force_complete(pending=True)
            # except Exception, e:
            # raise forms.ValidationError(e)
        return t


class FixCategoryMergeForm(autocomplete_light.ModelForm):
    class Meta:
        model = FixCategoryMerge
        exclude = []


class FixPlaceMergeForm(autocomplete_light.ModelForm):
    class Meta:
        model = FixPlaceMerge
        exclude = []


class CellForm(autocomplete_light.ModelForm):

    place = forms.ModelChoiceField(queryset=Place.objects.filter(has_cells=1), empty_label=None)

    class Meta:
        model = Cell
        exclude = []


class CellItemActionForm(ActionForm):

    @staticmethod
    def cell_choices():
        return Cell.objects.all().values_list("id", "name")

    cell = forms.ModelChoiceField(queryset=Cell.objects.all())
    # all_serials = forms.ChoiceField(choices=(
    #     (0, '----------',),
    #     (1, _('update all serials'))
    # ))


class ItemInlineForm(autocomplete_light.ModelForm):

    class Meta:
        model = Item
        fields = ['cell']