# -*- encoding: utf-8 -*-
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _


def process_to_void(modeladmin, request, queryset):
    for item in queryset:
        if item.comment:
            item.process()
            messages.add_message(request, messages.SUCCESS, _("processed %s" % item))
        else:
            messages.add_message(request, messages.ERROR, _("Error: no comment for %s" % item))


process_to_void.short_description = _("Process to void")