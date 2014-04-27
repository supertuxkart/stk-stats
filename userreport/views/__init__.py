from userreport.views.upload import Upload
from userreport.views.cpu import ReportCpu
# from userreport.views.usercount import ReportUsercount
from userreport.views.opengl import ReportOpenglIndex, ReportOpenglFeature,\
    ReportOpenglDevice, ReportOpenglDevices, ReportOpenglDeviceCompare
from userreport.views.opengl_json import ReportOpenglJson,\
    ReportOpenglJsonFormat

from django.shortcuts import render_to_response


def index(request):
    return render_to_response('index.html')
