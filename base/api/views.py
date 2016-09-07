# -*- encoding: utf-8 -*-
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response

from base.models import Place
from .serializers import PlaceSerializer


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
        return Response(PlaceSerializer(place, context={'request': request}).data)
