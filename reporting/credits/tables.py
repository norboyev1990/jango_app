import django_tables2 as tables
from .models import *
import itertools

attr_right_text = {"th":{"class":"text-center"}, "td":{"class":"text-center"}, "tf":{"class":"text-center"}}

class NplClientsTable(tables.Table):
    Balans = tables.Column(verbose_name="Остаток кредита", attrs=attr_right_text)
    class Meta:
        model = NplClients
        orderable = False
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-centered table-hover mb-0", "thead": {"class": "thead-dark"}}
        exclude = ('id',)

class ToxicCreditsTable(tables.Table):
    Balans = tables.Column(verbose_name="Остаток р/с 16377", attrs=attr_right_text)
    class Meta:
        model = ToxicCredits
        orderable = False
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-centered table-hover mb-0", "thead": {"class": "thead-dark"}}
        exclude = ('id',)

class OverdueCreditsTable(tables.Table):
    Balans = tables.Column(verbose_name="Остаток р/с 16377", attrs=attr_right_text)
    class Meta:
        model = OverdueCredits
        orderable = False
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-centered table-hover mb-0", "thead": {"class": "thead-dark"}}
        exclude = ('id',)
        
        

class ReportDataTable(tables.Table):
    class Meta:
        model = ReportData
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-centered mb-0", "thead": {"class": "thead-light"}}
        orderable = False
        fields = (
            'UNIQUE_CODE',
            'BORROWER', 
            'BRANCH_NAME',
            'LOAN_BALANCE',
            )
class OverallInfoTable(tables.Table):
    name        = tables.Column(verbose_name="Показатели")
    old_value   = tables.Column(attrs=attr_right_text, verbose_name="Предыдущий  месяц")
    new_value   = tables.Column(attrs=attr_right_text, verbose_name="Текущий месяц")
    difference  = tables.Column(attrs=attr_right_text, verbose_name="Изменение")
    percentage  = tables.Column(attrs=attr_right_text, verbose_name="Изменение, %")

    
    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-centered mb-0", "thead": {"class": "thead-dark"}}
        orderable = False

class ByTermsTable(tables.Table):
    Title = tables.Column(
        attrs={"td":{"class":"text-truncate"}},
        verbose_name="Сроки",
        footer="Итого:")
    PorBalans = tables.Column(
        attrs=attr_right_text,
        verbose_name="Кредитный портфель",
        footer=lambda table: sum(x.PorBalans for x in table.data)
    )
    PorPercent = tables.Column(
        attrs=attr_right_text,
        verbose_name="Доля, %",
        footer="100%"
    )
    NplBalans = tables.Column(
        attrs=attr_right_text,
        verbose_name="NPL",
        footer=lambda table: sum(x.NplBalans for x in table.data)
    )
    ToxBalans = tables.Column(
        attrs=attr_right_text,
        verbose_name="Токсичные кредиты",
        footer=lambda table: sum(x.ToxBalans for x in table.data)
    )
    NplToxic = tables.Column(
        accessor='amount_npl_toxic',
        attrs=attr_right_text,
        verbose_name="ТК + NPL",
        footer=lambda table: sum(x.NplBalans+x.ToxBalans for x in table.data)
    )
    TKNWeight = tables.Column(
        accessor='weight_npl_toxic',
        attrs=attr_right_text,
        verbose_name="Удельный вес",
        footer=lambda table: '{:.1%}'.format(sum(x.NplBalans+x.ToxBalans for x in table.data)/sum(x.PorBalans for x in table.data)))
    ResBalans = tables.Column(
        attrs=attr_right_text,
        verbose_name="Резервы",
        footer=lambda table: sum(x.ResBalans for x in table.data)
    )
    ResCover = tables.Column(
        accessor='reserve_cover',
        attrs=attr_right_text,
        verbose_name="Покрытие резервами",
        footer=lambda table: '{:.1%}'.format(sum(x.ResBalans for x in table.data)/sum(x.NplBalans+x.ToxBalans for x in table.data))
    )
    class Meta:
        model = ByTerms
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-centered mb-0", "thead": {"class": "thead-dark text-truncate"}, "tfoot": {"class": "bg-light"}}
        sequence = ('Title', 'PorBalans', 'PorPercent', 'NplBalans', 'ToxBalans', 'NplToxic', 'TKNWeight', 'ResBalans')
        orderable = False
        exclude = ('id',)

