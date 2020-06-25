import django_tables2 as tables
from .models import *
import itertools

attr_right_text = {"th":{"class":"text-center"}, "td":{"class":"text-center"}, "tf":{"class":"text-center"}}
attr_title_text = {"td":{"class":"sorting_1"}, "tf":{"class":"sorting_1"}}

class NplClientsTable(tables.Table):
    Name = tables.Column(verbose_name="Наименование заёмщика", attrs=attr_title_text)
    Balans = tables.Column(verbose_name="Остаток кредита", attrs=attr_right_text)
    class Meta:
        model = NplClients
        orderable = False
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-centered table-hover mb-10", "thead": {"class": "thead-light"}}
        exclude = ('id',)

class ToxicCreditsTable(tables.Table):
    Balans = tables.Column(verbose_name="Остаток р/с 16377", attrs=attr_right_text, 
        footer=lambda table: sum(x.Balans for x in table.data))
    class Meta:
        model = ToxicCredits
        orderable = False
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-centered table-hover mb-10", "thead": {"class": "thead-light"}}
        exclude = ('id',)

class OverdueCreditsTable(tables.Table):
    Balans = tables.Column(verbose_name="Остаток р/с 16377", attrs=attr_right_text)
    class Meta:
        model = OverdueCredits
        orderable = False
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-centered table-hover mb-10", "thead": {"class": "thead-light"}}
        exclude = ('id',)
        
class OverallInfoTable(tables.Table):
    name        = tables.Column(verbose_name="Показатели")
    old_value   = tables.Column(attrs=attr_right_text, verbose_name="Предыдущий  месяц")
    new_value   = tables.Column(attrs=attr_right_text, verbose_name="Текущий месяц")
    difference  = tables.Column(attrs=attr_right_text, verbose_name="Изменение")
    percentage  = tables.Column(attrs=attr_right_text, verbose_name="Изменение, %")

    
    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-centered table-hover mb-10", "thead": {"class": "thead-light"}}
        orderable = False

class ByTermsTable(tables.Table):
    Title = tables.Column(attrs={"td":{"class":"text-truncate"}}, verbose_name="Сроки", footer="Итого:")
    PorBalans = tables.Column(attrs=attr_right_text, verbose_name="Кредитный портфель",
        footer=lambda table: sum(x.PorBalans for x in table.data))
    PorPercent = tables.Column(attrs=attr_right_text, verbose_name="Доля, %", footer="100%")
    NplBalans = tables.Column(attrs=attr_right_text, verbose_name="NPL",
        footer=lambda table: sum(x.NplBalans for x in table.data))
    ToxBalans = tables.Column(attrs=attr_right_text, verbose_name="Токсичные кредиты",
        footer=lambda table: sum(x.ToxBalans for x in table.data))
    NplToxic = tables.Column(accessor='amount_npl_toxic', attrs=attr_right_text, verbose_name="ТК + NPL",
        footer=lambda table: sum(x.NplBalans+x.ToxBalans for x in table.data))
    TKNWeight = tables.Column(accessor='weight_npl_toxic', attrs=attr_right_text, verbose_name="Удельный вес",
        footer=lambda table: '{:.1%}'.format(sum(x.NplBalans+x.ToxBalans for x in table.data)/sum(x.PorBalans for x in table.data)))
    ResBalans = tables.Column(attrs=attr_right_text, verbose_name="Резервы",
        footer=lambda table: sum(x.ResBalans for x in table.data))
    ResCover = tables.Column(accessor='reserve_cover', attrs=attr_right_text, verbose_name="Покрытие резервами",
        footer=lambda table: '{:.1%}'.format(sum(x.ResBalans for x in table.data)/sum(x.NplBalans+x.ToxBalans for x in table.data)))
    
    class Meta:
        model = ByTerms
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-centered table-hover mb-10", "thead": {"class": "thead-light text-truncate"}, "tfoot": {"class": "bg-light"}}
        sequence = ('Title', 'PorBalans', 'PorPercent', 'NplBalans', 'ToxBalans', 'NplToxic', 'TKNWeight', 'ResBalans')
        orderable = False
        exclude = ('id',)

class ByPercentageTable(tables.Table):
    Title = tables.Column(verbose_name="Коридор", attrs={"td":{"class":"text-truncate"}}, footer="Итого:")
    ULLongTerm  = tables.Column(verbose_name="Долгосрочные ЮЛ", attrs=attr_right_text, 
        footer=lambda table: sum(x.ULLongTerm for x in table.data))
    ULShortTerm = tables.Column(verbose_name="Краткосрочные ЮЛ", attrs=attr_right_text, 
        footer=lambda table: sum(x.ULShortTerm for x in table.data))
    FLLongTerm  = tables.Column(verbose_name="Долгосрочные ФЛ", attrs=attr_right_text, 
        footer=lambda table: sum(x.FLLongTerm for x in table.data))
    FLShortTerm = tables.Column(verbose_name="Краткосрочные ФЛ", attrs=attr_right_text, 
        footer=lambda table: sum(x.FLShortTerm for x in table.data))
    ULLongPart  = tables.Column(verbose_name="Доля, %", attrs=attr_right_text, 
        footer=lambda table: sum(x.ULLongPart for x in table.data))
    ULShortPart = tables.Column(verbose_name="Доля, %", attrs=attr_right_text, 
        footer=lambda table: sum(x.ULShortPart for x in table.data))
    FLLongPart  = tables.Column(verbose_name="Доля, %", attrs=attr_right_text, 
        footer=lambda table: sum(x.FLLongPart for x in table.data))
    FLShortPart = tables.Column(verbose_name="Доля, %", attrs=attr_right_text, 
        footer=lambda table: sum(x.FLShortPart for x in table.data))
    class Meta:
        model = ByPercentage
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-centered table-hover mb-10", "thead": {"class": "thead-light text-truncate"}, "tfoot": {"class": "bg-light"}}
        orderable = False
        exclude = ('id',)


