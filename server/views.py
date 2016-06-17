from django.shortcuts import HttpResponse, redirect
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from models import LineHosts
from logging.handlers import TimedRotatingFileHandler
import datetime, os, logging

TM_DELTA = 60
LB_IP = '183.61.80.68'


# Create your views here.
def getlogger(logfile='./log'):
    log_path = os.path.dirname(logfile)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = TimedRotatingFileHandler(logfile, 'd')
    formatter = logging.Formatter('[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def index(request):
    return redirect(reverse('adsl_list'))


def adsl_list(request):
    rets = ''

    if 'gid' in request.GET:
        gid = int(request.GET['gid'])
        queries = LineHosts.objects.filter(status='available', gid=gid)
    else:
        queries = LineHosts.objects.filter(status='available')

    if len(queries) > 0:
        for query in queries:
            if (query.last_update_time + datetime.timedelta(seconds=TM_DELTA)).replace(tzinfo=None) > datetime.datetime.utcnow():
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
                        return HttpResponseNotFound(content='no host')
            else:
                return HttpResponseForbidden(content='not authorized')

        elif 'host' in request.POST:
            if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                adsl_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            else:
                adsl_ip = request.META.get('REMOTE_ADDR')
            host = request.POST['host']
            ret = LineHosts.objects.filter(host=host)
            if len(ret) > 0:
                ret[0].adsl_ip = adsl_ip
                ret[0].last_update_time = datetime.datetime.now()
                ret[0].status = 'available'
                ret[0].save()

                return HttpResponse('OK')
            else:
                n = '8' + host.replace('seo', '')
                line = LB_IP + ':' + n
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
                tmdelta = (datetime.datetime.utcnow() - query.last_update_time).seconds
                if query.status == 'available' and tmdelta <= TM_DELTA:
                    s = query.host + ' ' + query.line + ' ' + query.adsl_ip + ' ' + query.status + ' ' + ' last updated before ' + str(
                        tmdelta) + ' seconds.'

                    rets += s + '\n'

            return HttpResponse(rets)
    else:
        return HttpResponseBadRequest()
