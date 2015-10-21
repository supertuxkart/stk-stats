import json

from userreport.settings import ENABLE_JSON
from userreport.models import GraphicsDevice
from userreport.util import HashableDict
from django.http import HttpResponse
from django.shortcuts import render_to_response


def report_opengl_json(request):
    content_type = 'application/json'
    if not ENABLE_JSON:
        return HttpResponse(json.dumps({'message': 'JSON Disabled'}), content_type=content_type)

    devices = {}
    reports = GraphicsDevice.objects.all()
    for report in reports:
        exts = frozenset(e.name for e in report.graphicsextension_set.all())
        limits = dict((l.name, l.value) for l in report.graphicslimit_set.all())

        device = (report.vendor, report.renderer, report.os, report.driver)
        devices.setdefault((HashableDict(limits), exts), set()).add(device)

    # TODO a lot of keys and values are repeated, maybe once the JSON is usable we can cache it every 24h
    # and make the JSON output much smaller
    sorted_devices = devices.items()  # sorted(devices.items(), key=devices.items().get)

    data = []
    for (limits, exts), deviceset in sorted_devices:
        devices = [{'vendor': v, 'renderer': r, 'os': o, 'driver': d} for (v, r, o, d) in sorted(deviceset)]
        data.append({'devices': devices, 'limits': limits, 'extensions': sorted(exts)})

    json_string = json.dumps(data, indent=1, sort_keys=True)
    return HttpResponse(json_string, content_type=content_type)


def report_opengl_json_format(request):
    return render_to_response('jsonformat.html')
