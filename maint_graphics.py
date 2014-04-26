#!/usr/bin/env python

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'userreport.settings'

from userreport import maint
maint.refresh_data()
