from django.db import models

# Create your models here.
class ListReports(models.Model):
    REPORT_TITLE = models.CharField(max_length=255)
    REPORT_MONTH = models.IntegerField()
    REPORT_YEAR  = models.IntegerField()
    DATE_CREATED = models.DateTimeField(null=True)
    START_MONTH  = models.DateTimeField(null=True)

    def __str__(self):
        return self.REPORT_TITLE

class ReportData(models.Model):
    REPORT = models.ForeignKey(ListReports, related_name="REPORT", on_delete=models.CASCADE, null=True)
    NUMBER                  = models.IntegerField(null=True)
    CODE_REG                = models.CharField(max_length=25)
    MFO                     = models.CharField(max_length=5)
    NAME_CLIENT             = models.CharField(max_length=255)
    BALANS_SCHET            = models.CharField(max_length=20, null=True)
    CREDIT_SCHET            = models.CharField(max_length=20)
    DATE_RESHENIYA          = models.CharField(max_length=25)
    CODE_VAL                = models.CharField(max_length=25)
    SUM_DOG_NOM             = models.FloatField(null=True)
    SUM_DOG_EKV             = models.FloatField(null=True)
    DATE_DOGOVOR            = models.DateField(null=True)
    DATE_FACTUAL            = models.DateField(null=True)
    DATE_POGASH             = models.DateField(null=True)
    SROK                    = models.CharField(max_length=25)
    DOG_NUMBER_DATE         = models.CharField(max_length=25)
    CREDIT_PROCENT          = models.IntegerField(null=True)
    PROSR_PROCENT           = models.IntegerField(null=True)
    OSTATOK_CRED_SCHET      = models.FloatField(null=True)
    OSTATOK_PERESM          = models.FloatField(null=True)
    DATE_PRODL              = models.CharField(max_length=25)
    DATE_POGASH_POSLE_PRODL = models.DateField(null=True)
    OSTATOK_PROSR           = models.FloatField(null=True)
    DATE_OBRAZ_PROS         = models.DateField(null=True)
    OSTATOK_SUDEB           = models.FloatField(null=True)
    KOD_PRAVOXR_ORG         = models.CharField(max_length=255)
    PRIZNAK_RESHENIYA       = models.CharField(max_length=255)
    DATE_PRED_RESH          = models.CharField(max_length=25)
    VSEGO_ZADOLJENNOST      = models.FloatField(null=True)
    CLASS_KACHESTVA         = models.CharField(max_length=25)
    OSTATOK_REZERV          = models.FloatField(null=True)
    OSTATOK_NACH_PRCNT      = models.FloatField(null=True)
    OSTATOK_NACH_PROSR_PRCNT= models.FloatField(null=True)
    OCENKA_OBESPECHENIYA    = models.FloatField(null=True)
    OBESPECHENIE            = models.CharField(max_length=255)
    OPISANIE_OBESPECHENIE   = models.CharField(max_length=255)
    ISTOCHNIK_SREDTSVO      = models.CharField(max_length=255)
    VID_KREDITOVANIYA       = models.CharField(max_length=255)
    PURPOSE_CREDIT          = models.CharField(max_length=255)
    VISHEST_ORG_CLIENT      = models.CharField(max_length=255)
    OTRASL_KREDITOVANIYA    = models.CharField(max_length=255)
    OTRASL_CLIENTA          = models.CharField(max_length=255)
    CLASS_KREDIT_SPOS       = models.CharField(max_length=255)
    PREDSEDATEL_KB          = models.CharField(max_length=255)
    ADRESS_CLIENT           = models.CharField(max_length=255)
    UN_NUMBER_CONTRACT      = models.CharField(max_length=255)
    INN_PASSPORT            = models.CharField(max_length=25)
    OSTATOK_VNEB_PROSR      = models.FloatField(null=True)
    KONKR_NAZN_CREDIT       = models.CharField(max_length=255)
    BORROWER_TYPE           = models.CharField(max_length=255)
    SVYAZANNIY              = models.IntegerField(null=True)
    MALIY_BIZNES            = models.IntegerField(null=True)
    REGISTER_NUMBER         = models.CharField(max_length=255)
    OKED                    = models.CharField(max_length=255)
    CODE_CONTRACT           = models.CharField(max_length=255)
    def __str__(self):
        return self.NAME_CLIENT

class Branch(models.Model):
    CODE = models.CharField(max_length=5)
    NAME = models.CharField(max_length=255)
    SORT = models.IntegerField(null=True)
    def __str__(self):
        return self.CODE + ' - ' + self.NAME

