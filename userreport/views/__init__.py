from userreport.views.upload import report_upload
from userreport.views.cpu import report_cpu
from userreport.views.usercount import report_user_count
from userreport.views.opengl import report_opengl_index, report_opengl_feature, \
    report_opengl_device, report_opengl_devices, report_opengl_device_compare
from userreport.views.opengl_json import report_opengl_json, \
    report_opengl_json_format
from userreport.views.ram import report_ram
from userreport.views.os import report_os

from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))
