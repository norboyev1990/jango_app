from django.db import models
from .queries import Query
from django.db import connection


class ListReports(models.Model):
    REPORT_TITLE = models.CharField(max_length=255)
    REPORT_MONTH = models.IntegerField()
    REPORT_YEAR = models.IntegerField()
    DATE_CREATED = models.DateTimeField(null=True)
    START_MONTH = models.DateTimeField(null=True)

    def __str__(self):
        return self.REPORT_TITLE


class ReportData(models.Model):
    REPORT = models.ForeignKey(ListReports, related_name="REPORT", on_delete=models.CASCADE, null=True)
    NUMBERS = models.IntegerField(null=True)
    CODE_REG = models.CharField(max_length=25)
    MFO = models.CharField(max_length=5)
    RAYON_PODACHI = models.CharField(max_length=255, null=True)
    NAME_CLIENT = models.CharField(max_length=255)
    BALANS_SCHET = models.CharField(max_length=20, null=True)
    CREDIT_SCHET = models.CharField(max_length=20)
    DATE_RESHENIYA = models.CharField(max_length=25)
    CODE_VAL = models.CharField(max_length=25)
    SUM_DOG_NOM = models.FloatField(null=True)
    SUM_DOG_EKV = models.FloatField(null=True)
    DATE_DOGOVOR = models.DateField(null=True)
    DATE_FACTUAL = models.DateField(null=True)
    DATE_POGASH = models.DateField(null=True)
    SROK = models.CharField(max_length=25)
    DOG_NUMBER_DATE = models.CharField(max_length=25)
    CREDIT_PROCENT = models.FloatField(null=True)
    PROSR_PROCENT = models.FloatField(null=True)
    OSTATOK_CRED_SCHET = models.FloatField(null=True)
    OSTATOK_PERESM = models.FloatField(null=True)
    DATE_PRODL = models.CharField(max_length=25)
    DATE_POGASH_POSLE_PRODL = models.DateField(null=True)
    OSTATOK_PROSR = models.FloatField(null=True)
    DATE_OBRAZ_PROS = models.DateField(null=True)
    OSTATOK_SUDEB = models.FloatField(null=True)
    DATE_SUDEB = models.DateField(null=True)
    KOD_PRAVOXR_ORG = models.CharField(max_length=255)
    PRIZNAK_RESHENIYA = models.CharField(max_length=255)
    DATE_PRED_RESH = models.CharField(max_length=45)
    VSEGO_ZADOLJENNOST = models.FloatField(null=True)
    CLASS_KACHESTVA = models.CharField(max_length=45)
    OSTATOK_REZERV = models.FloatField(null=True)
    OSTATOK_NACH_PRCNT = models.FloatField(null=True)
    OSTATOK_NACH_PROSR_PRCNT = models.FloatField(null=True)
    OCENKA_OBESPECHENIYA = models.FloatField(null=True)
    OBESPECHENIE = models.CharField(max_length=255)
    OPISANIE_OBESPECHENIE = models.CharField(max_length=255)
    ISTOCHNIK_SREDTSVO = models.CharField(max_length=255)
    ZARUBEJNIY_BANK = models.CharField(max_length=255, null=True)
    VID_KREDITOVANIYA = models.CharField(max_length=255)
    PURPOSE_CREDIT = models.CharField(max_length=255)
    VISHEST_ORG_CLIENT = models.CharField(max_length=255)
    OTRASL_KREDITOVANIYA = models.CharField(max_length=255)
    OTRASL_CLIENTA = models.CharField(max_length=255)
    CLASS_KREDIT_SPOS = models.CharField(max_length=255)
    PREDSEDATEL_KB = models.CharField(max_length=255)
    ADRESS_CLIENT = models.CharField(max_length=255)
    UN_NUMBER_CONTRACT = models.CharField(max_length=255)
    INN_PASSPORT = models.CharField(max_length=45)
    OSTATOK_VNEB_PROSR = models.FloatField(null=True)
    KONKR_NAZN_CREDIT = models.CharField(max_length=255)
    BORROWER_TYPE = models.CharField(max_length=255)
    SVYAZANNIY = models.IntegerField(null=True)
    MALIY_BIZNES = models.IntegerField(null=True)
    REGISTER_NUMBER = models.CharField(max_length=1000)
    OKED = models.CharField(max_length=255)
    CODE_CONTRACT = models.CharField(max_length=255)

    def __str__(self):
        return self.NAME_CLIENT