class ClientType(models.Model):
    CHOICES = (
       ('ФЛ', ('Физические лица')),
       ('ЮЛ', ('Юридические лица')),
       ('ИП', ('Индивидуалные предприятия')),
    )
    SUBJECT = models.TextChoices('Subject', 'P J')
    CODE = models.CharField(max_length=5)
    NAME = models.CharField(choices=CHOICES, max_length=2, default='ФЛ')
    SUBJ = models.CharField(choices=SUBJECT.choices, max_length=1, default='P')
    def __str__(self):
        return self.CODE + ' - ' + self.NAME

class Currency(models.Model):
    CODE = models.CharField(max_length=3)
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
    CODE = models.CharField(max_length=2)
    NAME = models.CharField(choices=CHOICES, max_length=255)
    def __str__(self):
        return self.CODE + ' - ' + self.NAME

class NplClients(models.Model):
    Number = models.IntegerField(verbose_name="№")
    Name   = models.CharField(max_length=255, verbose_name="Наименование заёмщика")
    Branch = models.CharField(max_length=255, verbose_name="Филиал")
    Balans = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Остаток кредита")
    class Meta:
        managed  = False

class ToxicCredits(models.Model):
    Number = models.IntegerField(verbose_name="№")
    Name   = models.CharField(max_length=255, verbose_name="Наименование клиента")
    Branch = models.CharField(max_length=255, verbose_name="Филиал")
    Balans = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Остаток р/с 16377")
    class Meta:
        managed  = False

class OverdueCredits(models.Model):
    Number = models.IntegerField(verbose_name="№")
    Name   = models.CharField(max_length=255, verbose_name="Наименование клиента")
    Branch = models.CharField(max_length=255, verbose_name="Филиал")
    Balans = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Остаток р/с 16377")
    class Meta:
        managed  = False

class ByTerms(models.Model):
    Title     = models.CharField(max_length=255, verbose_name="Сроки")
    PorBalans = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Кредитный портфель")
    PorPercent= models.DecimalField(max_digits=12, decimal_places=1, verbose_name="Доля")
    NplBalans = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="NPL")
    ToxBalans = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Токсичные кредиты")
    ResBalans = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Резервы")

    def amount_npl_toxic(self):
        return self.NplBalans + self.ToxBalans

    def weight_npl_toxic(self):
        return '{:.1%}'.format((self.NplBalans+self.ToxBalans)/self.PorBalans)

    def reserve_cover(self):
        return '{:.1%}'.format(self.ResBalans/(self.NplBalans+self.ToxBalans))


    class Meta:
        managed  = False

class ByPercentage(models.Model):
    Number    = models.CharField(max_length=255, verbose_name="№")
    Title     = models.CharField(max_length=255, verbose_name="Коридор")
    ULLongTerm = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Долгосрочные ЮЛ")
    ULLongPart = models.DecimalField(max_digits=12, decimal_places=1, verbose_name="Доля, %")
    ULShortTerm = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Краткосрочные ЮЛ")
    ULShortPart = models.DecimalField(max_digits=12, decimal_places=1, verbose_name="Доля, %")
    FLLongTerm = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Долгосрочные ФЛ")
    FLLongPart = models.DecimalField(max_digits=12, decimal_places=1, verbose_name="Доля, %")
    FLShortTerm = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Краткосрочные ФЛ")
    FLShortPart = models.DecimalField(max_digits=12, decimal_places=1, verbose_name="Доля, %")

    class Meta:
        managed  = False

class ByPercentageUL(models.Model):
    Number  = models.CharField(max_length=255, verbose_name="№")
    Title   = models.CharField(max_length=255, verbose_name="Коридор")
    Term1   = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="до 2-х лет")
    Term2   = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="от 2-х до 5 лет")
    Term3   = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="от 5-ти до 7 лет")
    Term4   = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="от 7-ми до 10 лет")
    Term5   = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="свыше 10 лет")
    

    class Meta:
        managed  = False

class ByRetailProduct(models.Model):
    Number      = models.CharField(max_length=255, verbose_name="№")
    Title       = models.CharField(max_length=255, verbose_name="Продукт")
    PorBalans   = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Кредитный портфель")
    PorPercent  = models.DecimalField(max_digits=12, decimal_places=1, verbose_name="Доля, %")
    PrsBalans   = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Просрочка ОД")
    NplBalans   = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="NPL")
    NplWeight   = models.DecimalField(max_digits=12, decimal_places=1, verbose_name="Удельный вес")
    NachBalans  = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Просрочка по % (16377)")

    class Meta:
        managed  = False