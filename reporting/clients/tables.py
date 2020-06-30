from django_tables2.utils import A
from .models import *
import django_tables2 as tables
import itertools

attr_right_text = {"th":{"class":"text-center"}, "td":{"class":"text-right"}, "tf":{"class":"text-right"}}
class ClientsTable(tables.Table):
    ClientName = tables.LinkColumn('clients-view', verbose_name="Наименование клиента", 
        args=[A('pk')], attrs={"a": {"style": "color: #6b5eae;"}})
    TotalLoans = tables.Column(verbose_name="Всего задолженность", attrs=attr_right_text)
    class Meta:
        model = Clients
        orderable = False
        template_name = "django_tables2/bootstrap4.html"