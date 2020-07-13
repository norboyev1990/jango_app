import django_tables2 as tables
from .models import *

attrs_title = {
    "td": {"class": "text-truncate"}}

attrs_text_center = {
    "th": {"class": "text-center"},
    "td": {"class": "text-center"},
    "tf": {"class": "text-center"}}

attrs_table_style = {
    "class": "table table-centered table-hover mb-10",
    "thead": {"class": "thead-dark text-truncate"},
    "tfoot": {"class": "bg-light"}}

attrs_scroll_table_style = {
    "id": "scroll-vertical-datatable",
    "class": "table dt-responsive nowrap",
    "thead": {"class": "thead-dark text-truncate"},
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

    def render_footer(self, bound_column, table):
        return '{:0.1%}'.format(sum(bound_column.accessor.resolve(row) for row in table.data))

class SummingColumn(tables.Column):
    attrs = attrs_text_center

    def render(self, value):
        return int(value)

    def render_footer(self, bound_column, table):
        return int(sum(bound_column.accessor.resolve(row) for row in table.data))

class AverageColumn(tables.Column):
    attrs = attrs_text_center

    def render(self, value):
        return '{:0.1f}'.format(value)

class InfoCreditsTable(tables.Table):
    Older = tables.Column(accessor='get_old_value', verbose_name="Предыдущий  месяц")
    Never = tables.Column(accessor='get_new_value', verbose_name="Текущий месяц")

    class Meta:
        model = InfoCredits
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        sequence = ('Title', 'Older', 'Never', 'Updates', 'Percent')
        exclude = ('id', 'Old_Value', 'New_Value')


class NplClientsTable(tables.Table):
    Name = StringColumn(verbose_name="Наименование заёмщика", footer="Итого:")
    Balans = SummingColumn(verbose_name="Остаток кредита")

    class Meta:
        model = NplClients
        template_name = "django_tables2/bootstrap4.html"
        orderable = False
        attrs = attrs_table_style
        exclude = ('id',)


class ToxicCreditsTable(tables.Table):
    Name = StringColumn(verbose_name="Наименование клиента", footer="Итого:")
    Balans = SummingColumn(verbose_name="Остаток р/с 16377")

    class Meta:
        model = ToxicCredits
        template_name = "django_tables2/bootstrap4.html"
        orderable = False
        attrs = attrs_table_style
        exclude = ('id',)


class OverdueCreditsTable(tables.Table):
    Name = StringColumn(verbose_name="Наименование клиента", footer="Итого:")
    Balans = SummingColumn(verbose_name="Остаток р/с 16377")

    class Meta:
        model = OverdueCredits
        template_name = "django_tables2/bootstrap4.html"
        orderable = False
        attrs = attrs_table_style
        exclude = ('id',)


class ByTermsTable(tables.Table):
    Title = StringColumn(verbose_name="Сроки", footer="Итого:")
    PorBalans = SummingColumn(verbose_name="Кредитный портфель")
    PorPercent = PercentColumn(verbose_name="Доля, %", footer="100%")
    NplBalans = SummingColumn(verbose_name="NPL")
    ToxBalans = SummingColumn(verbose_name="Токсичные кредиты")
    AmountNTK = SummingColumn(verbose_name="ТК + NPL")
    WeightNTK = PercentColumn(verbose_name="Удельный вес", footer=lambda table: '{:.1%}'.format(
        sum(x.AmountNTK for x in table.data) / sum(x.PorBalans for x in table.data)))
    ResBalans = SummingColumn(verbose_name="Резервы")
    ResCovers = PercentColumn(verbose_name="Покрытие резервами", footer=lambda table: '{:.1%}'.format(
        sum(x.ResBalans for x in table.data) / sum(x.AmountNTK for x in table.data)))

    class Meta:
        model = ByTerms
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        exclude = ('id',)

class ByRetailProductTable(tables.Table):
    Title = StringColumn(verbose_name="Продукт", footer="Итого:")
    PorBalans = SummingColumn(verbose_name="Кредитный портфель")
    PorPercent = PercentColumn(verbose_name="Доля, %", footer="100%")
    PrsBalans = SummingColumn(verbose_name="Просрочка ОД")
    NplBalans = SummingColumn(verbose_name="NPL")
    NplWeight = PercentColumn(verbose_name="Удельный вес", footer=lambda table: '{:.1%}'.format(
        sum(x.NplBalans for x in table.data)/sum(x.PorBalans for x in table.data)))
    NachBalans = SummingColumn(verbose_name="Просрочка по % (16377)")

    class Meta:
        model = ByRetailProduct
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        exclude = ('id',)


class ByPercentageTable(tables.Table):
    Title = StringColumn(verbose_name="Коридор", footer="Итого:")
    ULLongTerm = SummingColumn(verbose_name="Долгосрочные ЮЛ")
    ULShortTerm = SummingColumn(verbose_name="Краткосрочные ЮЛ")
    FLLongTerm = SummingColumn(verbose_name="Долгосрочные ФЛ")
    FLShortTerm = SummingColumn(verbose_name="Краткосрочные ФЛ")
    ULLongPart = PercentColumn(verbose_name="Доля, %")
    ULShortPart = PercentColumn(verbose_name="Доля, %")
    FLLongPart = PercentColumn(verbose_name="Доля, %")
    FLShortPart = PercentColumn(verbose_name="Доля, %")

    class Meta:
        model = ByPercentage
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        exclude = ('id',)


class ByPercentageULTable(tables.Table):
    Title = StringColumn(verbose_name="Коридор", footer="Итого:")
    TermLess2 = SummingColumn(verbose_name="до 2-х лет")
    PartLess2 = PercentColumn(verbose_name="Доля, %")
    TermLess5 = SummingColumn(verbose_name="от 2-х до 5 лет")
    PartLess5 = PercentColumn(verbose_name="Доля, %")
    TermLess7 = SummingColumn(verbose_name="от 5-ти до 7 лет")
    PartLess7 = PercentColumn(verbose_name="Доля, %")
    TermLess10 = SummingColumn(verbose_name="от 7-ми до 10 лет")
    PartLess10 = PercentColumn(verbose_name="Доля, %")
    TermMore10 = SummingColumn(verbose_name="свыше 10 лет")
    PartMore10 = PercentColumn(verbose_name="Доля, %")


    class Meta:
        model = ByPercentageUL
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        exclude = ('id',)


class ByAverageULTable(tables.Table):
    Title      = StringColumn(verbose_name="Срок", footer="Итого:")
    AverageUZS = AverageColumn(verbose_name="UZS", footer=lambda table:
                '{:.2f}'.format(max(c.TotalUZS for c in table.data)))
    AverageUSD = AverageColumn(verbose_name="USD", footer=lambda table:
                '{:.2f}'.format(max(c.TotalUSD for c in table.data)))
    AverageEUR = AverageColumn(verbose_name="EUR", footer=lambda table:
                '{:.2f}'.format(max(c.TotalEUR for c in table.data)))
    AverageJPY = AverageColumn(verbose_name="JPY", footer=lambda table:
                '{:.2f}'.format(max(c.TotalJPY for c in table.data)))

    class Meta:
        model = ByAverageUl
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        exclude = ('id','TotalUZS','TotalUSD','TotalEUR','TotalJPY')


class ByAverageFLTable(tables.Table):
    Title   = StringColumn(verbose_name="Продукты", footer="Итого:")
    Balance = AverageColumn(verbose_name="UZS", footer=lambda table:
                '{:.1f}'.format(max(c.Average for c in table.data)))

    class Meta:
        model = ByAverageFl
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_table_style
        orderable = False
        exclude = ('id','Average')

class ByOverdueBranchTable(tables.Table):
    Title = StringColumn(verbose_name="Филиал", footer="Итого:")
    Balance = SummingColumn(verbose_name="Выданные")
    Overdue = SummingColumn(verbose_name="Просрочка")
    CountPr = SummingColumn(verbose_name="Количество")

    class Meta:
        model = ByOverdueBranch
        template_name = "django_tables2/bootstrap4.html"
        attrs = attrs_scroll_table_style
        orderable = False
        exclude = ('id',)

