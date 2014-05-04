from userreport.models import UserReport

from django.http import HttpResponse
from django.views.decorators.cache import cache_page

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib.artist


@cache_page(60 * 120)
def ReportUsercount(request):
    reports = UserReport.objects.\
            order_by('upload_date')

    users_by_date = {}

    for report in reports:
        t = report.upload_date.date() # group by day
        users_by_date.setdefault(t, set()).add(report.user_id_hash)

    seen_users = set()
    data_scatter = ([], [], [])
    for date,users in sorted(users_by_date.items()):
        data_scatter[0].append(date)
        data_scatter[1].append(len(users))
        data_scatter[2].append(len(users - seen_users))
        seen_users |= users

    fig = Figure(figsize=(12,6))

    ax = fig.add_subplot(111)
    fig.subplots_adjust(left = 0.08, right = 0.95, top = 0.95, bottom = 0.2)

    ax.plot(data_scatter[0], data_scatter[1], marker='o')
    ax.plot(data_scatter[0], data_scatter[2], marker='o')

    ax.legend(('Total users', 'New users'), 'upper left', frameon=False)
    matplotlib.artist.setp(ax.get_legend().get_texts(), fontsize='small')

    ax.set_ylabel('Number of users per day')

    for label in ax.get_xticklabels():
        label.set_rotation(90)
        label.set_fontsize(9)

    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response, dpi=80)
    return response
