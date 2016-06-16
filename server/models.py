# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class LineHosts(models.Model):
    line = models.CharField(max_length=20, verbose_name=u'线路', default='')
    host = models.CharField(max_length=6, verbose_name=u'主机', default='')
    status = models.CharField(max_length=20, verbose_name='线路状态', default='')
    adsl_ip = models.CharField(max_length=15, verbose_name=u'adsl地址', default='')
    gid = models.IntegerField(verbose_name=u'分组', default='1')

    last_update_time = models.DateTimeField(verbose_name='最近更新时间', auto_now_add=True)

    def __unicode__(self):
        return unicode(self.host)

    class Meta:
        verbose_name = u'线路主机列表'
        verbose_name_plural = u'线路主机列表'
