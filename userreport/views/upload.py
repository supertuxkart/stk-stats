import hashlib
import datetime
import zlib

from userreport.util import convert_to_int
from userreport.models import UserReport
from django.http import HttpResponseBadRequest, HttpResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(['POST'])
def report_upload(request):
    try:
        decompressed = zlib.decompress(request.body)
        post = QueryDict(decompressed)
    except zlib.error:
        # If zlib can't decode it, assume it's an uncompressed POST
        post = request.POST

    try:
        post_time = convert_to_int(post['time'])
        post_version = convert_to_int(post['version'])

        if post_time is None or post_version is None:
            return HttpResponseBadRequest('The "time" or "version" fields are not integers\n',
                                          content_type='text/plain')

        user_id = post['user_id']
        generation_date = datetime.datetime.utcfromtimestamp(post_time)
        data_type = post['type']
        data_version = post_version
        data = post['data']
    except KeyError:
        return HttpResponseBadRequest('Missing required fields.\n',
                                      content_type='text/plain')

    uploader = request.META['REMOTE_ADDR']
    # Fix the IP address if running via proxy on localhost
    if uploader == '127.0.0.1':
        try:
            uploader = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        except KeyError:
            pass

    user_id_hash = hashlib.sha1(user_id.encode('utf-8')).hexdigest()

    report = UserReport(
        uploader=uploader,
        user_id_hash=user_id_hash,
        generation_date=generation_date,
        data_type=data_type,
        data_version=data_version,
        data=data
    )
    report.save()

    return HttpResponse('OK', content_type='text/plain')