class BySubjectTable(tables.Table):
    attr={"th":{"class":"text-right"}, "td":{"class":"text-right"}}
    TITLE       = tables.Column(verbose_name="Статус", footer="Итого:")
    LOAN        = tables.Column(attrs=attr, verbose_name="Кредитный портфель")
    RATION      = tables.Column(attrs=attr, verbose_name="Доля %")
    NPL_LOAN    = tables.Column(attrs=attr, verbose_name="NPL")
    TOX_LOAN    = tables.Column(attrs=attr, verbose_name="Токсичные кредиты")
    TOX_NPL     = tables.Column(attrs=attr, verbose_name="ТК+NPL")
    WEIGHT      = tables.Column(attrs=attr, verbose_name="удельный вес")
    RESERVE     = tables.Column(attrs=attr, verbose_name="Резервы")
    COATING     = tables.Column(attrs=attr, verbose_name="Покрытие резервами")

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-centered mb-0", "thead": {"class": "thead-dark text-truncate"}, "tfoot": {"class": "bg-light"}}
        orderable = False

class ByPercentageTable(tables.Table):
    attr={"th":{"class":"text-right"}, "td":{"class":"text-right"}}
    TITLE       = tables.Column(verbose_name = "Коридор")
    ULL_LOAN    = tables.Column(attrs=attr, verbose_name = "Долгосрочные ЮЛ")
    ULL_PERCENT = tables.Column(attrs=attr, verbose_name = "Доля %")
    ULS_LOAN    = tables.Column(attrs=attr, verbose_name = "Краткосрочные ЮЛ")
    ULS_PERCENT = tables.Column(attrs=attr, verbose_name = "Доля %")
    FLL_LOAN    = tables.Column(attrs=attr, verbose_name = "Долгосрочные ФЛ")
    FLL_PERCENT = tables.Column(attrs=attr, verbose_name = "Доля %")
    FLS_LOAN    = tables.Column(attrs=attr, verbose_name = "Краткосрочные ФЛ")
    FLS_PERCENT = tables.Column(attrs=attr, verbose_name = "Доля %")
    
    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped #table-bordered table-head-custom  table-overall"}
        orderable = False

class ByPercentageULTable(tables.Table):
    attr={"th":{"class":"text-right"}, "td":{"class":"text-right"}}
    TITLE       = tables.Column(verbose_name = "Коридор")
    T2_LOAN    = tables.Column(attrs=attr, verbose_name = "до 2-х лет")
    T2_PERCENT    = tables.Column(attrs=attr, verbose_name = "Доля %")
    T5_LOAN    = tables.Column(attrs=attr, verbose_name = "от 2-х до 5 лет")
    T5_PERCENT    = tables.Column(attrs=attr, verbose_name = "Доля %")
    T7_LOAN    = tables.Column(attrs=attr, verbose_name = "от 5-ти до 7 лет")
    T7_PERCENT    = tables.Column(attrs=attr, verbose_name = "Доля %")
    T10_LOAN    = tables.Column(attrs=attr, verbose_name = "от 7-ми до 10 лет")
    T10_PERCENT    = tables.Column(attrs=attr, verbose_name = "Доля %")
    T11_LOAN    = tables.Column(attrs=attr, verbose_name = "свыше 10 лет")
    T11_PERCENT    = tables.Column(attrs=attr, verbose_name = "Доля %")
    
    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped #table-bordered table-head-custom  table-overall"}
        orderable = False

class ByAverageULTable(tables.Table):
    attr={"th":{"class":"text-right"}, "td":{"class":"text-right"}}
    TITLE       = tables.Column(verbose_name = "Срок")
    UZS_AVERAGE    = tables.Column(attrs=attr, verbose_name = "UZS")
    USD_AVERAGE    = tables.Column(attrs=attr, verbose_name = "USD")
    EUR_AVERAGE    = tables.Column(attrs=attr, verbose_name = "EUR")
    JPY_AVERAGE    = tables.Column(attrs=attr, verbose_name = "JPY")
    
    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped #table-bordered table-head-custom  table-overall"}
        orderable = False

class ByAverageFLTable(tables.Table):
    TITLE       = tables.Column()
    BALANS    = tables.Column(attrs={"th":{"class":"text-right"}, "td":{"class":"text-right"}})
    
    class Meta:
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-striped #table-bordered table-head-custom  table-overall"}
        orderable = False

class ContractListTable(tables.Table):
    class Meta:
        model = ReportData
        template_name = "django_tables2/bootstrap.html"
        attrs = {"class": "table table-centered mb-0", "thead": {"class": "thead-light"}}
        orderable = True
        fields = (
            'id',
            'NAME_CLIENT', 
            'DATE_DOGOVOR',
            'DATE_POGASH',
            'SUM_DOG_NOM',
            'VALUTE',
            'BRANCH',
            'TYPE_CLIENT',
            )