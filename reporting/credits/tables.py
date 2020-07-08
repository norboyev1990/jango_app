import django_tables2 as tables
from .models import *
import itertools

attrs_title = {
    "td":{"class":"text-truncate"}}

attrs_text_center = {
    "th":{"class":"text-center"}, 
    "td":{"class":"text-center"}, 
    "tf":{"class":"text-center"}}

attrs_table_style = {
    "class": "table table-centered table-hover mb-10", 
    "thead": {"class": "thead-dark"},
    "tfoot": {"class": "bg-light"}}

class StringColumn(tables.Column):
    attrs = attrs_title
    def render(self, value):
        return value

class NumberColumn(tables.Column):
    attrs = attrs_text_center
    def render(self, value):
        return int('{:0.0f}'.format(value))

class PercentColumn(tables.Column):
    attrs = attrs_text_center
    def render(self, value):
        return '{:0.1%}'.format(value)

class InfoCreditsTable(tables.Table):  
    Older = tables.Column(accessor='get_old_value', verbose_name="Предыдущий  месяц")  
    Never = tables.Column(accessor='get_new_value', verbose_name="Текущий месяц")  
    class Meta:
        model = InfoCredits
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        sequence = ('Title', 'Older', 'Never', 'Updates', 'Percent')
        exclude = ('id','Old_Value','New_Value')

class NplClientsTable(tables.Table):
    Name    = StringColumn(verbose_name="Наименование заёмщика", footer="Итого:")
    Balans  = NumberColumn(verbose_name="Остаток кредита", footer=lambda table: '{:0.2f}'.format(sum(x.Balans for x in table.data)))
    class Meta:
        model = NplClients
        template_name = "django_tables2/bootstrap4.html"
        orderable = False
        attrs = attrs_table_style
        exclude = ('id',)

class ToxicCreditsTable(tables.Table):
    Name    = StringColumn(verbose_name="Наименование клиента", footer="Итого:")
    Balans  = NumberColumn(verbose_name="Остаток р/с 16377", footer=lambda table: '{:0.2f}'.format(sum(x.Balans for x in table.data)))
    class Meta:
        model = ToxicCredits
        template_name = "django_tables2/bootstrap4.html"
        orderable = False
        attrs = attrs_table_style
        exclude = ('id',)

class OverdueCreditsTable(tables.Table):
    Balans = NumberColumn(verbose_name="Остаток р/с 16377")
    class Meta:
        model = OverdueCredits
        template_name = "django_tables2/bootstrap4.html"
        orderable = False
        attrs = attrs_table_style
        exclude = ('id',)
        


class ByTermsTable(tables.Table):
    Title       = StringColumn(verbose_name="Сроки", footer="Итого:")
    PorBalans   = NumberColumn(verbose_name="Кредитный портфель", footer=lambda table: int(sum(x.PorBalans for x in table.data)))
    PorPercent  = PercentColumn(verbose_name="Доля, %", footer="100%")
    NplBalans   = NumberColumn(verbose_name="NPL", footer=lambda table: int(sum(x.NplBalans for x in table.data)))
    ToxBalans   = NumberColumn(verbose_name="Токсичные кредиты", footer=lambda table: int(sum(x.ToxBalans for x in table.data)))
    AmountNTK   = NumberColumn(verbose_name="ТК + NPL", footer=lambda table: int(sum(x.AmountNTK for x in table.data)))
    WeightNTK   = PercentColumn(verbose_name="Удельный вес", footer=lambda table: '{:.1%}'.format(sum(x.AmountNTK for x in table.data)/sum(x.PorBalans for x in table.data)))
    ResBalans   = NumberColumn(verbose_name="Резервы", footer=lambda table: int(sum(x.ResBalans for x in table.data)))
    ResCovers   = PercentColumn(verbose_name="Покрытие резервами", footer=lambda table: '{:.1%}'.format(sum(x.ResBalans for x in table.data)/sum(x.AmountNTK for x in table.data))) 
    class Meta:
        model = ByTerms
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        exclude = ('id',)

