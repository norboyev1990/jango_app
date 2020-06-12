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
class OverallInfoTable(tables.Table):
    name        = tables.Column()
    old_value   = tables.Column(attrs={"th":{"class":"text-right"}, "td":{"class":"text-right"}})
    new_value   = tables.Column(attrs={"th":{"class":"text-right"}, "td":{"class":"text-right"}})
    difference  = tables.Column(attrs={"th":{"class":"text-right"}, "td":{"class":"text-right"}})
    percentage  = tables.Column(attrs={"th":{"class":"text-right"}, "td":{"class":"text-right"}})


    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped #table-bordered table-head-custom  table-overall"}
        orderable = False