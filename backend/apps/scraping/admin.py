from django.contrib import admin

from .models import AutomateLog, ScrapeRun

admin.site.register(AutomateLog)
admin.site.register(ScrapeRun)
