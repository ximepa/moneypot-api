# -*- encoding: utf-8 -*-
__author__ = 'maxim'

from django.views.debug import ExceptionReporter
from django.http import HttpResponse
from unidecode import unidecode
import sys
import code

class ExceptionMiddleware(object):

    def process_exception(self, request, exception):
        exc_type, exc_value, tb = sys.exc_info()
        reporter = ExceptionReporter(request, exc_type, exc_value, tb)
        html = reporter.get_traceback_html()
        return HttpResponse(html, status=500, content_type='text/html')
