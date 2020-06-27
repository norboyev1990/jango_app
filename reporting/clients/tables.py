import django_tables2 as tables
from .models import *
import itertools

attr_right_text = {"th":{"class":"text-center"}, "td":{"class":"text-right"}, "tf":{"class":"text-right"}}
class ClientsTable(tables.Table):
    TotalLoans = tables.Column(verbose_name="Всего задолженность", attrs=attr_right_text)
    class Meta:
        model = Clients
        orderable = False
        template_name = "django_tables2/bootstrap4.html"