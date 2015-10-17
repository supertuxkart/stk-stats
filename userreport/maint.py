import logging
import time
from collections import defaultdict

from userreport.models import UserReport_hwdetect
from userreport.settings_local import DATABASES
import pymysql
import pymysql.err
import pymysql.cursors

LOG = logging.getLogger(__name__)


def refresh_data():
    connection = pymysql.connect(host=DATABASES['default']['HOST'],
                                 user=DATABASES['default']['USER'],
                                 password=DATABASES['default']['PASSWORD'],
                                 db=DATABASES['default']['NAME'],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.SSCursor)

    remove_time = _remove_old_records(connection)
    devices, get_time = _get_devices()
    save_time = _save_devices(connection, devices)

    connection.close()
    LOG.info('Finished')

    return remove_time, get_time, save_time


def _remove_old_records(connection):
    LOG.info('Removing old data')
    start_time = time.time()
    with connection.cursor() as cursor:
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0;'
                       'TRUNCATE TABLE userreport_graphicsextension;'
                       'TRUNCATE TABLE userreport_graphicslimit;'
                       'TRUNCATE TABLE userreport_graphicsdevice;'
                       'SET FOREIGN_KEY_CHECKS = 1;')

    connection.commit()

    return time.time() - start_time


def _get_devices():
    LOG.info('Collecting data')
    start_time = time.time()

    reports = UserReport_hwdetect.objects.filter(data_type='hwdetect', data_version__gte=1)
    devices = defaultdict(set)
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

        devices[(device, vendor, renderer, os, driver, exts, tuple(sorted(limits.items())))].add(report.user_id_hash)

        count += 1
        if count % 100 == 0:
            LOG.info("%d / %d..." % (count, len_reports))
    LOG.info('Collected %d devices' % len_reports)

    return devices, time.time() - start_time


def _save_devices(connection, devices):
    LOG.info('Saving device records')
    start_time = time.time()
    count = 0
    count_total = len(devices)

    sql_device = 'INSERT INTO `userreport_graphicsdevice`(`device_name`, `vendor`, `renderer`, `os`, `driver`, `usercount`) ' \
                 'VALUES (%s, %s, %s, %s, %s, %s)'
    sql_ext = 'INSERT INTO `userreport_graphicsextension`(`device_id`, `name`) VALUES'
    sql_ext_value = "(%s, '%s')"
    sql_limit = 'INSERT INTO `userreport_graphicslimit`(`device_id`, `name`, `value`) VALUES'
    sql_limit_value = "(%s, '%s', '%s')"
    for (device, vendor, renderer, os, driver, exts, limits), users in devices.items():
        try:
            # Add GraphicsDevice
            with connection.cursor() as cursor:
                cursor.execute(sql_device, (device, vendor, renderer, os, driver, len(users)))
                device_id = cursor.lastrowid

                # Add GraphicsExtension
                if exts:
                    sql_exts = sql_ext + ", ".join([sql_ext_value % (device_id, ext) for ext in exts])
                    cursor.execute(sql_exts)

                # Add GraphicsLimit
                if limits:
                    sql_limits = sql_limit + ", ".join(
                        [sql_limit_value % (device_id, limit[0], limit[1]) for limit in limits])
                    cursor.execute(sql_limits)

            if count % 100 == 0:
                # connection.commit()
                LOG.info("%d / %d..." % (count, count_total))
            count += 1
        except pymysql.err.Warning as e:
            print("MYSQL WARNING (device_id = %s): %s" % (device, e))

    connection.commit()
    return time.time() - start_time
