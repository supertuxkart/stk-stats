from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
from userreport.settings import ENABLE_VIEWS, STATIC_URL
from . import views

urlpatterns = [
    # API
    url(r'^upload/v1/$', 'userreport.views.report_upload', name='upload-v1'),

    # Index page
    url(r'^$', views.index, name='index'),

    # Favicon
    url(r'^favicon\.ico$', RedirectView.as_view(url=STATIC_URL + 'favicon.ico', permanent=True)),

    # robots.txt
    url(r'^robots\.txt$', RedirectView.as_view(url=STATIC_URL + 'robots.txt', permanent=True)),
]

if ENABLE_VIEWS:
    urlpatterns.extend([
        url(r'^opengl/$', views.report_opengl_index, name='report-opengl-index'),

        url(r'^opengl/json$', views.report_opengl_json, name='report-opengl-json'),

        url(r'^opengl/json/format$', views.report_opengl_json_format, name='report-opengl-json-format'),

        url(r'^opengl/feature/(?P<feature>[^/]+)$', views.report_opengl_feature, name='report-opengl-feature'),

        url(r'^opengl/device/(?P<device>.+)$', views.report_opengl_device, name='report-opengl-device'),

        url(r'^opengl/device', views.report_opengl_device_compare, name='report-opengl-device-compare'),

        url(r'^cpu/$', views.report_cpu, name='report-cpu'),

        url(r'^ram/$', views.report_ram, name='report-ram'),

        url(r'^os/$', views.report_os, name='report-os'),

        url(r'^usercount/$', views.report_user_count, name='report-usercount'),

        url(r'^admin/', include(admin.site.urls))
    ])
