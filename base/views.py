from django.shortcuts import render_to_response
from base.models import Item, PurchaseItem, ItemSerial, Cell
import json
from django.http import HttpResponse

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
            'category_name':serial.item.category.name,
            'category_id':serial.item.category_id,
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