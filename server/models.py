# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class LineHosts(models.Model):
    line = models.CharField(max_length=20, verbose_name=u'线路名')
    host = models.CharField(max_length=6, verbose_name=u'主机名')

    def __unicode__(self):
        return unicode(self.host)

    class Meta:
        verbose_name = u'线路主机列表'
        verbose_name_plural = u'线路主机列表'


class LineStatus(models.Model):
    line = models.ForeignKey(LineHosts, verbose_name=u'线路名')
    status = models.IntegerField(choices=((0, 'available'), (1, 'using'), (2, 'used'), (3, 'dailing')),
                                 verbose_name='线路状态')
    adsl_ip = models.CharField(max_length=15, default='', verbose_name=u'adsl地址')

    last_update_time = models.DateTimeField(verbose_name='最近更新时间', auto_now_add=True)

    def __unicode__(self):
        return unicode(self.line)

    class Meta:
        verbose_name = u'线路状态'
        verbose_name_plural = u'线路状态'
