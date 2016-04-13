from django.shortcuts import render_to_response,HttpResponse
from models import LineHosts,LineStatus
from django.utils.timezone import localtime
import datetime


# Create your views here.
def adsl_list(request):
    queries = LineStatus.objects.filter(status=0)

    rets = ''
    if len(queries) > 0:
        for query in queries:
            print query.line.line,query.last_update_time
            print query.line.line,localtime(query.last_update_time)

            print datetime.datetime.now()
            if query.last_update_time + datetime.timedelta(seconds=9000) > datetime.datetime.now():
                str = query.line.line + ':ONLINE\n'
            else:
                str = query.line.line + ':ERROR\n'

            rets += str
    return HttpResponse(rets)

