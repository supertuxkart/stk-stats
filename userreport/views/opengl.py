from userreport.models import GraphicsDevice, GraphicsExtension, GraphicsLimit
from userreport.gl import glext_versions

from django.db import connection, transaction
from django.db.models import Sum
from django.shortcuts import render_to_response


def ReportOpenglIndex(request):
    num_users = GraphicsDevice.objects.\
        aggregate(Sum('usercount'))['usercount__sum']

    exts = GraphicsExtension.objects.values('name').\
        select_related('device').\
        annotate(count=Sum('device__usercount')).values('name', 'count')
    all_exts = set(e['name'] for e in list(exts))
    ext_devices = {e['name']: e['count'] for e in list(exts)}

    limits = GraphicsLimit.objects.values('name')
    all_limits = set(l['name'] for l in list(limits))

    devices = GraphicsDevice.objects.values('device_name').\
        annotate(count=Sum('usercount'))
    all_devices = {}
    for device in devices:
        all_devices[device['device_name']] = device['count']

    all_limits = sorted(all_limits)
    all_exts = sorted(all_exts)

    return render_to_response('reports/opengl_index.html', {
        'all_limits': all_limits,
        'all_exts': all_exts,
        'all_devices': all_devices,
        'ext_devices': ext_devices,
        'num_users': num_users,
        'ext_versions': glext_versions,
    })
