# -*- encoding: utf-8 -*-
from django.contrib import admin


class ReadOnlyMixin(object):
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        result = list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))
        result.remove('id')
        return result


class InlineReadOnly(ReadOnlyMixin, admin.TabularInline):
    pass


class AdminReadOnly(ReadOnlyMixin, admin.ModelAdmin):
    pass
