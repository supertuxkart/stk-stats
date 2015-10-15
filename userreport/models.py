# This file is mainly for detecting the graphics used and storing these
# information in string that are later used for the report

import json
import re
import logging

from django.db import models

LOG = logging.getLogger(__name__)


class UserReport(models.Model):
    uploader = models.GenericIPAddressField(editable=False)

    # Hex SHA-1 digest of user's reported ID
    # (The hashing means that publishing the database won't let people upload
    # faked reports under someone else's user ID, and also ensures a simple
    # consistent structure)
    user_id_hash = models.CharField(max_length=40, db_index=True, editable=False)

    # When the server received the upload
    upload_date = models.DateTimeField(auto_now_add=True, db_index=True, editable=False)

    # When the user claims to have generated the report
    generation_date = models.DateTimeField(editable=False)

    data_type = models.CharField(max_length=16, db_index=True, editable=False)
    data_version = models.IntegerField(editable=False)
    data = models.TextField(editable=False)

    def get_data_json(self, cache=True):
        """
        Get the json data
        :param cache flag that indicates to cache the json
        :return json
        """

        def get_json(data):
            try:
                return json.loads(data)
            except ValueError:
                LOG.warning("The data_json is invalid for id = %d" % self.id)
                return {}

        # Cache the json
        if cache and not hasattr(self, 'cached_json'):
            self.cached_json = get_json(self.data)

            return self.cached_json

        return get_json(self.data)

    def has_data(self):
        return bool(self.get_data_json())

    def clear_cache(self):
        delattr(self, 'cached_json')

    def downcast(self):
        if self.data_type == 'hwdetect':
            return UserReport_hwdetect.objects.get(id=self.id)

        return self


