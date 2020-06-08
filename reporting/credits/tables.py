import django_tables2 as tables
from .models import ReportData

class ReportDataTable(tables.Table):
    class Meta:
        model = ReportData
        template_name = "django_tables2/bootstrap.html"
        fields = ('id', 'NAME_CLIENT', 'MFO', 'VSEGO_ZADOLJENNOST',)
