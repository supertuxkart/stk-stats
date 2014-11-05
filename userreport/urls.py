from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'userstats.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'userreport.views.index', name='index'),

    url(r'^upload/v1/$', 'userreport.views.report_upload', name='upload-v1'),

    url(r'^opengl/$', 'userreport.views.report_opengl_index', name="report-opengl-index"),

    url(r'^opengl/json$', 'userreport.views.report_opengl_json',
        name='report-opengl-json'),

    url(r'^opengl/json/format$', 'userreport.views.report_opengl_json_format',
        name='report-opengl-json-format'),

    url(r'^opengl/feature/(?P<feature>[^/]+)$',
        'userreport.views.report_opengl_feature',
        name='report-opengl-feature'),

    url(r'^opengl/device/(?P<device>.+)$',
        'userreport.views.report_opengl_device',
        name='report-opengl-device'),

    url(r'^opengl/device', 'userreport.views.report_opengl_device_compare',
        name='report-opengl-device-compare'),

    url(r'^cpu/$', 'userreport.views.report_cpu', name='report-cpu'),

    url(r'^ram/$', 'userreport.views.report_ram', name='report-ram'),

    url(r'^os/$', 'userreport.views.report_os', name='report-os'),

    url(r'^usercount/$', 'userreport.views.report_user_count',
        name='report-usercount'),

    url(r'^admin/', include(admin.site.urls)),
)
