Statistics Browser
==================

This repository has been forked from the 0 A.D. project.
The intent is to use this as a base for a statistics collection
system for SuperTuxKart.

Installation
============

Before proceeding, install the following packages using your favorite package
manager:
 * postgresql 9.0+
 * python 3.3+
 * python-virtualenv
 * python-distutils-extra
 * memcached
 * gcc
 * gfortran
 * libatlas-base-dev
 * libatlas3gf-base
 * libfreetype6-dev
 * libxft-dev

Several of the above packages are dependencies for `python-matplotlib`. This module
is difficult to install via `pip`, so you may want to create a virtualenv with
site-packages available to it.

From the repository root, run:
```
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `userreport/settings_local.EXAMPLE.py` to `userreport/settings_local.py`, and
edit the settings inside that file to match your environment.

Make sure you have created a database for yourself.

Run `python manage.py syncdb` to create your database.

To start the Django development server, run `python manage.py runserver`

Submitting Data
===============

This tool supports one report, called `hwdetect`. This report consists of the following
POST data:

 * user_id: Unique ID of the user
 * generation_date: Time report was generated, as a POSIX timestamp
 * data_type: Name of the report - in this case, `hwdetect`
 * data_version: Report version. OAD currently reports `11`
 * data: A json string with all parameters of the report. See below for an incomplete example.

```JSON
{"os_unix":1,
 "os_bsd":0,
 "os_linux":1,
 "os_android":0,
 "os_macosx":0,
 "os_win":0,
 "arch_ia32":0,
 "arch_amd64":1,
 "arch_arm":0,
 "build_debug":0,
 "build_opengles":0,
 "build_datetime":"Feb 18 2014 11:27:25",
 "build_revision":"14386-release",
 "build_msc":0,
 "build_icc":0,
 "build_gcc":408,
 "build_clang":0,
 "gfx_card":"Intel Open Source Technology Center Mesa DRI Intel(R) Haswell Mobile ",
 "gfx_drv_ver":"OpenGL 3.0 Mesa 10.1.1",
 "snd_card":"",
 "snd_drv_ver":"",
 "GL_VERSION":"3.0 Mesa 10.1.1",
 "GL_VENDOR":"Intel Open Source Technology Center",
 "GL_RENDERER":"Mesa DRI Intel(R) Haswell Mobile ",
 "GL_EXTENSIONS":"GL_ARB_multisample GL_EXT_abgr ... GL_EXT_shader_integer_mix",
 "GL_MAX_LIGHTS":8,
 "GL_MAX_CLIP_PLANES":8, 
 "GL_MAX_MODELVIEW_STACK_DEPTH":32,
 "GL_MAX_PROJECTION_STACK_DEPTH":32,
 ... more GL limits ...
 "GL_SAMPLES_PASSED.GL_QUERY_COUNTER_BITS":64,
 "GL_SHADING_LANGUAGE_VERSION_ARB":"1.30",
 "GL_MAX_VERTEX_ATTRIBS_ARB":16,
 "GL_MAX_VERTEX_UNIFORM_COMPONENTS_ARB":16384,
 "GL_MAX_VARYING_FLOATS_ARB":128,
 ... and more GL limits ...
 "GL_MAX_ARRAY_TEXTURE_LAYERS_EXT":2048,
 "GL_FRAGMENT_PROGRAM_ARB.GL_MAX_PROGRAM_NATIVE_TEX_INDIRECTIONS_ARB":1024,
 "GL_FRAGMENT_PROGRAM_ARB.GL_MAX_PROGRAM_NATIVE_TEMPORARIES_ARB":256,
 "GL_FRAGMENT_PROGRAM_ARB.GL_MAX_PROGRAM_NATIVE_PARAMETERS_ARB":1024,
 "GL_FRAGMENT_PROGRAM_ARB.GL_MAX_PROGRAM_NATIVE_ATTRIBS_ARB":12,
 "glx_extensions":"GLX_ARB_create_context GLX_ARB_fbconfig_float GLX_ARB_framebuffer_sRGB GLX_ARB_get_proc_address GLX_ARB_multisample ... GLX_INTEL_swap_event ",
 "GLX_RENDERER_VENDOR_ID_MESA":32902,
 "GLX_RENDERER_DEVICE_ID_MESA":2582,
 "GLX_RENDERER_VERSION_MESA[0]":10,
 "GLX_RENDERER_VERSION_MESA[1]":1,
 "GLX_RENDERER_VENDOR_ID_MESA.string":"Intel Open Source Technology Center",
 "GLX_RENDERER_DEVICE_ID_MESA.string":"Mesa DRI Intel(R) Haswell Mobile ",
 "video_xres":1024,
 "video_yres":768,
 "video_bpp":32,
 "video_desktop_xres":3840,
 "video_desktop_yres":1397,
 "video_desktop_bpp":24,
 "video_desktop_freq":0,
 "uname_sysname":"Linux",
 "uname_release":"3.14.1-1-ARCH",
 "uname_version":"#1 SMP PREEMPT Mon Apr 14 20:40:47 CEST 2014",
 "uname_machine":"x86_64",
 "cpu_identifier":"Intel Core i7-4600U @ 2.10GHz",
 "cpu_frequency":-1,
 "cpu_pagesize":4096,
 "cpu_largepagesize":0,
 "cpu_numprocs":4,
 "cpu_numpackages":1,
 "cpu_coresperpackage":2,
 "cpu_logicalpercore":2,
 "cpu_numcaches":2,
 ...
 "x86_icaches":[{"type":2,"level":1,"associativity":8,"linesize":64,"sharedby":2,"totalsize":32768},
                {"type":3,"level":2,"associativity":8,"linesize":64,"sharedby":2,"totalsize":262144},
                {"type":3,"level":3,"associativity":16,"linesize":64,"sharedby":16,"totalsize":4194304}],
 "x86_dcaches":[{"type":1,"level":1,"associativity":8,"linesize":64,"sharedby":2,"totalsize":32768},
                {"type":3,"level":2,"associativity":8,"linesize":64,"sharedby":2,"totalsize":262144},
                {"type":3,"level":3,"associativity":16,"linesize":64,"sharedby":16,"totalsize":4194304}],
 "x86_tlbs":   [{"type":2,"level":1,"associativity":255,"pagesize":4194304,"entries":8},
                {"type":1,"level":1,"associativity":4,"pagesize":4096,"entries":64},
                {"type":1,"level":1,"associativity":4,"pagesize":1073741824,"entries":4},
                {"type":2,"level":1,"associativity":4,"pagesize":4096,"entries":128},
                {"type":3,"level":2,"associativity":8,"pagesize":4096,"entries":1024}],
 "timer_resolution":1e-9}
```

Maintenance Tasks
=================

This stat collection program does not update reports immediately after receiving
system information from users. Instead, the `maint_graphics.py` script regenerates
the report data. This script should be run regularly by a cron job, but note that
it is a very expensive task.

