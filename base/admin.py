from functools import update_wrapper

from django.contrib import admin
from django import forms
from django.db import models
from django_mptt_admin.admin import DjangoMpttAdmin
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.contrib import messages
import autocomplete_light

from base.models import Unit, ItemCategory, Place, PurchaseItem, Payer, Purchase, Item, ItemSerial, ItemChunk, \
    TransactionItem, Transaction, ItemCategoryComment, OrderItemSerial, ContractItemSerial


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


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


class ItemCategoryCommentForm(autocomplete_light.ModelForm):
    class Meta:
        model = ItemCategoryComment
        exclude = []


class ItemCategoryCommentInline(admin.TabularInline):
    model = ItemCategoryComment
    form = ItemCategoryCommentForm
    extra = 10


class ItemCategoryForm(autocomplete_light.ModelForm):
    class Meta:
        model = ItemCategory
        exclude = []


@admin.register(ItemCategory)
class ItemCategoryAdmin(DjangoMpttAdmin):
    form = ItemCategoryForm
    search_fields = ['name', ]
    tree_auto_open = False
    inlines = [ItemCategoryCommentInline]


class PlaceForm(autocomplete_light.ModelForm):
    class Meta:
        model = Place
        exclude = []


@admin.register(Place)
class PlaceAdmin(DjangoMpttAdmin):
    search_fields = ['name', ]
    tree_auto_open = False
    form = PlaceForm
    list_display = ['__unicode__', 'is_shop', 'items_changelist_link']

    def items_changelist_link(self, obj):
        # link = reverse("admin:base_item_change", args=[obj.id])
        link = reverse("admin:base_place_item_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("items list")))


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Payer)
class PayerAdmin(admin.ModelAdmin):
    search_fields = ['name', ]


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
            if p.is_completed:
                raise RuntimeError(_("already completed"))
            # try:
            p.complete()
            # except Exception, e:
            # raise forms.ValidationError(e)
        return p


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
    inlines = [PurchaseItemInline, ]
    list_display = ['__unicode__', 'created_at', 'completed_at', 'source', 'destination', 'is_completed',
                    'is_prepared', ]
    list_filter = ['source', 'destination', 'is_completed', 'is_prepared', ]
    search_fields = ['source__name', 'destination__name', 'purchase_items__category__name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ['category__name', 'place__name']
    list_filter = ['category', ]
    list_display = ['__unicode__', 'quantity', 'place']


@admin.register(ItemSerial)
class ItemSerialAdmin(admin.ModelAdmin):
    search_fields = ['item__category__name', 'serial']
    list_filter = ['item__category', ]
    list_display = ['__unicode__', 'category_name']


@admin.register(ItemChunk)
class ItemChunkAdmin(admin.ModelAdmin):
    search_fields = ['item__category__name']
    list_filter = ['item__category', ]
    list_display = ['__unicode__', 'category_name']


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


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    form = TransactionItemForm
    extra = 10
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
    }


class TransactionCommentPlaceInline(admin.TabularInline):
    model = Transaction.comment_places.through
    form = autocomplete_light.modelform_factory(Place, exclude=[])
    extra = 10


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
        TransactionItemInline, TransactionCommentPlaceInline
    ]


class PlaceItemAdmin(ItemAdmin):
    place_id = None
    list_display = ['obj_link', 'quantity', 'place', 'items_serials_changelist_link', 'items_chunks_changelist_link']

    def obj_link(self, obj):
        # link = reverse("admin:base_item_change", args=[obj.id])
        link = reverse("admin:base_place_item_change", args=[self.place_id, obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, obj.__unicode__()))

    def items_serials_changelist_link(self, obj):
        link = reverse("admin:base_item_serials_filtered_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("serials list")))

    def items_chunks_changelist_link(self, obj):
        # link = reverse("admin:base_item_serials_filtered_changelist", args=[obj.id])
        link = "#%s" % obj.id
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("chunks list")))

    def get_queryset(self, request):
        qs = super(PlaceItemAdmin, self).get_queryset(request)
        return qs.filter(place_id=self.place_id)

    def changelist_view(self, request, place_id, extra_context=None):  # pylint:disable=arguments-differ
        self.place_id = place_id
        extra_context = extra_context or {}
        try:
            place = Place.objects.get(pk=place_id)
        except Place.DoesNotExist:
            extra_context.update({'cl_header': _('Place does not exist')})
        else:
            extra_context.update({'cl_header': _(u"Items for {name}".format(name=unicode(place.name)))})
        view = super(PlaceItemAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

    def change_view(self, request, place_id, object_id, form_url='', extra_context=None):  # pylint:disable=arguments-differ
        self.place_id = place_id
        extra_context = extra_context or {}
        extra_context.update({
            'place_id': place_id,
            'proxy_url': "admin:base_place_item_changelist",
            'proxy_url_arg': self.place_id,
        })
        try:
            item = Item.objects.get(pk=object_id)
        except Item.DoesNotExist:
            extra_context.update({'obj_header': _('Serial does not exist')})
        else:
            extra_context.update({'obj_header': unicode(item.category.name)})
        try:
            place = Place.objects.get(pk=place_id)
        except Place.DoesNotExist:
            extra_context.update({'cl_header': _('Place does not exist')})
        else:
            extra_context.update({'cl_header': _(u"Items for {name}".format(name=unicode(place.name)))})
        return super(PlaceItemAdmin, self).change_view(request, object_id, form_url='', extra_context=extra_context)

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^(\d+)/$', wrap(self.changelist_view), name='base_place_item_changelist'),
            url(r'^(\d+)/(\d+)$', wrap(self.change_view), name='base_place_item_change'),
        ]
        return urlpatterns

    change_list_template = 'admin/proxy_change_list.html'
    change_form_template = 'admin/proxy_change_form.html'


