from userreport.models import UserReport, UserReport_hwdetect, GraphicsDevice, \
    GraphicsExtension, GraphicsLimit
from django.db import transaction

import logging

LOG = logging.getLogger(__name__)


@transaction.atomic
def refresh_data():
    _remove_old_records()
    devices = _get_devices()
    _save_devices(devices)


def _remove_old_records():
    LOG.info('Removing old data')
    GraphicsDevice.objects.all().delete()
    GraphicsExtension.objects.all().delete()
    GraphicsLimit.objects.all().delete()


def _get_devices():
    LOG.info('Collecting data')

    reports = UserReport_hwdetect.objects.filter(data_type='hwdetect',
                                                 data_version__gte=1)
    devices = {}
    count = 0
    len_reports = len(reports)
    for report in reports:
        if not report.has_data():
            continue

        device = report.gl_device_identifier()
        vendor = report.gl_vendor()
        renderer = report.gl_renderer()
        os = report.get_os()
        driver = report.gl_driver()
        exts = report.gl_extensions()
        limits = report.gl_limits()
        report.clear_cache()

        devices.setdefault(
            (device, vendor, renderer, os, driver, exts, tuple(sorted(limits.items()))),
            set()
        ).add(report.user_id_hash)

        count += 1
        if count % 100 == 0:
            LOG.info("%d / %d..." % (count, len_reports))
    LOG.info('Collected %d devices' % len_reports)

    return devices


def _save_devices(devices):
    LOG.info('Saving device records')
    count = 0
    for (device, vendor, renderer, os, driver, exts, limits), users \
            in devices.items():
        # Add GraphicsDevice
        gd = GraphicsDevice(device_name=device, vendor=vendor,
                            renderer=renderer, os=os, driver=driver,
                            usercount=len(users))
        gd.save()
        device_id = gd.id

        # Add GraphicsExtension
        if exts:
            for ext in exts:
                e = GraphicsExtension(device_id=device_id, name=ext)
                e.save()

        # Add GraphicsLimit
        if limits:
            for limit in limits:
                l = GraphicsLimit(device_id=device_id, name=limit[0],
                                  value=limit[1])
                l.save()

        count += 1
        if count % 100 == 0:
            LOG.info("%d / %d..." % (count, len(devices)))
    LOG.info('Finished')
