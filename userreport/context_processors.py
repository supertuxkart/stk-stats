from django.conf import settings


def site_constants(request):
    return {'PROJECT_NAME': settings.PROJECT_NAME,
            'PROJECT_URL': settings.PROJECT_URL,
            'ENABLE_CPU': settings.ENABLE_CPU,
            'ENABLE_VIEWS': settings.ENABLE_VIEWS,
            'ENABLE_JSON': settings.ENABLE_JSON}