class ByPercentageTable(tables.Table):
    Title = StringColumn(verbose_name="Коридор", footer="Итого:")
    ULLongTerm  = NumberColumn(verbose_name="Долгосрочные ЮЛ",  
        footer=lambda table: sum(x.ULLongTerm for x in table.data))
    ULShortTerm = NumberColumn(verbose_name="Краткосрочные ЮЛ", 
        footer=lambda table: sum(x.ULShortTerm for x in table.data))
    FLLongTerm  = NumberColumn(verbose_name="Долгосрочные ФЛ", 
        footer=lambda table: sum(x.FLLongTerm for x in table.data))
    FLShortTerm = NumberColumn(verbose_name="Краткосрочные ФЛ", 
        footer=lambda table: sum(x.FLShortTerm for x in table.data))
    ULLongPart  = NumberColumn(verbose_name="Доля, %", 
        footer=lambda table: sum(x.ULLongPart for x in table.data))
    ULShortPart = NumberColumn(verbose_name="Доля, %", 
        footer=lambda table: sum(x.ULShortPart for x in table.data))
    FLLongPart  = NumberColumn(verbose_name="Доля, %", 
        footer=lambda table: sum(x.FLLongPart for x in table.data))
    FLShortPart = NumberColumn(verbose_name="Доля, %", 
        footer=lambda table: sum(x.FLShortPart for x in table.data))
    class Meta:
        model = ByPercentage
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        exclude = ('id',)


class ByPercentageULTable(tables.Table):
    Title = StringColumn(verbose_name="Коридор", footer="Итого:")
    Term1  = NumberColumn(verbose_name="до 2-х лет", footer=lambda table: sum(x.Term1 for x in table.data))
    Term2  = NumberColumn(verbose_name="от 2-х до 5 лет", footer=lambda table: sum(x.Term2 for x in table.data))
    Term3  = NumberColumn(verbose_name="от 5-ти до 7 лет", footer=lambda table: sum(x.Term3 for x in table.data))
    Term4  = NumberColumn(verbose_name="от 7-ми до 10 лет", footer=lambda table: sum(x.Term4 for x in table.data))
    Term5  = NumberColumn(verbose_name="свыше 10 лет", footer=lambda table: sum(x.Term5 for x in table.data))
    class Meta:
        model = ByPercentageUL
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        exclude = ('id',)

class ByAverageULTable(tables.Table):
    TITLE       = StringColumn(verbose_name = "Срок")
    UZS_AVERAGE = NumberColumn(verbose_name = "UZS")
    USD_AVERAGE = NumberColumn(verbose_name = "USD")
    EUR_AVERAGE = NumberColumn(verbose_name = "EUR")
    JPY_AVERAGE = NumberColumn(verbose_name = "JPY")
    
    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False

class ByAverageFLTable(tables.Table):
    TITLE     = StringColumn(verbose_name="Продукты", footer="Итого:")
    BALANS    = NumberColumn(verbose_name = "UZS",
        footer=lambda table: '{:.1f}'.format(
            sum(item['CREDIT'] for item in table.data)/sum(item['LOAN'] for item in table.data))
    )
    
    class Meta:
        attrs = attrs_table_style
        orderable = False

class ByRetailProductTable(tables.Table):
    Title       = StringColumn(verbose_name="Продукт", footer="Итого:")
    PorBalans   = NumberColumn(verbose_name="Кредитный портфель", footer=lambda table: sum(x.PorBalans for x in table.data))
    PorPercent  = NumberColumn(verbose_name="Доля, %", footer="100%")
    PrsBalans   = NumberColumn(verbose_name="Просрочка ОД", footer=lambda table: sum(x.PrsBalans for x in table.data))
    NplBalans   = NumberColumn(verbose_name="NPL", footer=lambda table: sum(x.NplBalans for x in table.data))
    NplWeight   = NumberColumn(verbose_name="Удельный вес", 
        footer=lambda table: '{:.1%}'.format(sum(x.NplBalans for x in table.data)/sum(x.PorBalans for x in table.data))
    )
    NachBalans  = NumberColumn(verbose_name="Просрочка по % (16377)", footer=lambda table: sum(x.NachBalans for x in table.data))
    class Meta:
        model = ByRetailProduct
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
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