class TempData(models.Model):
    NUMBERS = models.CharField(max_length=255)
    CODE_REG = models.CharField(max_length=255)
    MFO = models.CharField(max_length=255)
    RAYON_PODACHI = models.CharField(max_length=255, null=True)
    NAME_CLIENT = models.CharField(max_length=255)
    BALANS_SCHET = models.CharField(max_length=255)
    CREDIT_SCHET = models.CharField(max_length=255)
    DATE_RESHENIYA = models.CharField(max_length=255)
    CODE_VAL = models.CharField(max_length=255)
    SUM_DOG_NOM = models.CharField(max_length=255)
    SUM_DOG_EKV = models.CharField(max_length=255)
    DATE_DOGOVOR = models.CharField(max_length=255)
    DATE_FACTUAL = models.CharField(max_length=255)
    DATE_POGASH = models.CharField(max_length=255)
    SROK = models.CharField(max_length=255)
    DOG_NUMBER_DATE = models.CharField(max_length=255)
    CREDIT_PROCENT = models.CharField(max_length=255)
    PROSR_PROCENT = models.CharField(max_length=255)
    OSTATOK_CRED_SCHET = models.CharField(max_length=255)
    OSTATOK_PERESM = models.CharField(max_length=255)
    DATE_PRODL = models.CharField(max_length=255)
    DATE_POGASH_POSLE_PRODL = models.CharField(max_length=255)
    OSTATOK_PROSR = models.CharField(max_length=255)
    DATE_OBRAZ_PROS = models.CharField(max_length=255)
    OSTATOK_SUDEB = models.CharField(max_length=255)
    DATE_SUDEB = models.CharField(max_length=255, null=True)
    KOD_PRAVOXR_ORG = models.CharField(max_length=255)
    PRIZNAK_RESHENIYA = models.CharField(max_length=255)
    DATE_PRED_RESH = models.CharField(max_length=255)
    VSEGO_ZADOLJENNOST = models.CharField(max_length=255)
    CLASS_KACHESTVA = models.CharField(max_length=255)
    OSTATOK_REZERV = models.CharField(max_length=255)
    OSTATOK_NACH_PRCNT = models.CharField(max_length=255)
    OSTATOK_NACH_PROSR_PRCNT = models.CharField(max_length=255)
    OCENKA_OBESPECHENIYA = models.CharField(max_length=255)
    OBESPECHENIE = models.CharField(max_length=255)
    OPISANIE_OBESPECHENIE = models.CharField(max_length=255)
    ISTOCHNIK_SREDTSVO = models.CharField(max_length=255)
    ZARUBEJNIY_BANK = models.CharField(max_length=255, null=True)
    VID_KREDITOVANIYA = models.CharField(max_length=255)
    PURPOSE_CREDIT = models.CharField(max_length=255)
    VISHEST_ORG_CLIENT = models.CharField(max_length=255)
    OTRASL_KREDITOVANIYA = models.CharField(max_length=255)
    OTRASL_CLIENTA = models.CharField(max_length=255)
    CLASS_KREDIT_SPOS = models.CharField(max_length=255)
    PREDSEDATEL_KB = models.CharField(max_length=255)
    ADRESS_CLIENT = models.CharField(max_length=255)
    UN_NUMBER_CONTRACT = models.CharField(max_length=255)
    INN_PASSPORT = models.CharField(max_length=255)
    OSTATOK_VNEB_PROSR = models.CharField(max_length=255)
    KONKR_NAZN_CREDIT = models.CharField(max_length=255)
    BORROWER_TYPE = models.CharField(max_length=255)
    SVYAZANNIY = models.CharField(max_length=255)
    MALIY_BIZNES = models.CharField(max_length=255)
    REGISTER_NUMBER = models.CharField(max_length=1000)
    OKED = models.CharField(max_length=255)
    CODE_CONTRACT = models.CharField(max_length=255)
    MONTH_CODE = models.IntegerField(null=True)

    def __str__(self):
        return self.NAME_CLIENT


class Branch(models.Model):
    CODE = models.CharField(max_length=5, db_index=True)
    NAME = models.CharField(max_length=255)
    SORT = models.IntegerField(null=True)
    GEOCODE = models.CharField(max_length=7, null=True)

    @property
    def __str__(self):
        return self.CODE + ' - ' + self.NAME


