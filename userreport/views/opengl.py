from userreport.models import GraphicsDevice, GraphicsExtension, GraphicsLimit
from userreport.gl import glext_versions

from django.db import connection, transaction
from django.db.models import Sum
from django.shortcuts import render_to_response

import re


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


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
