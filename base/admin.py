from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from base.models import Unit, ItemCategory, Place, PurchaseItem, Payer, Purchase, Item, ItemSerial, ItemChunk, \
    TransactionItem, Transaction

import autocomplete_light

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemCategory)
class ItemCategoryAdmin(MPTTModelAdmin):
    pass


@admin.register(Place)
class PlaceAdmin(MPTTModelAdmin):
    pass


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Payer)
class PayerAdmin(admin.ModelAdmin):
    pass


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    inlines = [PurchaseItemInline,]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemSerial)
class ItemSerialAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemChunk)
class ItemChunkAdmin(admin.ModelAdmin):
    pass


class TransactionItemForm(autocomplete_light.ModelForm):
    class Meta:
        model = TransactionItem
        exclude = ['_chunks', 'purchase']
        autocomplete_fields = ('category',)


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    pass


class TransactionForm(autocomplete_light.ModelForm):
    class Meta:
        model = Transaction
        exclude = []
        autocomplete_fields = ('source', 'destination', 'items')


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    form = TransactionItemForm


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    class Media:
        js = ('base/js/transaction_source_item_autocomplete.js',)
    form = TransactionForm
    inlines = [
        TransactionItemInline
    ]