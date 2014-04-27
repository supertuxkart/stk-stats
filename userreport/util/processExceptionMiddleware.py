import traceback
import sys

class ProcessExceptionMiddleware(object):
    def process_exception(self, request, exception):
        print(exception) # or log, or whatever.

        # print traceback
        print('\n'.join(traceback.format_exception(*sys.exc_info())))
