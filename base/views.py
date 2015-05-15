from django.shortcuts import render_to_response
from base.models import Item
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
    print "IP: %s" % ip
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