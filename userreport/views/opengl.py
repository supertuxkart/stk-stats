import re
import logging

from userreport.models import GraphicsDevice
from userreport.util.gl import glext_versions
from userreport.util import HashableDict, convert_to_int, convert_to_float
from django.http import HttpResponseNotFound
from django.db import connection
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page

LOG = logging.getLogger(__name__)


@cache_page(60 * 120)
def report_opengl_index(request):
    # TODO apply tables normalization, there are a lot of duplicate data
    with connection.cursor() as cursor:
        # Get the total user count
        cursor.execute('SELECT SUM(`usercount`) FROM `userreport_graphicsdevice`')
        num_users, = cursor.fetchone()

        # Get all distinct limits
        cursor.execute('SELECT DISTINCT `name` FROM `userreport_graphicslimit` ORDER BY `name` ASC')
        limits = [l for l, in cursor]

        # Get all distinct devices
        cursor.execute('SELECT DISTINCT `device_name` FROM `userreport_graphicsdevice` ORDER BY `device_name` ASC')
        devices = [d for d, in cursor]

        # Get all distinct extensions
        cursor.execute('''
            SELECT `GE`.`name`, SUM(`GD`.`usercount`) AS `count`
                FROM `userreport_graphicsextension` `GE`
                INNER JOIN `userreport_graphicsdevice` `GD`
                    ON ( `GE`.`device_id` = `GD`.`id` )
            GROUP BY `GE`.`name`
            ORDER BY `GE`.`name`
        ''')
        extensions = [(name, count) for name, count, in cursor]

    return render_to_response('reports/opengl_index.html', {
        'all_limits': limits,
        'all_exts': extensions,
        'all_devices': devices,
        'num_users': num_users,
        'ext_versions': glext_versions,
    }, context_instance=RequestContext(request))


@cache_page(60 * 120)
def report_opengl_feature(request, feature):
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
            v = values.setdefault(val, {}).setdefault(HashableDict({
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
            new_value = convert_to_int(val)
            if new_value is None:
                new_value = convert_to_float(val)
            val = new_value

            all_values.add(val)
            usercounts[val] = usercounts.get(val, 0) + usercount
            v = values.setdefault(val, {}).setdefault(HashableDict({
                'vendor': vendor,
                'renderer': renderer,
                'os': os,
                'device': device_name
            }), {'usercount': 0, 'drivers': set()})
            v['usercount'] += usercount
            v['drivers'].add(driver)

    if not values or values.keys() == ['false']:
        return HttpResponseNotFound()

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

    reports = GraphicsDevice.objects.filter(device_name__in=selected)
    for report in reports:
        exts = frozenset(e.name for e in report.graphicsextension_set.all())
        all_exts |= exts

        limits = dict((l.name, l.value) for l in report.graphicslimit_set.all())
        all_limits |= set(limits.keys())

        devices.setdefault(
            HashableDict({'device': report.device_name, 'os': report.os}), {}
        ).setdefault((HashableDict(limits), exts), set()).add(report.driver)

        gl_renderers.add(report.renderer)

    if len(selected) == 1 and not devices:
        return HttpResponseNotFound()

    all_limits = sorted(all_limits)
    all_exts = sorted(all_exts)

    distinct_devices = []
    for (renderer, v) in devices.items():
        for (caps, versions) in v.items():
            distinct_devices.append((renderer, sorted(versions), caps))

    distinct_devices.sort(key=lambda x: (x[0]["device"], x[0]["os"]))

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
