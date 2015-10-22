# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from django.core.management.base import BaseCommand, CommandError
from base.models import Place, FixPlaceMerge
from base.admin.validators import validate_place_name
from django.conf import settings
from django.core.exceptions import ValidationError

PLACE_ADDRESS_ID = settings.APP_FILTERS['PLACE_ADDRESS_ID']


class Command(BaseCommand):
    help = 'Check place name and mark them for fix'

    def handle(self, *args, **options):
        p = Place.objects.get(pk=PLACE_ADDRESS_ID)
        addrs = p.get_descendants()
        for a in addrs:
            if 'FIX' not in a.name:
                try:
                    name = validate_place_name(a.name)
                except Exception as e:
                    a.name = "%s FIX" % a.name
                    a.save()
                else:
                    if not a.name == name:
                        old_name = a.name
                        a.name = name
                        try:
                            a.save()
                        except ValidationError as e:
                            print("dup! %s" % old_name)
                            a.name = "%s DUP!" % name
                            a.save()
                            # new_place = Place.objects.get(name=name)
                            # pm = FixPlaceMerge(
                            #     old_place=a,
                            #     new_place=new_place
                            # )
                            # pm.save()


