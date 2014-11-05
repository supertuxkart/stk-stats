from userreport.models import UserReport

from django.http import HttpResponse
from django.views.decorators.cache import cache_page

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


@cache_page(60 * 120)
def report_ram(request):
    reports = UserReport.objects
    reports = reports.filter(data_type='hwdetect', data_version__gte=1)

    counts = {}
    for report in reports:
        report_json = report.get_data_json()
        ram = report_json.get("ram_total", 0)

        counts.setdefault(ram, set()).add(report.user_id_hash)

    datapoints = [(0, 0)]
    accum = 0
    for size, count in sorted(counts.items()):
        accum += len(count)
        datapoints.append((size, accum))

    fig = Figure(figsize=(16, 10))

    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.05)

    ax.grid(True)

    if accum:  # We have data
        ax.step([d[0] for d in datapoints], [100 * (1 - float(d[1]) / accum) for d in datapoints])

    ax.set_xticks([0, 256, 512] + [1024 * n for n in range(1, 9)])
    ax.set_xlim(0, 8192)
    ax.set_xlabel('RAM (megabytes)')

    ax.set_yticks(range(0, 101, 5))
    ax.set_ylim(0, 100)
    ax.set_ylabel('Cumulative percentage of users')

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, dpi=80)

    return response
