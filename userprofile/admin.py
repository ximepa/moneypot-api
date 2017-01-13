# -*- encoding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from userprofile.models import Profile
import autocomplete_light


class ProfileInlineForm(autocomplete_light.ModelForm):
    class Meta:
        model = Profile
        exclude = []


class ProfileInline(admin.StackedInline):
    form = ProfileInlineForm
    model = Profile
    can_delete = False
    verbose_name_plural = 'profiles'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'place')

    def place(self, obj):
        return obj.profile.place


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
