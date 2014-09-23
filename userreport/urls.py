from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'userstats.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'userreport.views.index', name='index'),

    url(r'^upload/v1/$', 'userreport.views.Upload', name='upload-v1'),

    url(r'^opengl/$', 'userreport.views.ReportOpenglIndex', name="report-opengl-index"),

    url(r'^opengl/json$', 'userreport.views.ReportOpenglJson',
        name='report-opengl-json'),

    url(r'^opengl/json/format$', 'userreport.views.ReportOpenglJsonFormat',
        name='report-opengl-json-format'),

    url(r'^opengl/feature/(?P<feature>[^/]+)$',
        'userreport.views.ReportOpenglFeature',
        name='report-opengl-feature'),

    url(r'^opengl/device/(?P<device>.+)$',
        'userreport.views.ReportOpenglDevice',
        name='report-opengl-device'),

    url(r'^opengl/device', 'userreport.views.ReportOpenglDeviceCompare',
        name='report-opengl-device-compare'),

    url(r'^cpu/$', 'userreport.views.ReportCpu', name='report-cpu'),

    url(r'^ram/$', 'userreport.views.ReportRam', name='report-ram'),

    url(r'^os/$', 'userreport.views.ReportOS', name='report-os'),

    url(r'^usercount/$', 'userreport.views.ReportUsercount',
        name='report-usercount'),

    url(r'^admin/', include(admin.site.urls)),
)
