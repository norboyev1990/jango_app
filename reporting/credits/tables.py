import django_tables2 as tables
from .models import ReportData

class ReportDataTable(tables.Table):
    class Meta:
        model = ReportData
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped #table-bordered table-head-custom"}
        orderable = False
        fields = (
            'UNIQUE_CODE',
            'BORROWER', 
            'BRANCH_NAME',
            'LOAN_BALANCE',
            )
