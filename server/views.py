from django.shortcuts import HttpResponse, redirect
from django.http import HttpResponseForbidden,HttpResponseNotFound,HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from models import LineHosts
import datetime

TM_DELTA = 60*60

# Create your views here.
def index(request):
    return redirect(reverse('adsl_list'))


def adsl_list(request):
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
    if request.method == 'POST':
        if 'ip' in request.POST:
            if request.META['HTTP_USER_AGENT'].lower() == 'dj-adsl-backend':
                ips = request.POST['ip']
                for ip in ips.split(','):
                    line = LineHosts.objects.filter(host=ip)
                    if line:
                        line[0].status = 'used'
                        line[0].save()
                return HttpResponse('OK')
            else:
                return HttpResponseForbidden(content='not authorized')

        elif 'host' in request.POST:
            adsl_ip = request.META.get('REMOTE_ADDR')
            host = request.POST['host']
            ret = LineHosts.objects.filter(host=host)
            if len(ret) > 0:
                if adsl_ip != ret[0].adsl_ip:
                    ret[0].adsl_ip = adsl_ip
                    ret[0].last_update_time = datetime.datetime.now()
                    ret[0].status = 'available'
                    ret[0].save()

                    return HttpResponse('OK')
                else:
                    return HttpResponse(content='Need re-dail')
            else:
                line = '100.100.100.100:8' + host.replace('seo', '')
                record = LineHosts(host=host, line=line, adsl_ip=adsl_ip, status='available')
                record.save()
                return HttpResponse('add new line, host:' + host + ' line:' + line)
        else:
            return HttpResponseBadRequest(content='parameters error')
    else:
        return HttpResponseBadRequest()


def adsl_status(request):
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
                    rets += s + '\n'

                return HttpResponse(rets)
            else:
                host = request.GET['show']
                queries = LineHosts.objects.filter(host=host)
                if queries:
                    return HttpResponse(queries[0].status)
                else:
                    return HttpResponseNotFound()
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