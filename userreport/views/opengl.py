from userreport.models import GraphicsDevice, GraphicsExtension
from userreport.gl import glext_versions

from django.db import connection, transaction
from django.shortcuts import render_to_response

def ReportOpenglIndex(request):
    cursor = connection.cursor()

    cursor.execute('''
        SELECT SUM(usercount)
        FROM userreport_graphicsdevice
    ''')
    num_users = sum(c for (c,) in cursor)

    cursor.execute('''
        SELECT name, SUM(usercount)
        FROM userreport_graphicsextension e
        JOIN userreport_graphicsdevice d
            ON e.device_id = d.id
        GROUP BY name
    ''')
    exts = cursor.fetchall()
    all_exts = set(n for n,c in exts)
    ext_devices = dict((n,c) for n,c in exts)

    cursor.execute('''
        SELECT name
        FROM userreport_graphicslimit l
        JOIN userreport_graphicsdevice d
            ON l.device_id = d.id
        GROUP BY name
    ''')
    all_limits = set(n for (n,) in cursor.fetchall())

    cursor.execute('''
        SELECT device_name, SUM(usercount)
        FROM userreport_graphicsdevice
        GROUP BY device_name
    ''')
    all_devices = dict((n,c) for n,c in cursor.fetchall())

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
