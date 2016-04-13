from django.shortcuts import render_to_response, HttpResponse
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from models import LineHosts
import datetime


# Create your views here.
def adsl_list(request):
    queries = LineHosts.objects.filter(status='available')
    rets = ''
    if len(queries) > 0:
        for query in queries:
            if (query.last_update_time + datetime.timedelta(seconds=60 * 60)).replace(
                    tzinfo=None) > datetime.datetime.utcnow():
                str = query.line + ':ONLINE\n'
            else:
                str = query.line + ':ERROR\n'

            rets += str
    return HttpResponse(rets)


@csrf_exempt
def adsl_host_report(request):
    if request.method == 'POST':
        if request.META['HTTP_USER_AGENT'].lower() == 'dj-adsl-backend':
            ips = request.POST['ip']
            for ip in ips.split(','):
                line = LineHosts.objects.filter(host=ip)
                if line:
                    line[0].status = 'used'
                    line[0].save()
        else:
            return HttpResponseForbidden(content='not authorized')
        return HttpResponse('OK')
    else:
        adsl_ip = request.META.get('REMOTE_ADDR')
        host = request.GET['host']
        ret = LineHosts.objects.get(host=host)

        if adsl_ip != ret.adsl_ip:
            ret.adsl_ip = adsl_ip
            ret.last_update_time = datetime.datetime.now()
            ret.status = 'available'
            ret.save()

            return HttpResponse('OK')
        else:
            return HttpResponse('Need re-dail')


def adsl_status(request):
    rets = ''
    queries = LineHosts.objects.all()
    for query in queries:
        tmdelta = (datetime.datetime.utcnow() - query.last_update_time.replace(tzinfo=None)).seconds
        if query.status == 'available' and tmdelta <= 60:
            s = query.host + ' ' + query.line + ' ' + query.adsl_ip + ' last updated before ' + str(
                tmdelta) + ' seconds.'
        elif tmdelta > 60:
            s = query.host + ' ' + query.line + ' ' + query.adsl_ip + ' last updated before ' + str(
                tmdelta) + ' seconds. WARN_TTL1min'
        rets += s + '\n'

    return HttpResponse(rets)
