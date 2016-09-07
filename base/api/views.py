# -*- encoding: utf-8 -*-
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import PlaceSerializer, ItemSerializer


class HomeView(APIView):
    """
    View to list item that current user own.

    * Requires token authentication.
    """
    def get(self, request):
        place = None
        try:
            place = request.user.profile.place
        except Exception as e:
            print(e)
        if not place:
            raise NotFound()

        q = request.GET.get('q', None)
        items = place.items.all()
        if len(q) > 3:
            items = items.filter(category__name__similar=q)
        elif q:
            items = items.filter(category__name__icontains=q)
        data = PlaceSerializer(place, context={'request': request}).data
        data['items'] = ItemSerializer(items, many=True, context={'request': request}).data

        return Response(data)
