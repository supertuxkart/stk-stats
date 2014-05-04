from userreport.models import GraphicsDevice, GraphicsExtension, GraphicsLimit
from userreport.util.gl import glext_versions
from userreport.util import hashabledict

from django.db import connection, transaction
from django.db.models import Sum
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page

import re


@cache_page(60 * 120)
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
    }, context_instance=RequestContext(request))


@cache_page(60 * 120)
def ReportOpenglFeature(request, feature):
    all_values = set()
    usercounts = {}
    values = {}

    cursor = connection.cursor()

    is_extension = False
    if re.search(r'[a-z]', feature):
        is_extension = True

    if is_extension:
        cursor.execute('''
            SELECT vendor, renderer, os, driver, device_name, SUM(usercount),
                (SELECT 1 FROM userreport_graphicsextension e WHERE e.name = %s AND e.device_id = d.id) AS val
            FROM userreport_graphicsdevice d
            GROUP BY vendor, renderer, os, driver, device_name, val
        ''', [feature])

        for vendor, renderer, os, driver, device_name, usercount, val in cursor:
            val = 'true' if val else 'false'
            all_values.add(val)
            usercounts[val] = usercounts.get(val, 0) + usercount
            v = values.setdefault(val, {}).setdefault(hashabledict({
                'vendor': vendor,
                'renderer': renderer,
                'os': os,
                'device': device_name
            }), {'usercount': 0, 'drivers': set()})
            v['usercount'] += usercount
            v['drivers'].add(driver)

    else:
        cursor.execute('''
            SELECT value, vendor, renderer, os, driver, device_name, usercount
            FROM userreport_graphicslimit l
            JOIN userreport_graphicsdevice d
                ON l.device_id = d.id
            WHERE name = %s
        ''', [feature])

        for val, vendor, renderer, os, driver, device_name, usercount in cursor:
            # Convert to int/float if possible, for better sorting
            try: val = int(val)
            except ValueError:
                try: val = float(val)
                except ValueError: pass

            all_values.add(val)
            usercounts[val] = usercounts.get(val, 0) + usercount
            v = values.setdefault(val, {}).setdefault(hashabledict({
                'vendor': vendor,
                'renderer': renderer,
                'os': os,
                'device': device_name
            }), {'usercount': 0, 'drivers': set()})
            v['usercount'] += usercount
            v['drivers'].add(driver)

    if values.keys() == [] or values.keys() == ['false']:
        raise Http404

    num_users = sum(usercounts.values())

    return render_to_response('reports/opengl_feature.html', {
        'feature': feature,
        'all_values': all_values,
        'values': values,
        'is_extension': is_extension,
        'usercounts': usercounts,
        'num_users': num_users,
    })


@cache_page(60 * 120)
def ReportOpenglDevices(request, selected):
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

def ReportOpenglDevice(request, device):
    return ReportOpenglDevices(request, [device])

def ReportOpenglDeviceCompare(request):
    return ReportOpenglDevices(request, request.GET.getlist('d'))