create_model_admin(PlaceItemAdmin, name='place_item', model=Item)


class ItemSerialsFilteredAdmin(ItemSerialAdmin):
    item_id = None
    list_display = ['obj_link', 'category_name']

    def obj_link(self, obj):
        link = reverse("admin:base_item_serials_filtered_change", args=[self.item_id, obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, obj.__unicode__()))

    def get_queryset(self, request):
        qs = super(ItemSerialsFilteredAdmin, self).get_queryset(request)
        return qs.filter(item_id=self.item_id)

    def changelist_view(self, request, item_id, extra_context=None):  # pylint:disable=arguments-differ
        self.item_id = item_id
        extra_context = extra_context or {}
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            extra_context.update({'cl_header': _('Item does not exist')})
        else:
            extra_context.update({'cl_header': _(u"Serials for {name} in {place}".format(
                name=unicode(item.category.name),
                place=unicode(item.place.name)
            ))})
        view = super(ItemSerialsFilteredAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

    def change_view(self, request, item_id, object_id, form_url='', extra_context=None):  # pylint:disable=arguments-differ
        self.item_id = item_id
        extra_context = extra_context or {}
        extra_context.update({
            'item_id': item_id,
            'proxy_url': "admin:base_item_serials_filtered_changelist",
            'proxy_url_arg': self.item_id,
        })
        try:
            serial = ItemSerial.objects.get(pk=object_id)
        except ItemSerial.DoesNotExist:
            extra_context.update({'obj_header': _('Serial does not exist')})
        else:
            extra_context.update({'obj_header': unicode(serial.serial)})
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            extra_context.update({'cl_header': _('Item does not exist')})
        else:
            extra_context.update({'cl_header': _(u"Serials for {name} in {place}".format(
                name=unicode(item.category.name),
                place=unicode(item.place.name)
            ))})
        return super(ItemSerialsFilteredAdmin, self).change_view(request, object_id, form_url='',
                                                                 extra_context=extra_context)

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^(\d+)/$', wrap(self.changelist_view), name='base_item_serials_filtered_changelist'),
            url(r'^(\d+)/(\d+)$', wrap(self.change_view), name='base_item_serials_filtered_change'),
        ]
        return urlpatterns

    change_list_template = 'admin/proxy_change_list.html'
    change_form_template = 'admin/proxy_change_form.html'


create_model_admin(ItemSerialsFilteredAdmin, name='item_serials_filtered', model=ItemSerial)


def process_to_void(modeladmin, request, queryset):
    for item in queryset:
        if item.comment:
            item.process()
            messages.add_message(request, messages.SUCCESS, _("processed %s" % item))
        else:
            messages.add_message(request, messages.ERROR, _("Error: no comment for %s" % item))
process_to_void.short_description = _("Process to void")


@admin.register(OrderItemSerial)
class OrderItemSerialAdmin(admin.ModelAdmin):
    search_fields = ['serial']
    list_filter = ['item__place', ]
    list_display = ['__unicode__', 'category_name', 'owner', 'comment']
    ordering = ['comment',]
    readonly_fields = ['item', 'purchase', 'serial', 'owner']
    fields = ['comment', 'serial', 'owner']
    actions = [process_to_void]


@admin.register(ContractItemSerial)
class ContractItemSerialAdmin(admin.ModelAdmin):
    search_fields = ['serial']
    list_filter = ['item__place', ]
    list_display = ['__unicode__', 'category_name', 'owner', 'comment']
    ordering = ['comment',]
    readonly_fields = ['item', 'purchase', 'serial', 'owner']
    fields = ['comment', 'serial', 'owner']
    actions = [process_to_void]
