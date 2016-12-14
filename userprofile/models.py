# -*- encoding: utf-8 -*-

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    place = models.ForeignKey("base.Place", blank=True, null=True)

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self):
        return str(self.user)


