from userreport.models import UserReport_hwdetect

from django.http import HttpResponse
from django.views.decorators.cache import cache_page

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

@cache_page(60 * 120)
def ReportOS(request):
    reports = UserReport_hwdetect.objects
    reports = reports.filter(data_type='hwdetect', data_version__gte=1)

    counts = {}
    for report in reports:
        #if 'linux_release' in json:
        #    counts.setdefault(repr(json['linux_release']), set()).add(report.user_id_hash)
        os = report.get_os()
        counts.setdefault(os, set()).add(report.user_id_hash)

    fig = Figure(figsize=(16, 10))
    ax = fig.add_subplot(111)

    os_counts = [(os, len(counts[os])) for os in counts.keys()]
    ax.pie([key[1] for key in os_counts],
           labels=['{0}: {1}'.format(key[0], key[1]) for key in os_counts],
           autopct='%1.1f%%')
    ax.axis('equal')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, dpi=80)

    return response
