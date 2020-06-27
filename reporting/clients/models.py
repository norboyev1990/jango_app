from django.db import models

# Create your models here.
class Clients(models.Model):
    ClientID = models.IntegerField(primary_key=True, verbose_name="Уникалный код")
    ClientName = models.CharField(max_length=255, verbose_name="Наименование клиента")
    ClientType = models.CharField(max_length=20, verbose_name="Тип клиента")
    TotalLoans = models.DecimalField(max_digits=20, decimal_places=0, verbose_name="Всего задолженность")
    Address    = models.CharField(max_length=255, verbose_name="Адрес клиента")

    class Meta:
        managed = False 