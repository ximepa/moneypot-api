# -*- encoding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext
from base.models import InvalidParameters
import re

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


def parse_serials_data(serials):

    serials_data = re.findall(r"[\w-]+", serials)
    for index, raw_serial in enumerate(serials_data):
        if '--' in raw_serial:
            l, r = raw_serial.split('--')
            if not len(r) == len(l):
                raise InvalidParameters(ugettext(
                    u'serials range left and rigth parts length mismatch: {raw_serial}'.format(
                        raw_serial=raw_serial
                    )
                ))
            rxp = re.compile(r"^([a-z0-9]*?)([0-9]+)$", re.I)
            lm = rxp.match(l)
            rm = rxp.match(r)
            if not lm or not rm:
                raise InvalidParameters(ugettext(
                    u'serials range format error: {raw_serial}'.format(
                        raw_serial=raw_serial
                    )
                ))
            lb, li = lm.groups()
            rb, ri = rm.groups()
            ln = len(li)
            if not lb == rb:
                raise InvalidParameters(ugettext(
                    u'serials range left and rigth parts base mismatch: {raw_serial}, {lb}≠{rb}'.format(
                        raw_serial=raw_serial,
                        rb=rb,
                        lb=lb,
                    )
                ))
            li = int(li)
            ri = int(ri)
            if not ri > li:
                raise InvalidParameters(ugettext(
                    u'serials range left part must be lesser than rigth: {raw_serial}, {li}>={ri}'.format(
                        raw_serial=raw_serial,
                        ri=ri,
                        li=li,
                    )
                ))
            if (ri - li) >= 500:
                raise InvalidParameters(ugettext(
                    u'serials range too large: {raw_serial} {size}>500'.format(
                        raw_serial=raw_serial,
                        size=ri-li+1
                    )
                ))
            del(serials_data[index])
            for i in range(li, ri+1):
                serial = "%s%s" % (lb, str(i).zfill(ln))
                serials_data.insert(index, serial)
                index += 1

    if not len(serials_data) == len(set(serials_data)):
        raise InvalidParameters(ugettext(
            "serials data non unique"
        ))

    return sorted(serials_data)
