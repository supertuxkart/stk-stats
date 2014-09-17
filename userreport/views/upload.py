from userreport.models import UserReport

import hashlib
import datetime
import zlib

from django.http import HttpResponseBadRequest, HttpResponse, QueryDict

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(['POST'])
def Upload(request):

    try:
        decompressed = zlib.decompress(request.body)
        POST = QueryDict(decompressed)
    except zlib.error:
        # If zlib can't decode it, assume it's an uncompressed POST
        POST = request.POST
        
    try:
        user_id = POST['user_id']
        generation_date = datetime.datetime.utcfromtimestamp(int(POST['time']))
        data_type = POST['type']
        data_version = int(POST['version'])
        data = POST['data']
    except KeyError as e:
        return HttpResponseBadRequest('Missing required fields.\n',
                                      content_type='text/plain')

    uploader = request.META['REMOTE_ADDR']
    # Fix the IP address if running via proxy on localhost
    if uploader == '127.0.0.1':
        try:
            uploader = request.META['HTTP_X_FORWARDED_FOR']\
                              .split(',')[0].strip()
        except KeyError:
            pass

    user_id_bytes = user_id.encode('utf-8')
    user_id_hash = hashlib.sha1(user_id_bytes).hexdigest()

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
