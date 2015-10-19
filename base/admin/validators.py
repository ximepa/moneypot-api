# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

import re
from django.core.exceptions import ValidationError
from base.models import GeoName


def validate_place_name(value, fix=False):
    """
    вул. С.Перовської, 19, кв. 24
    пров. Смідовича, 5, кв. 4
    с. Кочержинці, вул. Черняховського, 13 (груша)
    """

    addrs_re = re.compile(r"(\bв\b\.?|\bвул\b\.?|\bпров\b\.?|\bпер\b\.?|\bпр\b\.?)", re.IGNORECASE)
    street_re = re.compile(r"(\bв\b\.?|\bвул\b\.?|\bпров\b\.?|\bпер\b\.?|\bпр\b\.?) (.+)", re.IGNORECASE, )
    if addrs_re.match(value):
        parts = map(lambda x: x.strip(), value.split(","))
        for part in parts:
            street_match = street_re.match(part)
            if street_match:
                if 'в' in street_match.group(1):
                    prefix = "вул."
                elif 'п' in street_match.group(1):
                    prefix = "пров."
                else:
                    raise ValidationError("вулиця чи провулок?")
                q = street_match.group(2)
                try:
                    geoname = GeoName.objects.get(name__iexact=q)
                except GeoName.DoesNotExist:
                    geonames = GeoName.objects.filter(name__similar=q).extra(
                        select={'distance': "similarity(name, '%s')" % q}
                    ).order_by('-distance')
                    if geonames.count():
                        if not fix:
                            raise ValidationError("Можливо ви мали на увазі %s?" % geonames[0].name)
                        else:
                            geoname = geonames[0]
                    else:
                        raise ValidationError("географічний об'єкт не знайдено")


if __name__ == "__main__":
    validate_place_name("вул. С.Перовської, 19, кв. 24")