class ClientType(models.Model):
    CHOICES = (
        ('ФЛ', 'Физические лица'),
        ('ЮЛ', 'Юридические лица'),
        ('ИП', 'Индивидуалные предприятия'),
    )
    SUBJECT = models.TextChoices("Subject", 'P J')
    CODE = models.CharField(max_length=5, db_index=True)
    NAME = models.CharField(choices=CHOICES, max_length=2, default='ФЛ')
    SUBJ = models.CharField(choices=SUBJECT.choices, max_length=1, default='P')

    def __str__(self):
        return self.CODE + ' - ' + self.NAME


class Currency(models.Model):
    CODE = models.CharField(max_length=3, db_index=True)
    NAME = models.CharField(max_length=3)

    def __str__(self):
        return self.CODE + ' - ' + self.NAME


class Segment(models.Model):
    CHOICES = (
        ('Прочие', 'Прочие'),
        ('ФЛ', 'ФЛ'),
        ('Торговля', 'Торговля'),
        ('Промышленность', 'Промышленность'),
        ('Строительство', 'Строительство'),
        ('Селськое хозяйство', 'Селськое хозяйство'),
        ('ЖКХ', 'ЖКХ'),
        ('Транспорт', 'Транспорт'),
        ('Заготовки', 'Заготовки'),
    )
    CODE = models.CharField(max_length=2, db_index=True)
    NAME = models.CharField(choices=CHOICES, max_length=255)

    def __str__(self):
        return self.CODE + ' - ' + self.NAME

