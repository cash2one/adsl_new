from django.contrib import admin
from models import LineHosts


# Register your models here.
class LineHostsAdmin(admin.ModelAdmin):
    list_display = ('line', 'host', 'status', 'last_update_time')
    search_fields = ('line', 'host', 'status')


admin.site.register(LineHosts, LineHostsAdmin)
