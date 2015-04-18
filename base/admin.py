from django.contrib import admin
from django import forms
from django.db import models
from mptt.admin import MPTTModelAdmin
from django_mptt_admin.admin import DjangoMpttAdmin
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf.urls import patterns, include, url

from base.models import Unit, ItemCategory, Place, PurchaseItem, Payer, Purchase, Item, ItemSerial, ItemChunk, \
    TransactionItem, Transaction

import autocomplete_light


def create_model_admin(model_admin, model, name=None):
    class  Meta:
        proxy = True
        app_label = model._meta.app_label

    attrs = {'__module__': '', 'Meta': Meta}

    new_model = type(name, (model,), attrs)
    admin.site.register(new_model, model_admin)
    return model_admin


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemCategory)
class ItemCategoryAdmin(DjangoMpttAdmin):
    search_fields = ['name',]
    tree_auto_open = False


@admin.register(Place)
class PlaceAdmin(DjangoMpttAdmin):
    search_fields = ['name',]
    tree_auto_open = False


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Payer)
class PayerAdmin(admin.ModelAdmin):
    search_fields = ['name',]


class PurchaseItemForm(autocomplete_light.ModelForm):
    class Meta:
        model = PurchaseItem
        exclude = ['_chunks']


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    form = PurchaseItemForm
    extra = 10
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
    }


class PurchaseForm(autocomplete_light.ModelForm):
    force_complete = forms.BooleanField(required=False, label=_("force complete"))

    class Meta:
        model = Purchase
        exclude = ['is_completed', 'is_prepared']

    def save(self, *args, **kwargs):
        p = super(PurchaseForm, self).save(*args, **kwargs)
        if self.cleaned_data['force_complete']:
            try:
                p.complete()
            except Exception, e:
                raise forms.ValidationError(e)
        return p


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
    inlines = [PurchaseItemInline,]
    list_display = ['__unicode__', 'created_at', 'completed_at', 'source', 'destination', 'is_completed', 'is_prepared',]
    list_filter = ['source', 'destination', 'is_completed', 'is_prepared',]
    search_fields = ['source__name', 'destination__name', 'purchase_items__category__name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ['category__name', 'place__name']
    list_filter = ['category',]
    list_display = ['__unicode__', 'quantity', 'place']


@admin.register(ItemSerial)
class ItemSerialAdmin(admin.ModelAdmin):
    search_fields = ['item__category__name']
    list_filter = ['item__category',]


@admin.register(ItemChunk)
class ItemChunkAdmin(admin.ModelAdmin):
    search_fields = ['item__category__name']
    list_filter = ['item__category',]


class TransactionItemForm(autocomplete_light.ModelForm):
    class Meta:
        model = TransactionItem
        exclude = ['_chunks', 'purchase']
        autocomplete_fields = ('category',)

    def save(self, *args, **kwargs):
        ti = super(TransactionItemForm, self).save(*args, **kwargs)
        if ti.transaction.is_completed:
            print
            print "TRANSACTION RESET"
            ti.transaction.reset()
        return ti


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    pass


class TransactionForm(autocomplete_light.ModelForm):
    force_complete = forms.BooleanField(required=False, label=_("force complete"))

    class Meta:
        model = Transaction
        exclude = ['is_completed', 'is_prepared', 'is_negotiated_source',
                   'is_negotiated_destination', 'is_confirmed_source', 'is_confirmed_destination']
        autocomplete_fields = ('source', 'destination', 'items')

    def save(self, *args, **kwargs):
        t = super(TransactionForm, self).save(*args, **kwargs)
        if self.cleaned_data['force_complete']:
            try:
                t.force_complete()
            except Exception, e:
                raise forms.ValidationError(e)
        return t


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    form = TransactionItemForm
    extra = 10
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
    }


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    class Media:
        js = ('base/js/transaction_source_item_autocomplete.js',)

    form = TransactionForm
    list_display = ['__unicode__', 'created_at', 'completed_at', 'source', 'destination', 'is_completed', 'is_prepared',
                    'is_negotiated_source', 'is_negotiated_destination', 'is_confirmed_source',
                    'is_confirmed_destination']
    list_filter = ['source', 'destination', 'is_completed', 'is_prepared',
                   'is_negotiated_source', 'is_negotiated_destination', 'is_confirmed_source',
                   'is_confirmed_destination']
    search_fields = ['source__name', 'destination__name', 'transaction_items__category__name']
    inlines = [
        TransactionItemInline
    ]


class PlaceItemAdmin(ItemAdmin):
    place_id = None

    def get_queryset(self, request):
        qs = super(PlaceItemAdmin, self).get_queryset(request)
        return qs.filter(place_id=self.place_id)

    def changelist_view(self, request, place_id=None, extra_context=None):
        self.place_id = place_id
        try:
            place = Place.objects.get(pk=place_id)
        except Place.DoesNotExist:
            self.opts.verbose_name_plural = _('Place does not exist')
        else:
            self.opts.verbose_name_plural = _("Items for {name}".format(name=place.name))
        view = super(PlaceItemAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

    def get_urls(self):
        from django.conf.urls import url
        from functools import update_wrapper

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        # info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            url(r'^(?P<place_id>\d+)/$', wrap(self.changelist_view), name='base_place_items_changelist'),
        ]
        return urlpatterns

create_model_admin(PlaceItemAdmin, name='place-item', model=Item)

