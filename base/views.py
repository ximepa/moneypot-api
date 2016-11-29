# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

import json
import xlsxwriter
from io import BytesIO
from unidecode import unidecode

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from datetime import datetime

from base.admin.forms import WarrantyForm
from base.models import Item, PurchaseItem, ItemSerial, Cell, ItemChunk, Warranty, Place


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def index(request):
    ip = get_client_ip(request)
    return render_to_response('base/index.html')


def ajax_qty(request, place_id, category_id):
    selector = request.GET.get('selector', '')
    data = {
        'selector': selector
    }
    try:
        item = Item.objects.get(place_id=place_id, category_id=category_id)
    except Item.DoesNotExist:
        data.update({
            'qty': 'n/a'
        })
    else:
        data.update({
            'qty': "%0.3f" % item.quantity
        })
    return HttpResponse(json.dumps(data), content_type="application/json")


def ajax_price(request, source_id, category_id):
    selector_usd = request.GET.get('selector_usd', '')
    selector_uah = request.GET.get('selector_uah', '')
    data = {
        'selector_usd': selector_usd,
        'selector_uah': selector_uah
    }

    p_items = PurchaseItem.objects.filter(purchase__source_id=source_id, category_id=category_id)
    if not p_items.count():
        data.update({
            'price_uah': 'n/a',
            'price_usd': 'n/a'
        })
    else:
        p_items.order_by("-purchase__created_at")
        item = p_items[0]
        data.update({
            'price_uah': "%0.2f" % (item.price or 0),
            'price_usd': "%0.2f" % (item.price_usd or 0)
        })
    return HttpResponse(json.dumps(data), content_type="application/json")


def ajax_serial_category(request, serial_id):
    selector = request.GET.get('selector', '')
    data = {
        'selector': selector
    }
    try:
        serial = ItemSerial.objects.get(pk=serial_id)
    except ItemSerial.DoesNotExist:
        pass
    else:
        data.update({
            'category_name': serial.item.category.name,
            'category_id': serial.item.category_id,
        })
    return HttpResponse(json.dumps(data), content_type="application/json")


def ajax_cell(request, place_id, category_id, serial_id=None):
    selector = request.GET.get('selector', '')
    data = {
        'selector': selector
    }
    cell_name = ''

    if not serial_id:
        item = Item.objects.filter(place_id=place_id, category_id=category_id)
        if item.count():
            cell = item[0].cell
            if cell:
                cell_name = item[0].cell.name
    else:
        try:
            serial = ItemSerial.objects.get(id=serial_id)
        except ItemSerial.DoesNotExist:
            pass
        else:
            cell = serial.cell
            if cell:
                cell_name = serial.cell.name

    data.update({
        'cell': cell_name
    })
    return HttpResponse(json.dumps(data), content_type="application/json")


def ajax_item_cell(request, item_id, cell_id):
    selector = request.GET.get('selector', '')
    cell_id = int(cell_id) or None
    data = {
        'selector': selector,
        'success': True,
    }

    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        data.update({
            'success': False,
            'msg': "item does not exist"
        })
    else:
        if cell_id:
            try:
                cell = Cell.objects.get(pk=cell_id)
            except Cell.DoesNotExist:
                data.update({
                    'success': False,
                    'msg': "cell does not exist"
                })
        if data['success']:
            item.cell_id = cell_id
            item.save()
            item.serials.update(cell_id=cell_id)
    return HttpResponse(json.dumps(data), content_type="application/json")


def ajax_serial_cell(request, serial_id, cell_id):
    selector = request.GET.get('selector', '')
    cell_id = int(cell_id) or None
    data = {
        'selector': selector,
        'success': True,
    }

    try:
        itemserial = ItemSerial.objects.get(pk=serial_id)
    except Item.DoesNotExist:
        data.update({
            'success': False,
            'msg': "item serial does not exist"
        })
    else:
        if cell_id:
            try:
                cell = Cell.objects.get(pk=cell_id)
            except Cell.DoesNotExist:
                data.update({
                    'success': False,
                    'msg': "cell does not exist"
                })
        if data['success']:
            itemserial.cell_id = cell_id
            itemserial.save()
    return HttpResponse(json.dumps(data), content_type="application/json")


