from django.contrib import admin
from models import LineStatus,LineHosts

# Register your models here.
class LineStatusAdmin(admin.ModelAdmin):
    list_display = ('line','status','last_update_time')
    search_fields = ('line','status')

class LineHostsAdmin(admin.ModelAdmin):
    list_display = ('line','host')
    search_fields = ('line','host')


admin.site.register(LineStatus,LineStatusAdmin)
admin.site.register(LineHosts,LineHostsAdmin)