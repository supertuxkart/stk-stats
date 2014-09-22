from django.conf import settings


def site_constants(request):
    return {'PROJECT_NAME': settings.PROJECT_NAME,
            'PROJECT_URL': settings.PROJECT_URL}
