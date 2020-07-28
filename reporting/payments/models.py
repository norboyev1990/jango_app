from django.db import models

# Create your models here.
class TypeClients(models.Model):
    Code = models.CharField(max_length=3, db_index=True)
    Name = models.CharField(max_length=255)

class PeriodList1(models.Model):
    Code = models.IntegerField(db_index=True)
    Name = models.CharField(max_length=25)
    MinD = models.IntegerField()
    MaxD = models.IntegerField()

class PeriodList2(models.Model):
    Code = models.IntegerField(db_index=True)
    Name = models.CharField(max_length=25)
    MinD = models.IntegerField()
    MaxD = models.IntegerField()
