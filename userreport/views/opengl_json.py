from userreport.models import GraphicsDevice

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def ReportOpenglJson(request):
    devices = {}

    reports = GraphicsDevice.objects.all()
    for report in reports:
        exts = frozenset(e.name for e in report.graphicsextension_set.all())
        limits = dict((l.name, l.value) for l in report.graphicslimit_set.all())

        device = (report.vendor, report.renderer, report.os, report.driver)
        devices.setdefault((hashabledict(limits), exts), set()).add(device)

    sorted_devices = devices.items()#sorted(devices.items(), key=devices.items().get)

    data = []
    for (limits,exts),deviceset in sorted_devices:
        devices = [
            {'vendor': v, 'renderer': r, 'os': o, 'driver': d}
            for (v,r,o,d) in sorted(deviceset)
        ]
        data.append({'devices': devices, 'limits': limits, 'extensions': sorted(exts)})
    json = simplejson.dumps(data, indent=1, sort_keys=True)
    return HttpResponse(json, content_type = 'text/plain')


def ReportOpenglJsonFormat(request):
    return render_to_response('jsonformat.html')
