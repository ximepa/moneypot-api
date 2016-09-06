# -*- encoding: utf-8 -*-

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
        p = Place.objects.get(pk=896)
        return Response(PlaceSerializer(p, context={'request': request}).data)
