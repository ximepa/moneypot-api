# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

import re
import sys

from django.conf import settings
from django.http import HttpResponse
from django.views.debug import ExceptionReporter


class ExceptionMiddleware(object):
    def process_exception(self, request, exception):
        exc_type, exc_value, tb = sys.exc_info()
        reporter = ExceptionReporter(request, exc_type, exc_value, tb)
        html = reporter.get_traceback_html()
        return HttpResponse(html, status=500, content_type='text/html')


class StaticRevision(object):
    def process_request(self, request):
        request.release_notes_url = settings.RELEASE_NOTES_URL

    def process_response(self, request, response):
        if response.has_header('Content-Type'):
            if "text/html" in response['Content-Type']:
                revision = getattr(request, "git_revision", "UNKNOWN_REVISION")
                html = response.content
                html = re.sub(b"\.(js|css)(\")", b".\\1?rev=%s\\2" % revision.encode('utf-8'), html, re.UNICODE)
                response.content = html
        return response
