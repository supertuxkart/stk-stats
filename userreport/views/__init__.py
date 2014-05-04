from userreport.views.upload import Upload
from userreport.views.cpu import ReportCpu
from userreport.views.usercount import ReportUsercount
from userreport.views.opengl import ReportOpenglIndex, ReportOpenglFeature,\
    ReportOpenglDevice, ReportOpenglDevices, ReportOpenglDeviceCompare
from userreport.views.opengl_json import ReportOpenglJson,\
    ReportOpenglJsonFormat
from userreport.views.ram import ReportRam
from userreport.views.os import ReportOS

from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request):
    return render_to_response('index.html',
                              context_instance=RequestContext(request))
