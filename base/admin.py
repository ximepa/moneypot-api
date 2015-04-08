from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from base.models import Unit, ItemCategory, Place, PurchaseItem, Payer, Purchase, Item, ItemSerial, ItemChunk, \
    TransactionItem, Transaction


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


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
