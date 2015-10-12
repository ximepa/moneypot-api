# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

import sys

from django.views.debug import ExceptionReporter
from django.http import HttpResponse


class ExceptionMiddleware(object):
    def process_exception(self, request, exception):
        print(exception)
        exc_type, exc_value, tb = sys.exc_info()
        reporter = ExceptionReporter(request, exc_type, exc_value, tb)
        html = reporter.get_traceback_html()
        return HttpResponse(html, status=500, content_type='text/html')
