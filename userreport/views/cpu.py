from userreport.models import UserReport_hwdetect
import userreport.x86 as x86
from userreport.util import hashabledict

from django.shortcuts import render_to_response
from django.template import RequestContext


def ReportCpu(request):
    reports = UserReport_hwdetect.objects
    reports = reports.filter(data_type = 'hwdetect', data_version__gte = 4)

    all_users = set()
    cpus = {}

    for report in reports:
        json = report.data_json_nocache()
        if json is None:
            continue

        cpu = {}
        for x in (
            'x86_vendor', 'x86_model', 'x86_family',
            'cpu_identifier', 'cpu_frequency',
            'cpu_numprocs', 'cpu_numpackages', 'cpu_coresperpackage',
            'cpu_logicalpercore',
            'cpu_numcaches', 'cpu_pagesize', 'cpu_largepagesize',
            'numa_numnodes', 'numa_factor', 'numa_interleaved',
        ):
            cpu[x] = json[x]

        cpu['os'] = report.os()

        def fmt_size(s):
            if s % (1024*1024) == 0:
                return "%d MB" % (s / (1024*1024))
            if s % 1024 == 0:
                return "%d kB" % (s / 1024)
            return "%d B" % s

        def fmt_assoc(w):
            if w == 255:
                return 'fully-assoc'
            else:
                return '%d-way' % w

        def fmt_cache(c, t):
            types = ('?', 'D', 'I ', 'U')
            if c['type'] == 0:
                return "(Unknown %s cache)" % t
            return "L%d %s: %s (%s, shared %dx%s)" % (
                c['level'], types[c['type']], fmt_size(c['totalsize']),
                fmt_assoc(c['associativity']), c['sharedby'],
                    ('' if c['linesize'] == 64 else ', %dB line' % c['linesize'])
            )

        def fmt_tlb(c, t):
            types = ('?', 'D', 'I ', 'U')
            if c['type'] == 0:
                return "(Unknown %s TLB)" % t
            return "L%d %s: %d-entry (%s, %s page)" % (
                c['level'], types[c['type']], c['entries'],
                fmt_assoc(c['associativity']), fmt_size(c['pagesize'])
            )

        def fmt_caches(d, i, cb):
            dcaches = d[:]
            icaches = i[:]
            caches = []
            while len(dcaches) or len(icaches):
                if len(dcaches) and len(icaches) and dcaches[0] == icaches[0] and dcaches[0]['type'] == 3:
                    caches.append(cb(dcaches[0], 'U'))
                    dcaches.pop(0)
                    icaches.pop(0)
                else:
                    if len(dcaches):
                        caches.append(cb(dcaches[0], 'D'))
                        dcaches.pop(0)
                    if len(icaches):
                        caches.append(cb(icaches[0], 'I'))
                        icaches.pop(0)
            return tuple(caches)

        try:
            cpu['caches'] = fmt_caches(json['x86_dcaches'], json['x86_icaches'], fmt_cache)
            cpu['tlbs'] = fmt_caches(json['x86_tlbs'], json['x86_tlbs'], fmt_tlb)
        except TypeError:
            continue # skip on bogus cache data

        caps = set()
        for (n,_,b) in x86.cap_bits:
            if n.endswith('[2]'):
                continue
            if json['x86_caps[%d]' % (b / 32)] & (1 << (b % 32)):
                caps.add(n)
        cpu['caps'] = frozenset(caps)

        all_users.add(report.user_id_hash)
        cpus.setdefault(hashabledict(cpu), set()).add(report.user_id_hash)

    return render_to_response('reports/cpu.html',
                              {'cpus': cpus, 'x86_cap_descs': x86.cap_descs},
                              context_instance=RequestContext(request))
