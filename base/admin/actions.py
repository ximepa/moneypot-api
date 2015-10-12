# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from base.models import Cell, ItemSerial


def process_to_void(modeladmin, request, queryset):
    for item in queryset:
        if item.comment:
            item.process()
            messages.add_message(request, messages.SUCCESS, _("processed %s" % item))
        else:
            messages.add_message(request, messages.ERROR, _("Error: no comment for %s" % item))


process_to_void.short_description = _("Process to void")


def update_cell(modelsadmin, request, queryset):
    cell_id = request.POST['cell']
    try:
        cell = Cell.objects.get(pk=cell_id)
    except Cell.DoesNotExist:
        modelsadmin.message_user(request, _("Selected cell does not exist"), level=messages.ERROR)
    else:
        cnt = queryset.count()
        queryset.update(cell=cell)
        if queryset.model.__name__ in ["place_item", "Item"]:
            ItemSerial.objects.filter(item__pk__in=queryset.values_list("pk", flat=True)).update(cell=cell)
        modelsadmin.message_user(request, _("Updated items count: {cnt}, Cell: {cell}".format(
            cnt=cnt,
            cell=cell.name
        )), level=messages.SUCCESS)

update_cell.short_description = _('Update cell of selected rows')