def ajax_chunk_cell(request, chunk_id, cell_id):
    selector = request.GET.get('selector', '')
    cell_id = int(cell_id) or None
    data = {
        'selector': selector,
        'success': True,
    }

    try:
        itemchunk = ItemChunk.objects.get(pk=chunk_id)
    except Item.DoesNotExist:
        data.update({
            'success': False,
            'msg': "item chunk does not exist"
        })
    else:
        if cell_id:
            try:
                cell = Cell.objects.get(pk=cell_id)
            except Cell.DoesNotExist:
                data.update({
                    'success': False,
                    'msg': "cell does not exist"
                })
        if data['success']:
            itemchunk.cell_id = cell_id
            itemchunk.save()
    return HttpResponse(json.dumps(data), content_type="application/json")


def ajax_serial_warranty(request, serial_id, datestr=None):
    selector = request.GET.get('selector', '')

    data = {
        'selector': selector,
        'success': True,
    }

    try:
        itemserial = ItemSerial.objects.get(pk=serial_id)
    except Item.DoesNotExist:
        data.update({
            'success': False,
            'msg': "Serial does not exist"
        })
    else:
        try:
            warranty = itemserial.warranty
        except Warranty.DoesNotExist:
            warranty = None
        if datestr:
            f = WarrantyForm({
                "serial": itemserial.id,
                "date": datestr
            }, instance=warranty)

            if not f.is_valid():
                data.update({
                    'success': False,
                    'msg': f.errors
                })
            else:
                f.save()
        else:
            if warranty:
                warranty.delete()

    return HttpResponse(json.dumps(data), content_type="application/json")


def export_items(request, place_id=None):
    try:
        pl = Place.objects.get(pk=place_id)
    except Place.DoesNotExist:
        raise Http404("No place with id: %s" % place_id)

    output = BytesIO()

    base_level = pl.level
    safe_name = unidecode(pl.name)[:30]
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename = slugify("%s-%s" % (safe_name, time_str))

    book = xlsxwriter.Workbook(output)
    blue_fmt = book.add_format({'bold': True, 'font_color': 'blue', 'align': 'center'})
    bold_fmt = book.add_format({'bold': True, 'font_color': 'black', 'align': 'left'})
    norm_fmt = book.add_format({'bold': False, 'font_color': 'black', 'align': 'left'})
    norm_fmt.set_text_wrap()

    sheet = book.add_worksheet(safe_name)
    sheet.merge_range('A1:E1', "%s -- %s" % (pl.name, time_str), blue_fmt)
    sheet.set_column(0, 0, 25)
    sheet.set_column(1, 1, 50)
    sheet.set_column(2, 2, 8)
    sheet.set_column(3, 3, 8)
    sheet.set_column(4, 4, 60)
    sheet.write(1, 0, 'Місце', bold_fmt)
    sheet.write(1, 1, 'Категорія предмету', bold_fmt)
    sheet.write(1, 2, 'Кількість', bold_fmt)
    sheet.write(1, 3, 'Одиниця', bold_fmt)
    sheet.write(1, 4, 'Серійні номери', bold_fmt)

    row = 1

    places = pl.get_descendants(include_self=True)
    for p in places:
        items = p.items.filter(quantity__gt=0).select_related(
            'place', 'category', 'category__unit').order_by('category__name')
        row += 1
        sheet.merge_range(row, 0, row, 4, p.name, bold_fmt)
        sheet.set_row(row, None, None, {'level': p.level - base_level})
        for i in items:
            row += 1
            sheet.write(row, 0, i.place.name, norm_fmt)
            sheet.write(row, 1, i.category.name, norm_fmt)
            sheet.write(row, 2, i.quantity, norm_fmt)
            sheet.write(row, 3, i.category.unit.name, norm_fmt)
            sheet.write(row, 4,
                        ', '.join(map(lambda x: x.serial, i.serials.all()))
                        , norm_fmt)
            sheet.set_row(row, None, None, {'level': p.level - base_level + 1})

    book.close()

    output.seek(0)
    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=%s.xlsx" % filename

    return response
