from django.shortcuts import HttpResponse, redirect
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from models import LineHosts

import datetime
import logging

TM_DELTA = 60
LB_IP = '183.61.70.113'
logger = logging.getLogger('access')


# Create your views here.
def getclientip(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        clientip = request.META.get('HTTP_X_FORWARDED_FOR')
    else:
        clientip = request.META.get('REMOTE_ADDR')

    return clientip


def index(request):
    ip = getclientip(request)
    logger.debug(ip + ' ' + request.method + ' ' + request.get_full_path())

    return redirect(reverse('adsl_list'))


def adsl_list(request):
    ip = getclientip(request)
    logger.info(ip + ' ' + request.method + ' ' + request.get_full_path())

    queries = LineHosts.objects.filter(status='available')
    rets = ''
    if len(queries) > 0:
        for query in queries:
            if (query.last_update_time + datetime.timedelta(seconds=TM_DELTA)).replace(
                    tzinfo=None) > datetime.datetime.utcnow():
                str = query.host + ' ' + query.line + ' ONLINE\n'
            else:
                str = query.host + ' ' + query.line + ' ERROR\n'

            rets += str
    return HttpResponse(rets)


@csrf_exempt
def adsl_host_report(request):
    ip = getclientip(request)
    logger.info(ip + ' ' + request.method + ' ' + request.get_full_path() + ' ' + str(request.POST))

    if request.method == 'POST' and request.META['HTTP_USER_AGENT'].lower() == 'dj-adsl-backend':
        if 'ip' in request.POST:
            ips = request.POST['ip']
            for ip in ips.split(','):
                line = LineHosts.objects.filter(host=ip)
                if line:
                    line[0].status = 'used'
                    line[0].save()
            return HttpResponse('OK')

        elif 'host' in request.POST:
            host = request.POST['host']
            ret = LineHosts.objects.filter(host=host)
            if len(ret) > 0:
                ret[0].adsl_ip = ip
                ret[0].last_update_time = datetime.datetime.now()
                ret[0].status = 'available'
                ret[0].save()

                return HttpResponse('OK')
            else:
                n = '8' + host.replace('seo', '')
                line = LB_IP + ':' + n
                record = LineHosts(host=host, line=line, adsl_ip=ip, status='available')
                record.save()
                return HttpResponse('add new line, host:' + host + ' line:' + line)
        else:
            return HttpResponseBadRequest(content='parameters error')
    else:
        return HttpResponseBadRequest()


def adsl_status(request):
    ip = getclientip(request)
    logger.info(ip + ' ' + request.method + ' ' + request.get_full_path())

    if request.method == 'GET':
        if 'show' in request.GET:
            if request.GET['show'] == 'all':
                rets = ''
                queries = LineHosts.objects.all()
                for query in queries:
                    tmdelta = (datetime.datetime.utcnow() - query.last_update_time.replace(tzinfo=None)).seconds
                    if query.status == 'available' and tmdelta <= TM_DELTA:
                        s = query.host + ' ' + query.line + ' ' + query.adsl_ip + ' ' + query.status + ' ' + ' last updated before ' + str(
                            tmdelta) + ' seconds.'
                    elif tmdelta > TM_DELTA:
                        s = query.host + ' ' + query.line + ' ' + query.adsl_ip + ' ' + query.status + ' ' + ' last updated before ' + str(
                            tmdelta) + ' seconds. WARN_TTL1min'
                    else:
                        s = query.host + ' ' + query.line + ' ' + query.adsl_ip + ' ' + query.status + ' ' + ' last updated before ' + str(
                            tmdelta) + ' seconds. WARN_status'
                    rets += s + '\n'

                return HttpResponse(rets)
            else:
                host = request.GET['show']
                queries = LineHosts.objects.filter(host=host)
                if len(queries) > 0:
                    return HttpResponse(queries[0].status)
                else:
                    return HttpResponse('404')
        else:
            rets = ''
            queries = LineHosts.objects.all()
            for query in queries:
                tmdelta = (datetime.datetime.utcnow() - query.last_update_time.replace(tzinfo=None)).seconds
                if query.status == 'available' and tmdelta <= TM_DELTA:
                    s = query.host + ' ' + query.line + ' ' + query.adsl_ip + ' ' + query.status + ' ' + ' last updated before ' + str(
                        tmdelta) + ' seconds.'

                    rets += s + '\n'

            return HttpResponse(rets)
    else:
        return HttpResponseBadRequest()
