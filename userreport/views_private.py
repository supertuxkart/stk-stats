from userreport.models import UserReport, UserReport_hwdetect
from userreport.util import hashabledict

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import re
import numpy
import json


def render_reports(request, reports, template, args):
    paginator = Paginator(reports, args.get('pagesize', 100))
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        report_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        report_page = paginator.page(paginator.num_pages)

    args['report_page'] = report_page
    return render_to_response(template, args)


def report_user(request, user):
    reports = UserReport.objects.order_by('-upload_date')
    reports = reports.filter(user_id_hash=user)

    return render_reports(request, reports, 'reports/user.html', {'user': user})


def report_messages(request):
    reports = UserReport.objects.order_by('-upload_date')
    reports = reports.filter(data_type='message', data_version__gte=1)

    return render_reports(request, reports, 'reports/message.html', {})


def report_profile(request):
    reports = UserReport.objects.order_by('-upload_date')
    reports = reports.filter(data_type='profile', data_version__gte=2)

    return render_reports(request, reports, 'reports/profile.html', {'pagesize': 20})


def report_hwdetect(request):
    reports = UserReport.objects.order_by('-upload_date')
    reports = reports.filter(data_type='hwdetect', data_version__gte=1)

    return render_reports(request, reports, 'reports/hwdetect.html', {})


def report_gfx(request):
    reports = UserReport.objects.order_by('-upload_date')
    reports = reports.filter(data_type='hwdetect', data_version__gte=1)

    return render_reports(request, reports, 'reports/gfx.html', {'pagesize': 1000})


def report_performance(request):
    reports = UserReport.objects.order_by('upload_date')
    reports = reports.filter(
        Q(data_type='hwdetect', data_version__gte=5) |
        Q(data_type='profile', data_version__gte=2)
    )
    # reports = reports[:500]

    def summarise_hwdetect(report):
        json = report.data_json_nocache()
        return {
            'cpu_identifier': json['cpu_identifier'],
            'device': report.gl_device_identifier(),
            'build_debug': json['build_debug'],
            'build_revision': json['build_revision'],
            'build_datetime': json['build_datetime'],
            'gfx_res': (json['video_xres'], json['video_yres']),
        }

    def summarise_profile(report):
        json = report.data_json_nocache()
        if 'map' in json:
            mapname = json['map']
        else:
            mapname = 'unknown'  # e.g. random maps
        msecs = None
        shadows = False
        for name, table in json['profiler'].items():
            m = re.match(r'Profiling Information for: root \(Time in node: (\d+\.\d+) msec/frame\)', name)
            if m:
                try:
                    msecs = float(table['data']['render'][2])
                except KeyError:
                    pass

                try:
                    if float(table['data']['render'][0]['render submissions'][0]['render shadow map'][2]):
                        shadows = True
                except (KeyError, TypeError):
                    pass

        if msecs is None:
            return None

        options = []
        if shadows:
            options.append('S')

        return {
            'msecs': msecs,
            'map': mapname,
            'time': json['time'],
            'options': '[%s]' % '+'.join(options),
        }

    profiles = []
    last_hwdetect = {}
    for report in reports:
        if report.data_type == 'hwdetect':
            last_hwdetect[report.user_id_hash] = summarise_hwdetect(report.downcast())
        elif report.data_type == 'profile':
            if report.user_id_hash in last_hwdetect:
                hwdetect = last_hwdetect[report.user_id_hash]
                if hwdetect['build_debug']:
                    continue
                prof = summarise_profile(report)
                if prof is not None:
                    profiles.append([report.user_id_hash, hwdetect, prof])

    datapoints = {}
    for user, hwdetect, profile in profiles:
        if profile['map'] != 'Death Canyon':
            continue
        if profile['time'] != 5:
            continue
        if profile['msecs'] is None or float(profile['msecs']) == 0:
            continue
        fps = 1000.0 / profile['msecs']
        title = '%s %s' % (hwdetect['device'], profile['options'])
        datapoints.setdefault(title, []).append(fps)

    #    return render_to_response('reports/performance.html', {'data': datapoints, 'reports': profiles})

    sorted_datapoints = sorted(datapoints.items(), key=lambda kv: -numpy.median(kv[1]))

    print("# %d datapoints" % sum(len(v) for k, v in sorted_datapoints))

    data_boxplot = [v for k, v in sorted_datapoints]
    data_scatter = ([], [])
    for i in range(len(data_boxplot)):
        for x in data_boxplot[i]:
            data_scatter[0].append(i + 1)
            data_scatter[1].append(x)

    fig = Figure(figsize=(16, 0.25 * len(datapoints.items())))

    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.22, right=0.98, top=0.98, bottom=0.05)

    ax.grid(True)

    ax.boxplot(data_boxplot, vert=0, sym='')
    ax.scatter(data_scatter[1], data_scatter[0], marker='x')

    ax.set_xlim(0.1, 1000)
    ax.set_xscale('log')
    ax.set_xlabel('Framerate (fps)')

    ax.set_yticklabels([k for k, v in sorted_datapoints], fontsize=8)
    ax.set_ylabel('Device [options: Shadows + Water reflections]')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, dpi=80)
    return response


def report_hwdetect_test_data(request):
    reports = UserReport_hwdetect.objects
    reports = reports.filter(data_type='hwdetect', data_version__gte=1)

    data = set()
    for report in reports:
        json = report.data_json_nocache()
        relevant = {
            'os_unix': json['os_unix'],
            'os_linux': json['os_linux'],
            'os_macosx': json['os_macosx'],
            'os_win': json['os_win'],
            'gfx_card': json['gfx_card'],
            'gfx_drv_ver': json['gfx_drv_ver'],
            'gfx_mem': json['gfx_mem'],
            'GL_VENDOR': json['GL_VENDOR'],
            'GL_RENDERER': json['GL_RENDERER'],
            'GL_VERSION': json['GL_VERSION'],
            'GL_EXTENSIONS': json['GL_EXTENSIONS'],
        }
        data.add(hashabledict(relevant))

    json = json.dumps(list(data), indent=1, sort_keys=True)
    return HttpResponse('var hwdetectTestData = %s' % json, content_type='text/plain')
