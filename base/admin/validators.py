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
    с. Родниківка, 2-й пров. Київський, (лінія)
    """

    def geoname_lookup(q, fix=False):
        try:
            geoname = GeoName.objects.get(name__iexact=q)
        except GeoName.DoesNotExist:
            geonames = GeoName.objects.filter(name__similar=q).extra(
                select={'distance': "similarity(base_geoname.name, '%s')" % q.replace("'", "")}
            ).order_by('-distance')
            if geonames.count():
                if geonames[0].name.replace(" ", "") == q.replace(" ", ""):
                    fix=True
                if not fix:
                    raise ValidationError("%s: Можливо ви мали на увазі `%s`?" % (value, geonames[0].name))
                else:
                    geoname = geonames[0]
            else:
                raise ValidationError("%s: географічний об'єкт не знайдено `%s`" % (value, q))
        return geoname

    def street_parse(street_match):
        numerator = street_match.group(1)
        if 'п' in street_match.group(2):
            prefix = "пров."
        elif 'в' in street_match.group(2):
            prefix = "вул."
        else:
            raise ValidationError("%s: вулиця чи провулок?" % value)
        print(street_match.groups())
        ext = street_match.group(4)
        q = street_match.group(3)
        geoname = geoname_lookup(q, fix)
        part = "%s %s" % (prefix, geoname)
        if ext:
            part = "%s %s" % (part, ext)
        if numerator:
            part = "%s %s" % (numerator, part)
        return part

    addrs_re = re.compile(r"(\bм\b\.?|\bс\b\.?|\bв\b\.?|\bвул\b\.?|\bпров\b\.?|\bпер\b\.?|\bпр\b\.?)", re.IGNORECASE)
    city_re = re.compile(r"(\bм\b\.?|\bс\b\.?) *(.+)", re.IGNORECASE, )
    street_re = re.compile(r"(\d+-[А-Я]+)? *"
                           r"(\bв\b\.?|\bвул\b\.?|\bпров\b\.?|\bпер\b\.?|\bпр\b\.?)"
                           r" *([^\(\)\"]+)"
                           r" *(\(.*\)|\".*\")?", re.IGNORECASE, )
    house_re = re.compile(r"^(\d+) *([А-Я]?)(\/\d+ *[А-Я]?)? *(\(.*\)|\".*\")?$", re.IGNORECASE, )
    flat_re = re.compile(r"^(кв|кімн?|оф|каб)\.? *(\d+[А-Я]?(\/\d+[А-Я]?)?) *(\(.*\)|\".*\")?$", re.IGNORECASE, )
    voca_re = re.compile(r"^(будка|ящик|криша|маг) *(.+)?$", re.IGNORECASE, )
    ext_re = re.compile(r"^(\(.*\)|\".*\")?$", re.IGNORECASE, )

    value = value.strip()

    if addrs_re.match(value):
        parts = map(lambda x: x.strip(), value.split(","))
        res = []
        for part in parts:

            city_match = city_re.match(part)
            if city_match:
                prefix = city_match.group(1)
                q = city_match.group(2)
                geoname = geoname_lookup(q, fix)
                part = "%s %s" % (prefix, geoname)
                res.append(part)
                continue

            street_match = street_re.match(part)
            if street_match:
                if '--' in part:
                    street_parts = part.split('--')
                    parts = []
                    for sp in street_parts:
                        sp = sp.strip()
                        sm = street_re.match(sp)
                        if sm:
                            parts.append(street_parse(sm))
                    part = " -- ".join(parts)
                else:
                    part = street_parse(street_match)
                res.append(part)
                continue

            house_match = house_re.match(part)
            if house_match:
                house = "%s%s%s" % (house_match.group(1), house_match.group(2) or '', house_match.group(3) or '')
                ext = house_match.group(4)
                if ext:
                    part = "%s %s" % (house.upper(), ext)
                else:
                    part = house
                res.append(part)
                continue

            flat_match = flat_re.match(part)
            if flat_match:
                if "кв" in flat_match.group(1):
                    prefix = "кв"
                elif "кім" in flat_match.group(1):
                    prefix = "кімн"
                elif "оф" in flat_match.group(1):
                    prefix = "оф"
                elif "каб" in flat_match.group(1):
                    prefix = "каб"
                else:
                    raise ValidationError("%s: квартира, кімната чи офіс?" % value)
                part = "%s. %s" % (prefix, flat_match.group(2))
                ext = flat_match.group(4)
                if ext:
                    part = "%s %s" % (part, ext)
                res.append(part)
                continue

            ext_match = ext_re.match(part)
            if ext_match:
                res.append(ext_match.group(1))
                continue

            voca_match = voca_re.match(part)
            if voca_match:
                part = "%s %s" % (voca_match.group(1), voca_match.group(2))
                res.append(part)
                continue

            raise ValidationError("частина адреси не розпізнається `%s` з `%s`" % (part, value))

        print(", ".join(res))
        return ", ".join(res)
    else:
        print("#!@")
        print(value)
        return value


if __name__ == "__main__":
    validate_place_name("вул. С.Перовської, 19, кв. 24")
    validate_place_name("с. Родниківка, 2-й пров. Київський, (лінія)")
