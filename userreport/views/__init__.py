from userreport.views.upload import Upload
from userreport.views.cpu import ReportCpu
# from userreport.views.usercount import ReportUsercount
from userreport.views.opengl import ReportOpenglIndex, ReportOpenglFeature

from userreport.models import UserReport #, UserReport_hwdetect, GraphicsDevice, GraphicsExtension, GraphicsLimit
#import userreport.x86 as x86
#import userreport.gl

import hashlib
import datetime
import zlib
import re

from django.http import HttpResponseBadRequest, HttpResponse, Http404, QueryDict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.db import connection, transaction

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

def index(request):
    return render_to_response('index.html')


"""
def report_opengl_json(request):
    devices = {}

    reports = GraphicsDevice.objects.all()
    for report in reports:
        exts = frozenset(e.name for e in report.graphicsextension_set.all())
        limits = dict((l.name, l.value) for l in report.graphicslimit_set.all())

        device = (report.vendor, report.renderer, report.os, report.driver)
        devices.setdefault((hashabledict(limits), exts), set()).add(device)

    sorted_devices = sorted(devices.items(), key=devices.items().get)

    data = []
    for (limits,exts),deviceset in sorted_devices:
        devices = [
            {'vendor': v, 'renderer': r, 'os': o, 'driver': d}
            for (v,r,o,d) in sorted(deviceset)
        ]
        data.append({'devices': devices, 'limits': limits, 'extensions': sorted(exts)})
    json = simplejson.dumps(data, indent=1, sort_keys=True)
    return HttpResponse(json, content_type = 'text/plain')

def report_opengl_json_format(request):
    return render_to_response('jsonformat.html')


def report_opengl_devices(request, selected):
    cursor = connection.cursor()
    cursor.execute('''
        SELECT DISTINCT device_name
        FROM userreport_graphicsdevice
    ''')
    all_devices = set(n for (n,) in cursor.fetchall())

    all_limits = set()
    all_exts = set()
    devices = {}
    gl_renderers = set()

    reports = GraphicsDevice.objects.filter(device_name__in = selected)
    for report in reports:
        exts = frozenset(e.name for e in report.graphicsextension_set.all())
        all_exts |= exts

        limits = dict((l.name, l.value) for l in report.graphicslimit_set.all())
        all_limits |= set(limits.keys())

        devices.setdefault(hashabledict({'device': report.device_name, 'os': report.os}), {}).setdefault((hashabledict(limits), exts), set()).add(report.driver)

        gl_renderers.add(report.renderer)

    if len(selected) == 1 and len(devices) == 0:
        raise Http404

    all_limits = sorted(all_limits)
    all_exts = sorted(all_exts)

    distinct_devices = []
    for (renderer, v) in devices.items():
        for (caps, versions) in v.items():
            distinct_devices.append((renderer, sorted(versions), caps))
    distinct_devices.sort(key = lambda x: (x[0]['device'], x))

    return render_to_response('reports/opengl_device.html', {
        'selected': selected,
        'all_limits': all_limits,
        'all_exts': all_exts,
        'all_devices': all_devices,
        'devices': distinct_devices,
        'gl_renderers': gl_renderers,
    })

def report_opengl_device(request, device):
    return report_opengl_devices(request, [device])

def report_opengl_device_compare(request):
    return report_opengl_devices(request, request.GET.getlist('d'))


"""