class UserReport_hwdetect(UserReport):
    pattern_device_identifier = re.compile(
        r'^(?:AMD |ATI |NVIDIA |Mesa DRI )?(.*?)\s*(?:GEM 20100328 2010Q1|GEM 20100330 DEVELOPMENT|GEM 20091221 2009Q4|20090101|Series)?\s*(?:x86|/AGP|/PCI|/MMX|/MMX\+|/SSE|/SSE2|/3DNOW!|/3DNow!|/3DNow!\+)*(?: TCL| NO-TCL)?(?: DRI2)?(?: \(Microsoft Corporation - WDDM\))?(?: OpenGL Engine)?\s*$')

    pattern_gl_version = re.compile(r'^(\d+\.\d+).*')

    pattern_gl_driver_mesa_git = re.compile(r'^OpenGL \d+\.\d+(?:\.\d+)? (Mesa \d+\.\d+)-devel \(git-([a-f0-9]+)')
    pattern_gl_driver_mesa_normal = re.compile(r'^OpenGL \d+\.\d+(?:\.\d+)? (Mesa .*)$')
    pattern_gl_driver_nvidia = re.compile(r'^OpenGL \d+\.\d+(?:\.\d+)? NVIDIA (.*)$')
    pattern_gl_driver_amd_direct = re.compile(r'^OpenGL (\d+\.\d+\.\d+) Compatibility Profile Context(?: FireGL)?$')
    pattern_gl_driver_amd_indirect = re.compile(
        r'^OpenGL 1\.4 \((\d+\.\d+\.\d+) Compatibility Profile Context(?: FireGL)?\)$')

    class Meta:
        proxy = True

    def get_os(self):
        """:return the operating system"""
        data_json = self.get_data_json()
        if data_json:
            if data_json.get('os_win'):
                return 'Windows'
            elif data_json.get('os_linux'):
                return 'Linux'
            elif data_json.get('os_macosx'):
                return 'OS X'
            elif data_json.get('os_unix'):
                return 'Other Unix'

        return 'Unknown'

    def gl_renderer(self):
        data_json = self.get_data_json()
        if 'GL_RENDERER' not in data_json:
            return ""

        # The renderer string should typically be interpreted as UTF-8
        try:
            return data_json['GL_RENDERER'].encode('iso-8859-1').decode('utf-8').strip()
        except UnicodeError:
            return data_json['GL_RENDERER'].strip()

    def gl_extensions(self):
        data_json = self.get_data_json()
        if 'GL_EXTENSIONS' not in data_json:
            LOG.warning("The GL_EXTENSIONS does not exist for id = %d" % self.id)
            return None

        values = re.split(r'\s+', data_json['GL_EXTENSIONS'])
        # skip empty strings (e.g. no extensions at all, or leading/trailing space)
        return frozenset(v for v in values if v)

    def gl_limits(self):
        data_json = self.get_data_json()

        limits = {}
        for (k, v) in data_json.items():
            if not k.startswith('GL_'):
                continue

            if k == 'GL_VERSION':
                m = re.match(self.pattern_gl_version, v)
                if m:
                    limits[k] = '%s [...]' % m.group(1)

                limits['GL_VERSION' + '_COMPLETE'] = v  # non standard
                continue

            if k in ('GL_RENDERER', 'GL_EXTENSIONS'):
                continue

            # Hide some values that got deleted from the report in r8953, for consistency
            if k in ('GL_MAX_COLOR_MATRIX_STACK_DEPTH', 'GL_FRAGMENT_PROGRAM_ARB.GL_MAX_PROGRAM_ADDRESS_REGISTERS_ARB',
                     'GL_FRAGMENT_PROGRAM_ARB.GL_MAX_PROGRAM_NATIVE_ADDRESS_REGISTERS_ARB'):
                continue

            # Hide some pixel depth values that are not really correlated with device
            if k in ('GL_RED_BITS', 'GL_GREEN_BITS', 'GL_BLUE_BITS', 'GL_ALPHA_BITS', 'GL_INDEX_BITS', 'GL_DEPTH_BITS',
                     'GL_STENCIL_BITS',
                     'GL_ACCUM_RED_BITS', 'GL_ACCUM_GREEN_BITS', 'GL_ACCUM_BLUE_BITS', 'GL_ACCUM_ALPHA_BITS'):
                continue

            limits[k] = v

        return limits

    def gl_device_identifier(self):
        """
        Construct a nice-looking concise graphics device identifier
        (skipping boring hardware/driver details)
        """
        renderer = self.gl_renderer()
        m = re.match(self.pattern_device_identifier, renderer)
        if m:
            renderer = m.group(1)

        return renderer.strip()

    def gl_vendor(self):
        return self.get_data_json().get('GL_VENDOR', '').strip()

    def gl_driver(self):
        """
        Construct a nice string identifying the driver
        It tries all the known possibilities for drivers to find the used one
        """
        data_json = self.get_data_json()
        if 'gfx_drv_ver' not in data_json or 'GL_VENDOR' not in data_json:
            return ''

        gfx_drv_ver = data_json['gfx_drv_ver']

        # Try the Mesa git style first
        m = re.match(self.pattern_gl_driver_mesa_git, gfx_drv_ver)
        if m:
            return '%s-git-%s' % (m.group(1), m.group(2))

        # Try the normal Mesa style
        m = re.match(self.pattern_gl_driver_mesa_normal, gfx_drv_ver)
        if m:
            return m.group(1)

        # Try the NVIDIA Linux style
        m = re.match(self.pattern_gl_driver_nvidia, gfx_drv_ver)
        if m:
            return m.group(1)

        # Try the ATI Catalyst Linux style
        m = re.match(self.pattern_gl_driver_amd_direct, gfx_drv_ver)
        if m:
            return m.group(1)

        # Try the non-direct-rendering ATI Catalyst Linux style
        m = re.match(self.pattern_gl_driver_amd_indirect, gfx_drv_ver)
        if m:
            return '%s (indirect)' % m.group(1)

        possibilities = []  # Otherwise the iteration at the will will

        # Try to guess the relevant Windows driver
        # (These are the ones listed in lib/sysdep/os/win/wgfx.cpp in the 0 AD code)
        if data_json['GL_VENDOR'] == 'NVIDIA Corporation':
            possibilities = [
                # Assume 64-bit takes precedence
                r'nvoglv64.dll \((.*?)\)',
                r'nvoglv32.dll \((.*?)\)',
                r'nvoglnt.dll \((.*?)\)'
            ]

        if data_json['GL_VENDOR'] in ('ATI Technologies Inc.', 'Advanced Micro Devices, Inc.'):
            possibilities = [
                r'atioglxx.dll \((.*?)\)',
                r'atioglx2.dll \((.*?)\)',
                r'atioglaa.dll \((.*?)\)'
            ]

        if data_json['GL_VENDOR'] == 'Intel':
            possibilities = [
                # Assume 64-bit takes precedence
                r'ig4icd64.dll \((.*?)\)',
                r'ig4icd32.dll \((.*?)\)',
                # Legacy 32-bit
                r'iglicd32.dll \((.*?)\)',
                r'ialmgicd32.dll \((.*?)\)',
                r'ialmgicd.dll \((.*?)\)'
            ]

        for i in possibilities:
            m = re.search(i, gfx_drv_ver)
            if m:
                return m.group(1)

        return gfx_drv_ver


class GraphicsDevice(models.Model):
    device_name = models.CharField(max_length=128, db_index=True)
    vendor = models.CharField(max_length=64)
    renderer = models.CharField(max_length=128)
    os = models.CharField(max_length=16)
    driver = models.CharField(max_length=128)
    usercount = models.IntegerField()


class GraphicsExtension(models.Model):
    device = models.ForeignKey(GraphicsDevice)
    name = models.CharField(max_length=128, db_index=True)


class GraphicsLimit(models.Model):
    device = models.ForeignKey(GraphicsDevice)
    name = models.CharField(max_length=128, db_index=True)
    value = models.CharField(max_length=64)
