from django.contrib import admin
from models import LineHosts


# Register your models here.
class LineHostsAdmin(admin.ModelAdmin):
    list_display = ('line', 'host', 'adsl_ip', 'status', 'last_update_time', 'gid')
    search_fields = ('line', 'host', 'adsl_ip', 'status', 'gid')


admin.site.register(LineHosts, LineHostsAdmin)
