from django.shortcuts import render_to_response
from base.models import Item, PurchaseItem
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