from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.ListReports)
admin.site.register(models.ReportData)
admin.site.register(models.Branch)
admin.site.register(models.ClientType)
admin.site.register(models.Currency)
admin.site.register(models.Segment)