class ByPercentageULTable(tables.Table):
    Title = tables.Column(verbose_name="Коридор", attrs={"td":{"class":"text-truncate"}}, footer="Итого:")
    Term1  = tables.Column(verbose_name="до 2-х лет", attrs=attr_right_text, footer=lambda table: sum(x.Term1 for x in table.data))
    Term2  = tables.Column(verbose_name="от 2-х до 5 лет", attrs=attr_right_text, footer=lambda table: sum(x.Term2 for x in table.data))
    Term3  = tables.Column(verbose_name="от 5-ти до 7 лет", attrs=attr_right_text, footer=lambda table: sum(x.Term3 for x in table.data))
    Term4  = tables.Column(verbose_name="от 7-ми до 10 лет", attrs=attr_right_text, footer=lambda table: sum(x.Term4 for x in table.data))
    Term5  = tables.Column(verbose_name="свыше 10 лет", attrs=attr_right_text, footer=lambda table: sum(x.Term5 for x in table.data))
    class Meta:
        model = ByPercentageUL
        template_name = "django_tables2/bootstrap4.html"
        attrs = {
            "class": "table table-centered table-hover mb-10", 
            "thead": {"class": "thead-light text-truncate"}, 
            "tfoot": {"class": "bg-light"}}
        orderable = False
        exclude = ('id',)

class ByAverageULTable(tables.Table):
    TITLE       = tables.Column(verbose_name = "Срок")
    UZS_AVERAGE    = tables.Column(attrs=attr_right_text, verbose_name = "UZS")
    USD_AVERAGE    = tables.Column(attrs=attr_right_text, verbose_name = "USD")
    EUR_AVERAGE    = tables.Column(attrs=attr_right_text, verbose_name = "EUR")
    JPY_AVERAGE    = tables.Column(attrs=attr_right_text, verbose_name = "JPY")
    
    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        attrs = {
            "class": "table table-centered table-hover mb-10", 
            "thead": {"class": "thead-light text-truncate"}, 
            "tfoot": {"class": "bg-light"}}
        orderable = False

class ByAverageFLTable(tables.Table):
    TITLE     = tables.Column(verbose_name="Продукты", footer="Итого:")
    BALANS    = tables.Column(attrs=attr_right_text, verbose_name = "UZS",
        footer=lambda table: '{:.1f}'.format(
            sum(item['CREDIT'] for item in table.data)/sum(item['LOAN'] for item in table.data))
    )
    
    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        attrs = {
            "class": "table table-centered table-hover mb-10", 
            "thead": {"class": "thead-light text-truncate"}, 
            "tfoot": {"class": "bg-light"}}
        orderable = False

class ByRetailProductTable(tables.Table):
    Title = tables.Column(verbose_name="Продукт", footer="Итого:")
    PorBalans  = tables.Column(verbose_name="Кредитный портфель", attrs=attr_right_text, footer=lambda table: sum(x.PorBalans for x in table.data))
    PorPercent = tables.Column(verbose_name="Доля, %", attrs=attr_right_text, footer="100%")
    PrsBalans  = tables.Column(verbose_name="Просрочка ОД", attrs=attr_right_text, footer=lambda table: sum(x.PrsBalans for x in table.data))
    NplBalans  = tables.Column(verbose_name="NPL", attrs=attr_right_text, footer=lambda table: sum(x.NplBalans for x in table.data))
    NplWeight  = tables.Column(verbose_name="Удельный вес", attrs=attr_right_text, 
        footer=lambda table: '{:.1%}'.format(sum(x.NplBalans for x in table.data)/sum(x.PorBalans for x in table.data))
    )
    NachBalans  = tables.Column(verbose_name="Просрочка по % (16377)", attrs=attr_right_text, footer=lambda table: sum(x.NachBalans for x in table.data))
    class Meta:
        model = ByRetailProduct
        template_name = "django_tables2/bootstrap4.html"
        attrs = {
            "class": "table table-centered table-hover mb-10", 
            "thead": {"class": "thead-light text-truncate"}, 
            "tfoot": {"class": "bg-light"}}
        orderable = False
        exclude = ('id',)


class ContractListTable(tables.Table):
    class Meta:
        model = ReportData
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-centered mb-10", "thead": {"class": "thead-light"}}
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