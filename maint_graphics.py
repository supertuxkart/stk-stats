#!/usr/bin/env python

import os
import time
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'userreport.settings'
django.setup()

from userreport import maint
start_time = time.time()
remove_time, get_time, save_time = maint.refresh_data()
total_time = time.time() - start_time
print("--- Remove Time: {:>5.2f} seconds, {:>5.2f}% ---" .format(remove_time, remove_time / total_time * 100))
print("--- Get    Time: {:>5.2f} seconds, {:>5.2f}% ---".format(get_time, get_time / total_time * 100))
print("--- Save   Time: {:>5.2f} seconds, {:>5.2f}% ---".format(save_time, save_time / total_time * 100))
print("--- Total  Time: {:>5.2f} seconds ---".format(total_time))