class OverduePercents(models.Model):
    FilialCode = models.CharField(max_length=5, null=True)
    LoanID = models.IntegerField(null=True)
    AccountCode = models.CharField(max_length=27, null=True)
    SaldoOut = models.FloatField(null=True)
    ArrearDate = models.CharField(max_length=20, null=True)
    DayCount = models.IntegerField(null=True)
    REPORT = models.ForeignKey(ListReports, related_name="REPORTDATA", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.LoanID

class NplClients(models.Model):
    Number = models.IntegerField(verbose_name="№", db_column="Numeral")
    Name = models.CharField(verbose_name="Наименование заёмщика", max_length=255)
    Branch = models.CharField(verbose_name="Филиал", max_length=255)
    Balans = models.FloatField(verbose_name="Остаток кредита")

    @staticmethod
    def table_fields():
        return ['Number', 'Name', 'Branch', 'Balans']

    @staticmethod
    def to_array(self):
        return {
            'Number': self.Number,
            'Name': self.Name,
            'Branch': self.Branch,
            'Balans': self.Balans
        }

    class Meta:
        managed = False



class ToxicCredits(models.Model):
    Number = models.IntegerField(verbose_name="№", db_column="Numeral")
    Name = models.CharField(verbose_name="Наименование клиента", max_length=255)
    Branch = models.CharField(verbose_name="Филиал", max_length=255)
    Balans = models.FloatField(verbose_name="Остаток р/с 16377")

    class Meta:
        managed = False


class OverdueCredits(models.Model):
    Number = models.IntegerField(verbose_name="№", db_column="Numeral")
    Name = models.CharField(verbose_name="Наименование клиента", max_length=255)
    Branch = models.CharField(verbose_name="Филиал", max_length=255)
    Balans = models.FloatField(verbose_name="Остаток р/с 16377")

    class Meta:
        managed = False


class InfoCredits(models.Model):
    Title = models.CharField(max_length=255, verbose_name="Показатели")
    Old_Value = models.CharField(max_length=255, verbose_name="Предыдущий  месяц")
    New_Value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Текущий месяц", )
    Updates = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Изменение")
    Percent = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Изменение, %")

    def get_old_value(self):
        return self.Old_Value if self.id not in [3, 5, 8, 10] else '{}%'.format(self.Old_Value)

    def get_new_value(self):
        return self.New_Value if self.id not in [3, 5, 8, 10] else '{}%'.format(self.New_Value)

    class Meta:
        managed = False


class ByTerms(models.Model):
    Title = models.CharField(verbose_name="Сроки", max_length=255)
    PorBalans = models.FloatField(verbose_name="Кредитный портфель")
    PorPercent = models.FloatField(verbose_name="Доля, %")
    NplBalans = models.FloatField(verbose_name="NPL")
    ToxBalans = models.FloatField(verbose_name="Токсичные кредиты")
    AmountNTK = models.FloatField(verbose_name="ТК+NPL")
    WeightNTK = models.FloatField(verbose_name="Удельный вес")
    ResBalans = models.FloatField(verbose_name="Резервы")
    ResCovers = models.FloatField(verbose_name="Покрытие резервами")

    class Meta:
        managed = False


class ByRetailProduct(models.Model):
    Numeral = models.IntegerField(verbose_name="№", primary_key=True)
    Title = models.CharField(verbose_name="Продукт", max_length=255)
    PorBalans = models.FloatField(verbose_name="Кредитный портфель")
    PorPercent = models.FloatField(verbose_name="Доля, %")
    PrsBalans = models.FloatField(verbose_name="Просрочка ОД")
    NplBalans = models.FloatField(verbose_name="NPL")
    NplWeight = models.FloatField(verbose_name="Удельный вес")
    NachBalans = models.FloatField(verbose_name="Просрочка по % (16377)")

    class Meta:
        managed = False


class ByPercentage(models.Model):
    Numeral = models.IntegerField(verbose_name="№", primary_key=True)
    Title = models.CharField(verbose_name="Коридор", max_length=255)
    ULLongTerm = models.FloatField(verbose_name="Долгосрочные ЮЛ")
    ULLongPart = models.FloatField(verbose_name="Доля, %")
    ULShortTerm = models.FloatField(verbose_name="Краткосрочные ЮЛ")
    ULShortPart = models.FloatField(verbose_name="Доля, %")
    FLLongTerm = models.FloatField(verbose_name="Долгосрочные ФЛ")
    FLLongPart = models.FloatField(verbose_name="Доля, %")
    FLShortTerm = models.FloatField(verbose_name="Краткосрочные ФЛ")
    FLShortPart = models.FloatField(verbose_name="Доля, %")

    class Meta:
        managed = False


class ByPercentageUL(models.Model):
    Numeral = models.IntegerField(verbose_name="№", primary_key=True)
    Title = models.CharField(verbose_name="Коридор", max_length=255)
    TermLess2 = models.FloatField(verbose_name="до 2-х лет")
    PartLess2 = models.FloatField(verbose_name="Доля, %")
    TermLess5 = models.FloatField(verbose_name="от 2-х до 5 лет")
    PartLess5 = models.FloatField(verbose_name="Доля, %")
    TermLess7 = models.FloatField(verbose_name="от 5-ти до 7 лет")
    PartLess7 = models.FloatField(verbose_name="Доля, %")
    TermLess10 = models.FloatField(verbose_name="от 7-ми до 10 лет")
    PartLess10 = models.FloatField(verbose_name="Доля, %")
    TermMore10 = models.FloatField(verbose_name="свыше 10 лет")
    PartMore10 = models.FloatField(verbose_name="Доля, %")

    class Meta:
        managed = False

class ByAverageUl(models.Model):
    Title = models.CharField(verbose_name="Срок", max_length=255)
    AverageUZS = models.FloatField(verbose_name="UZS")
    AverageUSD = models.FloatField(verbose_name="USD")
    AverageEUR = models.FloatField(verbose_name="EUR")
    AverageJPY = models.FloatField(verbose_name="JPY")
    TotalUZS = models.FloatField()
    TotalUSD = models.FloatField()
    TotalEUR = models.FloatField()
    TotalJPY = models.FloatField()

    class Meta:
        managed = False

class ByAverageFl(models.Model):
    Title = models.CharField(verbose_name="Продукты", max_length=255)
    Balance = models.FloatField(verbose_name="UZS")
    Average = models.FloatField()

class ByOverdueBranch(models.Model):
    Title = models.CharField(verbose_name="Филиал", max_length=255)
    Balance = models.FloatField(verbose_name="Выданные")
    Overdue = models.FloatField(verbose_name="Просрочка")
    CountPr = models.FloatField(verbose_name="Количество")

    class Meta:
        managed = False

class DataByGeocode(models.Model):
    Title = models.CharField(max_length=255)
    GeoCode = models.CharField(max_length=7, primary_key=True)
    Balance = models.FloatField()
