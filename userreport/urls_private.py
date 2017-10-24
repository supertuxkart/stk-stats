from django.conf.urls import include, url
from userreport.settings import ENABLE_VIEWS
from . import views_private

urlpatterns = []

if ENABLE_VIEWS:
    urlpatterns.extend([
        url(r'^hwdetect/$', views_private.report_hwdetect),

        url(r'^hwdetect_test_data/$', views_private.report_hwdetect_test_data),

        url(r'^messages/$', views_private.report_messages),

        url(r'^profile/$', views_private.report_profile),

        url(r'^performance/$', views_private.report_performance),

        url(r'^gfx/$', views_private.report_gfx),

        url(r'^user/([0-9a-f]+)$', views_private.report_user, name='report-user'),
    ])
