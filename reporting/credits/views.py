import pandas as pd
import numpy as np
from django.shortcuts import render
from django.db import connection
from io import BytesIO
from pandas import DataFrame
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django_tables2 import SingleTableView
from openpyxl import *
from .functions import CursorByName
from .queries import Query
from .models import *
from .tables import *
import json
from django_tables2.export.views import ExportMixin
from django_tables2.export.export import TableExport
from django_pandas.io import read_frame
# Create your views here.

def setReviewMonthInSession(request):
    if (request.POST.get('data_month')):
        request.session['data_month'] = request.POST.get('data_month')
        HttpResponseRedirect(request.path_info)
    
    if 'data_month' not in request.session:
        request.session['data_month'] = '2020-04'      

def index(request):
    setReviewMonthInSession(request)

    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    mylist = InfoCredits.objects.raw('SELECT ROWNUM as id, T.* FROM TABLE(GET_INDS(%s)) T', [sMonth])


    # cursor = connection.cursor()
    # cursor.execute(Query.named_query_indicators(), {'month2':sMonth.month, 'month1':sMonth.month-1})
    # data = [2]
    # for row in CursorByName(cursor):
    #     data.append(row)

    
    
    gdpData = {}
    gdpName = {}

    if (request.GET.get('q')=='tox'):
        geoTitle = "Токсичные кредиты"
        geoData = DataByGeocode.objects.raw(Query.orcl_toxics_by_branches(), [report.id])
    elif (request.GET.get('q')=='prs'):
        geoTitle = "Просрочка"
        geoData = DataByGeocode.objects.raw(Query.orcl_overdues_by_branches(), [report.id])
    else:
        geoTitle = "NPL клиенты"
        geoData = DataByGeocode.objects.raw(Query.orcl_npls_by_branches(), [report.id])

    for p in geoData:
        gdpData[p.GeoCode] = int(p.Balance)
        gdpName[p.GeoCode] = p.Title
    

    statistics = {
        'portfolio_value'   : mylist[0].New_Value,
        'portfolio_percent' : '{}%'.format(mylist[0].Percent),
        'portfolio_growth'  : mylist[0].Updates,
        'npl_value'         : mylist[1].New_Value,
        'npl_percent'       : '{}%'.format(mylist[1].Percent),
        'npl_growth'        : mylist[1].Updates,
        'toxic_value'       : mylist[3].New_Value,
        'toxic_percent'     : '{}%'.format(mylist[3].Percent),
        'toxic_growth'      : mylist[3].Updates,
        'overdue_value'     : mylist[8].New_Value,
        'overdue_percent'   : '{}%'.format(mylist[8].Percent),
        'overdue_growth'    : mylist[8].Updates,
    }

    context = {
        "page_title": "NPL кредиты",
        "statistics": statistics,
        "data_month": request.session['data_month'],
        "npls_page": "active",
        "gdpData": json.dumps(gdpData),
        "gdpName": json.dumps(gdpName),
        "geoTitle": geoTitle,
    }

    return render(request, 'credits/index.html', context)

def npls(request): 
    
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    
    top = int(request.GET.get('tp')) if request.GET.get('tp') else 9999999
    table = NplClientsTable(NplClients.objects.raw(Query.orcl_npls(), [report.id])[:top])
    table.paginate(page=request.GET.get("page", 1), per_page=10) 
    
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("npls_table.{}".format(export_format))  

    context = {
        "page_title": "NPL кредиты",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "npls_page": "font-weight-bold"
    }

    return render(request, 'credits/view.html', context)

def toxics(request):

    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)

    top = int(request.GET.get('tp')) if request.GET.get('tp') else 9999999
    table = ToxicCreditsTable(ToxicCredits.objects.raw(Query.orcl_toxics(), [report.id])[:top])
    table.paginate(page=request.GET.get("page", 1), per_page=10)            
    
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "Токсичные кредиты"})
        return exporter.response("toxics_table.{}".format(export_format))  

    context = {
        "page_title": "Токсичные кредиты",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "toxics_page" : "font-weight-bold"
    }

    return render(request, 'credits/view.html', context)

def overdues(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    
    top = int(request.GET.get('tp')) if request.GET.get('tp') else 9999999
    table = OverdueCreditsTable(OverdueCredits.objects.raw(Query.orcl_overdues(), [report.id])[:top])
    table.paginate(page=request.GET.get("page", 1), per_page=10)            
    
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "Просроченные кредиты",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "overdues_page": "font-weight-bold"
    }

    return render(request, 'credits/view.html', context)

def indicators(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    mylist = InfoCredits.objects.raw('SELECT ROWNUM as id, T.* FROM TABLE(GET_INDS(%s)) T', [sMonth])
    table = InfoCreditsTable(mylist)
    
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))  

    context = {
        "page_title": "Общие показатели",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "indicators_page" : "font-weight-bold"
    }

    return render(request, 'credits/view.html', context)

def byterms(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)

    data = ByTerms.objects.raw(Query.orcl_byterms(), [report.id])
    table = ByTermsTable(data)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "В разбивке по срокам",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "byterms_page": "font-weight-bold"
    }

    return render(request, 'credits/view.html', context)

def bysubjects(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)

    data = ByTerms.objects.raw(Query.orcl_bysubjects(), [report.id])
    table = ByTermsTable(data)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "В разбивке по субъектам",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "bysubjects_page": "font-weight-bold"
    }

    return render(request, 'credits/view.html', context)

def bysegments(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)

    data = ByTerms.objects.raw(Query.orcl_bysegments(), [report.id])
    table = ByTermsTable(data)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "В разбивке по сегментам",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "bysegments_page": "font-weight-bold"
    }

    return render(request, 'credits/view.html', context)

def bycurrency(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    data = ByTerms.objects.raw(Query.orcl_bycurrency(), [report.id])
    table = ByTermsTable(data)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "В разбивке по валютам",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "bycurrency_page": "font-weight-bold"}
    return render(request, 'credits/view.html', context)

def bybranches(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    data = ByTerms.objects.raw(Query.orcl_bybranches(), [report.id])
    table = ByTermsTable(data)
    table.paginate(page=request.GET.get("page", 1), per_page=10)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "В разбивке по филиалам",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "bybranches_page": "font-weight-bold"}
    return render(request, 'credits/view.html', context)

def byretailproduct(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    data = ByRetailProduct.objects.raw(Query.orcl_byretailproduct(), [report.id])
    table = ByRetailProductTable(data)

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title" : "По продуктам розничного бизнеса",
        "data_table" : table,
        "data_month": sMonth.strftime('%Y-%m'),
        "byretailproduct_page" : "font-weight-bold",

    }

    return render(request, 'credits/view.html', context)

def bypercentage_national(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)

    table = ByPercentageTable(ByPercentage.objects.raw(Query.orcl_bypercentage_national(), [report.id]))

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))
    
    context = {
        "page_title": "В разбивке по процентной ставке",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "bypercentage_national_page": "font-weight-bold"}
    return render(request, 'credits/view.html', context)

def bypercentage_foreign(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)

    table = ByPercentageTable(ByPercentage.objects.raw(Query.orcl_bypercentage_foreign(), [report.id]))

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))
    
    context = {
        "page_title": "В разбивке по процентной ставке",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "bypercentage_foreign_page": "font-weight-bold"}
    return render(request, 'credits/view.html', context)

def bypercentage_national_ul(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    table = ByPercentageULTable(ByPercentageUL.objects.raw(Query.orcl_bypercentage_national_ul(), [report.id]))

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "В разбивке по процентной ставке",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "bypercentage_national_ul_page": "font-weight-bold"}
    return render(request, 'credits/view.html', context)

def bypercentage_foreign_ul(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    table = ByPercentageULTable(ByPercentageUL.objects.raw(Query.orcl_bypercentage_foreign_ul(), [report.id]))
    
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "В разбивке по процентной ставке",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "bypercentage_foreign_ul_page": "font-weight-bold"}
    return render(request, 'credits/view.html', context)

def byaverageweight_ul(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    table = ByAverageULTable(ByAverageUl.objects.raw(Query.orcl_byaverageweight_ul(), [report.id]))

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title" : "В разбивке по средневзвешенной процентной ставке",
        "data_table" : table,
        "data_month": sMonth.strftime('%Y-%m'),
        "byaverageweight_ul_page" : "font-weight-bold"}
    return render(request, 'credits/view.html', context)

def byaverageweight_fl(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    table = ByAverageFLTable(ByAverageFl.objects.raw(Query.orcl_byaverageweight_fl(), [report.id]))
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "В разбивке по средневзвешенной процентной ставке",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "byaverageweight_fl_page" : "font-weight-bold"
    }

    return render(request, 'credits/view.html', context)

def byoverduebranch(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    table = ByOverdueBranchTable(ByOverdueBranch.objects.raw(Query.orcl_byoverduebrach(), [report.id]))

    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table,dataset_kwargs={"title": "NPL клиенты"})
        return exporter.response("table.{}".format(export_format))

    context = {
        "page_title": "Выданные | просрочка ",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "byoverduebranch_page": "font-weight-bold"}
    return render(request, 'credits/view.html', context)

# Экспортировать все таблицы в Excel
def export_all_tables(request):
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    last_month = pd.to_datetime(request.session['data_month']) - pd.DateOffset(months=1)
    cursor = connection.cursor()
    # Indicators
    cursor.execute('''SELECT ROWNUM as id, T.* FROM TABLE(GET_INDS(%s)) T''', [sMonth])
    ind_data = []
    for row in CursorByName(cursor):
        ind_data.append(row)

    ind_df = pd.DataFrame(ind_data)
    ind_df.drop(['ID'], axis=1, inplace=True)
    ind_df.rename(columns={"TITLE": "Показатели", "OLD_VALUE": last_month.strftime('%d.%m.%Y'), "NEW_VALUE": sMonth.strftime('%d.%m.%Y'),
                           "UPDATES": "Изменение", "PERCENT": "Изменение, %"},
                   inplace=True)
   
    #NPLS
    cursor.execute(Query.orcl_npls(), [report.id])
    npl_data = []
    for row in CursorByName(cursor):
        npl_data.append(row)
    
    npls_df = pd.DataFrame(npl_data[1:])
    npls_df = npls_df.head(10)
    npls_df.drop(['ID', 'NUMERAL'], axis=1, inplace = True)
    npls_df.rename(columns={"NAME": "Наименование клиента", "BRANCH": "Филиал", "BALANS": "Остаток Кредита"}, inplace =True)

    #TOXIC
    cursor.execute(Query.orcl_toxics(), [report.id])
    toxic = []
    for row in CursorByName(cursor):
        toxic.append(row)
    toxic_df = pd.DataFrame(toxic[1:])
    toxic_df = toxic_df.head(10)
    toxic_df.drop(['ID', 'NUMERAL'], axis=1, inplace = True)
    toxic_df.rename(columns={"NAME": "Наименование клиента", "BRANCH": "Филиал", "BALANS": "Остаток Кредита"}, inplace =True)

    #OVERDUE
    cursor.execute(Query.orcl_overdues(), [report.id])
    overdues = []
    for row in CursorByName(cursor):
        overdues.append(row)
    overdues_df = pd.DataFrame(overdues[1:])
    overdues_df = overdues_df.head(10)
    overdues_df.drop(['ID', 'NUMERAL'], axis=1, inplace = True)
    overdues_df.rename(columns={"NAME": "Наименование клиента", "BRANCH": "Филиал", "BALANS": "Остаток Кредита"}, inplace =True)
    
    #BYTERM
    cursor.execute(Query.orcl_byterms(), [report.id])
    byterm = []
    for row in CursorByName(cursor):
        byterm.append(row)
    byterm_df = pd.DataFrame(byterm)
    byterm_df.drop(['ID'], axis=1, inplace = True)
    byterm_df = byterm_df.pivot_table(index='TITLE',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    byterm_df = byterm_df.reset_index()

    byterm_df.rename(columns={"TITLE": "Сроки", "AMOUNTNTK": "ТК+NPL", "NPLBALANS": "NPL",  "PORBALANS": "Кредитный портфель", "PORPERCENT": "Доля %",
                                 "RESBALANS": "Резервы", "RESCOVERS": "Покрытие ТК+NPL резервами" , "TOXBALANS": "Токсичные кредиты", "WEIGHTNTK": "Удельный вес к своему портфелю"}, inplace =True)

    byterm_df = byterm_df.set_index('Сроки')
    byterm_df = byterm_df.rename({'total': 'Итого:'}, axis='index')
    byterm_df = byterm_df.reset_index()
    byterm_df['Доля %'] = (byterm_df['Доля %'].astype('float64') * 100).round(1).astype('str') + '%'
    byterm_df['Покрытие ТК+NPL резервами'] = (byterm_df['Покрытие ТК+NPL резервами'].astype('float64') * 100).round(1).astype('str') + '%'
    byterm_df['Удельный вес к своему портфелю'] = (byterm_df['Удельный вес к своему портфелю'].astype('float64') * 100).round(1).astype('str') + '%'
    byterm_df = byterm_df[["Сроки", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    byterm_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = byterm_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].astype('int64')
    

    #BYSUBJECTS
    cursor.execute(Query.orcl_bysubjects(), [report.id])
    bysubjects = []
    for row in CursorByName(cursor):
        bysubjects.append(row)
    bysubjects_df = pd.DataFrame(bysubjects)
    bysubjects_df.drop(['ID'], axis=1, inplace = True)
    bysubjects_df = bysubjects_df.pivot_table(index='TITLE',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bysubjects_df = bysubjects_df.reset_index()

    bysubjects_df.rename(columns={"TITLE": "Статус", "AMOUNTNTK": "ТК+NPL", "NPLBALANS": "NPL",  "PORBALANS": "Кредитный портфель", "PORPERCENT": "Доля %",
                                 "RESBALANS": "Резервы", "RESCOVERS": "Покрытие ТК+NPL резервами" , "TOXBALANS": "Токсичные кредиты", "WEIGHTNTK": "Удельный вес к своему портфелю"}, inplace =True)

    bysubjects_df = bysubjects_df.set_index('Статус')
    bysubjects_df = bysubjects_df.rename({'total': 'Итого:'}, axis='index')
    bysubjects_df = bysubjects_df.reset_index()
    bysubjects_df['Доля %'] = (bysubjects_df['Доля %'].astype('float64') * 100).round(1).astype('str') + '%'
    bysubjects_df['Покрытие ТК+NPL резервами'] = (bysubjects_df['Покрытие ТК+NPL резервами'].astype('float64') * 100).round(1).astype('str') + '%'
    bysubjects_df['Удельный вес к своему портфелю'] = (bysubjects_df['Удельный вес к своему портфелю'].astype('float64') * 100).round(1).astype('str') + '%'
    bysubjects_df = bysubjects_df[["Статус", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    bysubjects_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = bysubjects_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].astype('int64')

    #BYSEGMENTS
    cursor.execute(Query.orcl_bysegments(), [report.id])
    bysegments = []
    for row in CursorByName(cursor):
        bysegments.append(row)
    bysegments_df = pd.DataFrame(bysegments)
    bysegments_df.drop(['ID'], axis=1, inplace = True)
    bysegments_df = bysegments_df.pivot_table(index='TITLE',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bysegments_df = bysegments_df.reset_index()

    bysegments_df.rename(columns={"TITLE": "Сегмент", "AMOUNTNTK": "ТК+NPL", "NPLBALANS": "NPL",  "PORBALANS": "Кредитный портфель", "PORPERCENT": "Доля %",
                                 "RESBALANS": "Резервы", "RESCOVERS": "Покрытие ТК+NPL резервами" , "TOXBALANS": "Токсичные кредиты", "WEIGHTNTK": "Удельный вес к своему портфелю"}, inplace =True)

    bysegments_df = bysegments_df.set_index('Сегмент')
    bysegments_df = bysegments_df.rename({'total': 'Итого:'}, axis='index')
    bysegments_df = bysegments_df.reset_index()
    bysegments_df['Доля %'] = (bysegments_df['Доля %'].astype('float64') * 100).round(1).astype('str') + '%'
    bysegments_df['Покрытие ТК+NPL резервами'] = (bysegments_df['Покрытие ТК+NPL резервами'].astype(
        'float64') * 100).round(1).astype('str') + '%'
    bysegments_df['Удельный вес к своему портфелю'] = (bysegments_df['Удельный вес к своему портфелю'].astype(
        'float64') * 100).round(1).astype('str') + '%'
    bysegments_df = bysegments_df[["Сегмент", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    bysegments_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = bysegments_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].astype('int64')

    #BYCURRENCY
    cursor.execute(Query.orcl_bycurrency(), [report.id])
    bycurrency = []
    for row in CursorByName(cursor):
        bycurrency.append(row)
    bycurrency_df = pd.DataFrame(bycurrency)
    bycurrency_df.drop(['ID'], axis=1, inplace = True)
    bycurrency_df = bycurrency_df.pivot_table(index='TITLE',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bycurrency_df = bycurrency_df.reset_index()

    bycurrency_df.rename(columns={"TITLE": "Валюты", "AMOUNTNTK": "ТК+NPL", "NPLBALANS": "NPL",  "PORBALANS": "Кредитный портфель", "PORPERCENT": "Доля %",
                                 "RESBALANS": "Резервы", "RESCOVERS": "Покрытие ТК+NPL резервами" , "TOXBALANS": "Токсичные кредиты", "WEIGHTNTK": "Удельный вес к своему портфелю"}, inplace =True)

    bycurrency_df = bycurrency_df.set_index('Валюты')
    bycurrency_df = bycurrency_df.rename({'total': 'Итого:'}, axis='index')
    bycurrency_df = bycurrency_df.reset_index()
    bycurrency_df['Доля %'] = (bycurrency_df['Доля %'].astype('float64') * 100).round(1).astype('str') + '%'
    bycurrency_df['Покрытие ТК+NPL резервами'] = (bycurrency_df['Покрытие ТК+NPL резервами'].astype(
        'float64') * 100).round(1).astype('str') + '%'
    bycurrency_df['Удельный вес к своему портфелю'] = (bycurrency_df['Удельный вес к своему портфелю'].astype(
        'float64') * 100).round(1).astype('str') + '%'
    bycurrency_df = bycurrency_df[["Валюты", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    bycurrency_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = bycurrency_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].astype('int64')

    #BYBRANCHES
    cursor.execute(Query.orcl_bybranches(), [report.id])
    bybranches = []
    for row in CursorByName(cursor):
        bybranches.append(row)
    bybranches_df = pd.DataFrame(bybranches)
    bybranches_df.drop(['ID'], axis=1, inplace = True)
    bybranches_df = bybranches_df.pivot_table(index='TITLE',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bybranches_df = bybranches_df.reset_index()

    bybranches_df.rename(columns={"TITLE": "Филиалы", "AMOUNTNTK": "ТК+NPL", "NPLBALANS": "NPL",  "PORBALANS": "Кредитный портфель", "PORPERCENT": "Доля %",
                                 "RESBALANS": "Резервы", "RESCOVERS": "Покрытие ТК+NPL резервами" , "TOXBALANS": "Токсичные кредиты", "WEIGHTNTK": "Удельный вес к своему портфелю"}, inplace =True)
    bybranches_df = bybranches_df.set_index('Филиалы')
    bybranches_df = bybranches_df.rename({'total': 'Итого:'}, axis='index')
    bybranches_df = bybranches_df.reset_index()
    bybranches_df['Доля %'] = (bybranches_df['Доля %'].astype('float64') * 100).round(1).astype('str') + '%'
    bybranches_df['Покрытие ТК+NPL резервами'] = (bybranches_df['Покрытие ТК+NPL резервами'].astype(
        'float64') * 100).round(1).astype('str') + '%'
    bybranches_df['Удельный вес к своему портфелю'] = (bybranches_df['Удельный вес к своему портфелю'].astype(
        'float64') * 100).round(1).astype('str') + '%'
    bybranches_df = bybranches_df[["Филиалы", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    bybranches_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = bybranches_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].astype('int64')

    #BY NATIONAL PERCENTAGE 
    cursor.execute(Query.orcl_bypercentage_national(), [report.id])
    bypercentage_national = []
    for row in CursorByName(cursor):
        bypercentage_national.append(row)
    bypercentage_national_df = pd.DataFrame(bypercentage_national)
    bypercentage_national_df.drop(['NUMERAL'], axis=1, inplace = True)
    bypercentage_national_df = bypercentage_national_df.pivot_table(index='TITLE',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bypercentage_national_df = bypercentage_national_df.reset_index()

    bypercentage_national_df.rename(columns={"TITLE": "Коридор", "FLLONGPART": "Доля % ФЛД", "FLLONGTERM": "ФЛ-Долгосрочный", "FLSHORTPART": "Доля % ФЛК",
                                 "FLSHORTTERM": "ФЛ-Краткосрочный", "ULLONGPART": "Доля % ЮЛД", 'ULLONGTERM': 'ЮЛ-Долгосрочный',
                                 'ULSHORTPART': 'Доля % ЮЛД', 'ULSHORTTERM':'ЮЛ-Краткосрочный'}, inplace =True)

    bypercentage_national_df = bypercentage_national_df[["Коридор", 'ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']]
    bypercentage_national_df = bypercentage_national_df.set_index('Коридор')

    bypercentage_national_df[['ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']] = bypercentage_national_df[['ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']].astype('int64')

    pctCols = []
    for colName, col in bypercentage_national_df.iteritems():
        if colName[0] != 'total':
            pctCol = (col / col.iloc[-1] * 100).round(1).astype('str') + '%'
            pctCol.name = 'Доля %'
            pctCols.append(pctCol)

    pos = 1
    for col in pctCols:
        bypercentage_national_df.insert(pos, column=col.name, value=col, allow_duplicates=True)
        pos += 2

    bypercentage_national_df = bypercentage_national_df.apply(lambda x:x.replace("nan%", '0'))
    bypercentage_national_df = bypercentage_national_df.fillna(0)
    bypercentage_national_df = bypercentage_national_df.rename({'total': 'Итого:'}, axis='index')
    bypercentage_national_df = bypercentage_national_df.reset_index()


    #BY FOREGIN PERCENTAGE
    cursor.execute(Query.orcl_bypercentage_foreign(), [report.id])
    bypercentage_foreign = []
    for row in CursorByName(cursor):
        bypercentage_foreign.append(row)
    bypercentage_foreign_df = pd.DataFrame(bypercentage_foreign)
    bypercentage_foreign_df.drop(['NUMERAL'], axis=1, inplace = True)


    bypercentage_foreign_df.rename(columns={"TITLE": "Коридор", 'ULLONGTERM': 'ЮЛ-Долгосрочный', 'ULSHORTTERM': 'ЮЛ-Краткосрочный', 'FLLONGTERM': 'ФЛ-Долгосрочный', 'FLSHORTTERM': 'ФЛ-Краткосрочный'}, inplace =True)

    bypercentage_foreign_df = bypercentage_foreign_df[["Коридор", 'ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']]
    bypercentage_foreign_df[['ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']] = bypercentage_foreign_df[['ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']].astype('int64')
    bypercentage_foreign_df = bypercentage_foreign_df.reset_index()
    bypercentage_foreign_df = bypercentage_foreign_df.set_index('Коридор')
    bypercentage_foreign_df = bypercentage_foreign_df[['ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']]
    bypercentage_foreign_df.loc['total', :] = bypercentage_foreign_df.sum(axis=0)
    pctCols = []
    for colName, col in bypercentage_foreign_df.iteritems():
        if colName[0] != 'total':
            pctCol = (col / col.iloc[-1] * 100).round(1).astype('str') + '%'
            pctCol.name = 'Доля %'
            pctCols.append(pctCol)

    pos = 1
    for col in pctCols:
        bypercentage_foreign_df.insert(pos, column=col.name, value=col, allow_duplicates=True)
        pos += 2

    bypercentage_foreign_df = bypercentage_foreign_df.apply(lambda x:x.replace("nan%", '0'))
    bypercentage_foreign_df = bypercentage_foreign_df.fillna(0)
    bypercentage_foreign_df = bypercentage_foreign_df.rename({'total': 'Итого:'}, axis='index')
    bypercentage_foreign_df = bypercentage_foreign_df.reset_index()

    #В национальной валюте по ЮЛ (по срокам кредитов)
    cursor.execute(Query.orcl_bypercentage_national_ul(), [report.id])
    bypercentage_national_ul = []
    for row in CursorByName(cursor):
        bypercentage_national_ul.append(row)
    bypercentage_national_ul_df = pd.DataFrame(bypercentage_national_ul)
    bypercentage_national_ul_df.drop(['NUMERAL'], axis=1, inplace = True)
    bypercentage_national_ul_df = bypercentage_national_ul_df.set_index('TITLE')

    bypercentage_national_ul_df = bypercentage_national_ul_df.reset_index()

    bypercentage_national_ul_df.rename(columns={"TITLE": "Коридор", "TERMLESS2": "до 2-х лет", "TERMLESS5": "от 2-х до 5 лет", "TERMLESS7": "от 5-ти до 7 лет",
                                 "TERMLESS10": "от 7-ми до 10 лет", "TERMMORE10": "свыше 10 лет"}, inplace =True)


    bypercentage_national_ul_df = bypercentage_national_ul_df.set_index('Коридор')
    bypercentage_national_ul_df = bypercentage_national_ul_df[['до 2-х лет', 'от 2-х до 5 лет', 'от 5-ти до 7 лет', 'от 7-ми до 10 лет', 'свыше 10 лет']]
    bypercentage_national_ul_df = bypercentage_national_ul_df.apply(pd.to_numeric)
    bypercentage_national_ul_df.loc['total', :] = bypercentage_national_ul_df.sum(axis=0)
    pctCols = []
    for colName, col in bypercentage_national_ul_df.iteritems():
         if colName[0] != 'total':
             pctCol = (col / col.iloc[-1] * 100).round(1).astype('str') + '%'
             pctCol.name = 'Доля %'
             pctCols.append(pctCol)

    pos = 1
    for col in pctCols:
        bypercentage_national_ul_df.insert(pos, column=col.name, value=col, allow_duplicates=True)
        pos += 2

    bypercentage_national_ul_df = bypercentage_national_ul_df.apply(lambda x:x.replace("nan%", '0'))
    bypercentage_national_ul_df = bypercentage_national_ul_df.fillna(0)
    bypercentage_national_ul_df = bypercentage_national_ul_df.rename({'total': 'Итого:'}, axis='index')
    bypercentage_national_ul_df = bypercentage_national_ul_df.reset_index()
    bypercentage_national_ul_df[['до 2-х лет', 'от 2-х до 5 лет', 'от 5-ти до 7 лет', 'от 7-ми до 10 лет', 'свыше 10 лет']] = bypercentage_national_ul_df[['до 2-х лет', 'от 2-х до 5 лет', 'от 5-ти до 7 лет', 'от 7-ми до 10 лет', 'свыше 10 лет']].round(0)

    # #В иностранной  валюте по ЮЛ (по срокам кредитов)
    cursor.execute(Query.orcl_bypercentage_foreign_ul(), [report.id])
    bypercentage_foreign_ul = []
    for row in CursorByName(cursor):
        bypercentage_foreign_ul.append(row)
    bypercentage_foreign_ul_df = pd.DataFrame(bypercentage_foreign_ul)
    bypercentage_foreign_ul_df.drop(['NUMERAL'], axis=1, inplace = True)

    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.reset_index()

    bypercentage_foreign_ul_df.rename(columns={"TITLE": "Коридор", "TERMLESS2": "до 2-х лет", "TERMLESS5": "от 2-х до 5 лет", "TERMLESS7": "от 5-ти до 7 лет",
                                 "TERMLESS10": "от 7-ми до 10 лет", "TERMMORE10": "свыше 10 лет"}, inplace =True)

    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.set_index('Коридор')
    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df[['до 2-х лет', 'от 2-х до 5 лет', 'от 5-ти до 7 лет', 'от 7-ми до 10 лет', 'свыше 10 лет']]
    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.apply(pd.to_numeric)
    bypercentage_foreign_ul_df.loc['total', :] = bypercentage_foreign_ul_df.sum(axis=0)

    pctCols = []
    for colName, col in bypercentage_foreign_ul_df.iteritems():
         if colName[0] != 'total':
             pctCol = (col / col.iloc[-1] * 100).round(1).astype('str') + '%'
             pctCol.name = 'Доля %'
             pctCols.append(pctCol)

    pos = 1
    for col in pctCols:
        bypercentage_foreign_ul_df.insert(pos, column=col.name, value=col, allow_duplicates=True)
        pos += 2

    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.apply(lambda x:x.replace("nan%", '0'))
    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.fillna(0)
    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.rename({'total': 'Итого:'}, axis='index')
    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.reset_index()
    bypercentage_foreign_ul_df[['до 2-х лет', 'от 2-х до 5 лет', 'от 5-ти до 7 лет', 'от 7-ми до 10 лет', 'свыше 10 лет']] = bypercentage_foreign_ul_df[['до 2-х лет', 'от 2-х до 5 лет', 'от 5-ти до 7 лет', 'от 7-ми до 10 лет', 'свыше 10 лет']].round(0)

    #В разбивке по средневзвешенной процентной ставке (Юридические лица)                                                                             
    cursor.execute(Query.orcl_byaverageweight_ul(), [report.id])
    byweight_ul = []
    for row in CursorByName(cursor):
        byweight_ul.append(row)
    byaverageweight_ul_df = pd.DataFrame(byweight_ul)
    byaverageweight_ul_df = byaverageweight_ul_df.drop(['ID'], axis=1)

    byaverageweight_ul_df.rename(columns={"TITLE": "Срок", "AVERAGEUZS": "UZS", "AVERAGEUSD": "USD", "AVERAGEEUR": "EUR", "AVERAGEJPY": "JPY"}, inplace=True)
    byaverageweight_ul_df = byaverageweight_ul_df.set_index('Срок')
    by_sred_vzv = byaverageweight_ul_df[['UZS', 'USD', 'EUR', 'JPY']]
    by_sred_vzv.loc['Итого:', :] = by_sred_vzv.sum(axis=0)
    by_sred_vzv.iloc[2, 0] = byaverageweight_ul_df.iloc[0,4]
    by_sred_vzv.iloc[2, 1] = byaverageweight_ul_df.iloc[0, 5]
    by_sred_vzv.iloc[2, 2] = byaverageweight_ul_df.iloc[0, 6]
    by_sred_vzv.iloc[2, 3] = byaverageweight_ul_df.iloc[0, 7]
    by_sred_vzv[['UZS', 'USD', 'EUR', 'JPY']] = by_sred_vzv[['UZS', 'USD', 'EUR', 'JPY']].astype('float64').round(2)
    # by_sred_vzv = by_sred_vzv.fillna(0)
    # by_sred_vzv = by_sred_vzv.round(2)
    # by_sred_vzv = by_sred_vzv.rename(index={'3-Долгосрочный': 'Долгосрочные', '1-Краткосрочный' : 'Краткосрочные' })
    by_sred_vzv = by_sred_vzv.reset_index()

    #В разбивке по средневзвешенной процентной ставке (Юридические лица)                                                                             
    cursor.execute(Query.orcl_byaverageweight_fl(), [report.id])
    byweight_fl = []
    for row in CursorByName(cursor):
        byweight_fl.append(row)
    byaverageweight_fl_df = pd.DataFrame(byweight_fl)
    byaverageweight_fl_df = byaverageweight_fl_df.drop(['ID'], axis=1)
    byaverageweight_fl_df.rename(
        columns={"TITLE": "Продукты", "BALANCE": "UZS", "AVERAGE": "total"},
        inplace=True)
    byaverageweight_fl_df = byaverageweight_fl_df.append(overdues_df.sum(numeric_only=True), ignore_index=True)
    byaverageweight_fl_df.iloc[8, 0] = 'Итого:'
    byaverageweight_fl_df.iloc[8, 1] = byaverageweight_fl_df.iloc[1, 2]
    byaverageweight_fl_df.drop(['total'], axis=1, inplace=True)
    byaverageweight_fl_df["UZS"] = byaverageweight_fl_df["UZS"].astype('float64').round(2)



    dfs = {'Показатели': ind_df, 'Топ NPL': npls_df, 'Топ ТК': toxic_df, 'Топ проср': overdues_df, 'В разбивке по срокам': byterm_df,
        'В разбивке по субъектам': bysubjects_df, 'В разбивке по сегментам':bysegments_df, 'В разбивке по валютам': bycurrency_df, 
        'В разбивке по филиалам':bybranches_df, 'В разбивке по проц став нац.в' : bypercentage_national_df, 
        'В разбивке по проц став инстр.в' : bypercentage_foreign_df, 'В национальной валюте по ЮЛ': bypercentage_national_ul_df,
        'В иностранной валюте по ЮЛ': bypercentage_foreign_ul_df, 'В разбивке по срднвзв прц ЮЛ': by_sred_vzv, 'В разбивке по срднвзв прц ФЛ': byaverageweight_fl_df}
   
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        for sheetname, df in dfs.items():  # loop through `dict` of dataframes
            df.to_excel(writer, sheet_name=sheetname, index=False)  # send df to writer
            workbook  = writer.book
            worksheet = writer.sheets[sheetname]  # pull worksheet object
            format = workbook.add_format({'text_wrap': True})
            for idx, col in enumerate(npls_df):
              # loop through all columns
                series = npls_df[col]
                max_len = max((
                    series.astype(str).map(len).max(),  # len of largest item
                    len(str(series.name))  # len of column name/header
                    )) + 3  # adding a little extra space
                worksheet.set_column(idx, idx, max_len, format)
        writer.save()
        writer.close()
        response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
        response["Content-Disposition"] = 'attachment; filename="all_reports.xlsx"'
        return response

# Загрузка основные данных из Excel
def upload_excel(request):
    start = datetime.now()
    data = pd.read_excel (r'media/portfel/april.xlsx', 
        dtype=str)

    data = data.fillna('')
    data.columns = [
        'number', 'code_reg', 'mfo', 'name_client', 'balans_schet', 'credit_schet', 
        'date_resheniya', 'code_val', 'sum_dog_nom', 'sum_dog_ekv', 'date_dogovor', 
        'date_factual', 'date_pogash', 'srok', 'dog_number_date', 'credit_procent', 
        'prosr_procent', 'ostatok_cred_schet', 'ostatok_peresm', 'date_prodl', 
        'date_pogash_posle_prodl', 'ostatok_prosr', 'date_obraz_pros', 'ostatok_sudeb', 
        'kod_pravoxr_org', 'priznak_resheniya', 'date_pred_resh', 'vsego_zadoljennost', 
        'class_kachestva', 'ostatok_rezerv', 'ostatok_nach_prcnt', 'ostatok_nach_prosr_prcnt', 
        'ocenka_obespecheniya', 'obespechenie', 'opisanie_obespechenie', 'istochnik sredtsvo', 
        'vid_kreditovaniya' , 'purpose_credit', 'vishest_org_client', 'otrasl_kreditovaniya', 
        'otrasl_clienta', 'class_kredit_spos', 'predsedatel_kb', 'adress_client', 'un_number_contract', 
        'inn_passport', 'ostatok_vneb_prosr', 'konkr_nazn_credit', 'borrower_type', 'svyazanniy', 
        'maliy_biznes', 'register_number', 'oked', 'code_contract']

    # data.columns = [
    #     'number', 'code_reg', 'mfo', 'rayon_podachi', 'name_client', 'balans_schet', 'credit_schet', 
    #     'date_resheniya', 'code_val', 'sum_dog_nom', 'sum_dog_ekv', 'date_dogovor', 
    #     'date_factual', 'date_pogash', 'srok', 'dog_number_date', 'credit_procent', 
    #     'prosr_procent', 'ostatok_cred_schet', 'ostatok_peresm', 'date_prodl', 
    #     'date_pogash_posle_prodl', 'ostatok_prosr', 'date_obraz_pros', 'ostatok_sudeb', 'date_sudeb',
    #     'kod_pravoxr_org', 'priznak_resheniya', 'date_pred_resh', 'vsego_zadoljennost', 
    #     'class_kachestva', 'ostatok_rezerv', 'ostatok_nach_prcnt', 'ostatok_nach_prosr_prcnt', 
    #     'ocenka_obespecheniya', 'obespechenie', 'opisanie_obespechenie', 'istochnik sredtsvo', 'zarubejniy_bank',
    #     'vid_kreditovaniya' , 'purpose_credit', 'vishest_org_client', 'otrasl_kreditovaniya', 
    #     'otrasl_clienta', 'class_kredit_spos', 'predsedatel_kb', 'adress_client', 'un_number_contract', 
    #     'inn_passport', 'ostatok_vneb_prosr', 'konkr_nazn_credit', 'borrower_type', 'svyazanniy', 
    #     'maliy_biznes', 'register_number', 'oked', 'code_contract']
    
    cursor = connection.cursor()
    cursor.execute("select NVL(max(id),0) from CREDITS_TEMPDATA")
    maxID = cursor.fetchone()[0]+1
    data.insert(0, 'MONTH_CODE', 4)
    data.insert(0, 'ID', range(maxID, maxID + len(data)))
    
        
    objs = []
    for index, row in data.iterrows():
        tmp = row
        objs.append(
            TempData.objects.create(
                id                  = row['ID'],
                MONTH_CODE          = row['MONTH_CODE'],
                NUMBERS             = row['number'],
                CODE_REG            = row['code_reg'], 
                MFO                 = row['mfo'],
                NAME_CLIENT         = row['name_client'], 
                BALANS_SCHET        = row['balans_schet'], 
                CREDIT_SCHET        = row['credit_schet'], 
                CODE_VAL            = row['code_val'],
                DATE_RESHENIYA      = row['date_resheniya'],
                SUM_DOG_NOM         = row['sum_dog_nom'], 
                SUM_DOG_EKV         = row['sum_dog_ekv'], 
                DATE_DOGOVOR        = row['date_dogovor'], 
                DATE_FACTUAL        = row['date_factual'], 
                DATE_POGASH         = row['date_pogash'], 
                SROK                = row['srok'],
                DOG_NUMBER_DATE     = row['dog_number_date'], 
                CREDIT_PROCENT      = row['credit_procent'],
                PROSR_PROCENT       = row['prosr_procent'], 
                OSTATOK_CRED_SCHET  = row['ostatok_cred_schet'],
                OSTATOK_PERESM      = row['ostatok_peresm'], 
                DATE_PRODL          = row['date_prodl'],
                DATE_POGASH_POSLE_PRODL = row['date_pogash_posle_prodl'],
                OSTATOK_PROSR       = row['ostatok_prosr'], 
                DATE_OBRAZ_PROS     = row['date_obraz_pros'], 
                OSTATOK_SUDEB       = row['ostatok_sudeb'],
                KOD_PRAVOXR_ORG     = row['kod_pravoxr_org'], 
                PRIZNAK_RESHENIYA   = row['priznak_resheniya'], 
                DATE_PRED_RESH      = row['date_pred_resh'], 
                VSEGO_ZADOLJENNOST  = row['vsego_zadoljennost'], 
                CLASS_KACHESTVA     = row['class_kachestva'], 
                OSTATOK_REZERV      = row['ostatok_rezerv'], 
                OSTATOK_NACH_PRCNT  = row['ostatok_nach_prcnt'], 
                OSTATOK_NACH_PROSR_PRCNT    = row['ostatok_nach_prosr_prcnt'], 
                OCENKA_OBESPECHENIYA        = row['ocenka_obespecheniya'], 
                OBESPECHENIE                = row['obespechenie'], 
                OPISANIE_OBESPECHENIE       = row['opisanie_obespechenie'],
                ISTOCHNIK_SREDTSVO          = row['istochnik sredtsvo'], 
                VID_KREDITOVANIYA           = row['vid_kreditovaniya'],  
                PURPOSE_CREDIT              = row['purpose_credit'], 
                VISHEST_ORG_CLIENT          = row['vishest_org_client'],
                OTRASL_KREDITOVANIYA        = row['otrasl_kreditovaniya'], 
                OTRASL_CLIENTA              = row['otrasl_clienta'], 
                CLASS_KREDIT_SPOS           = row['class_kredit_spos'], 
                PREDSEDATEL_KB              = row['predsedatel_kb'],
                ADRESS_CLIENT               = row['adress_client'], 
                UN_NUMBER_CONTRACT          = row['un_number_contract'], 
                INN_PASSPORT                = row['inn_passport'], 
                OSTATOK_VNEB_PROSR          = row['ostatok_vneb_prosr'], 
                KONKR_NAZN_CREDIT           = row['konkr_nazn_credit'],
                BORROWER_TYPE               = row['borrower_type'], 
                SVYAZANNIY                  = row['svyazanniy'], 
                MALIY_BIZNES                = row['maliy_biznes'], 
                REGISTER_NUMBER             = row['register_number'], 
                OKED                        = row['oked'],
                CODE_CONTRACT               = row['code_contract'],
                # RAYON_PODACHI               = row['rayon_podachi'],
                # DATE_SUDEB                  = row['date_sudeb'],
                # ZARUBEJNIY_BANK             = row['zarubejniy_bank']
            )
        )
        
    message = "<b>Result:</b><hr>"
    try:
       # TempData.objects.bulk_create(objs)
        message += "<pre>"
        message += "SUCCESS"
        message += "</pre>"
    except Exception as e:
        message += "<p>Ошибка</p><pre>"
        message += str(e)
        message += "</pre>"
    finally:
        message += "<hr><b>Тест закончен.</b><br><code>time: "
        end = datetime.now()
        tdelta = end - start
        minutes = tdelta.total_seconds() / 60
        message += '{:.4f} minutes'.format(minutes)
        
    return HttpResponse(message)

# Загрузка просрочки из Excel
def upload_prs(request):
    start = datetime.now()
    data = pd.read_excel(r'media/excel/april_overdue_percent.xlsx')

    data = data.fillna('')

    cursor = connection.cursor()
    cursor.execute("select NVL(max(id),0) from CREDITS_OVERDUEPERCENTS")
    maxID = cursor.fetchone()[0] + 1
    data.insert(0, 'ID', range(maxID, maxID + len(data)))
    report = ListReports.objects.get(id=4)
    objs = []
    for index, row in data.iterrows():
        objs.append(
            OverduePercents.objects.create(
                id=row['ID'],
                FilialCode=row['FILIAL_CODE'],
                LoanID=row['LOAN_ID'],
                AccountCode=row['ACCOUNT_CODE'],
                SaldoOut=row['SALDO_OUT'],
                ArrearDate=row['ARREAR_DATE'],
                DayCount=row['DAY_COUNT'],
                REPORT=report
            )
        )

    message = "<b>Result:</b><hr>"
    try:
        message += "<pre>"
        message += "SUCCESS"
        message += "</pre>"
    except Exception as e:
        message += "<p>Ошибка</p><pre>"
        message += str(e)
        message += "</pre>"
    finally:
        message += "<hr><b>Тест закончен.</b><br><code>time: "
        end = datetime.now()
        tdelta = end - start
        minutes = tdelta.total_seconds() / 60
        message += '{:.4f} minutes'.format(minutes)

    return HttpResponse(message)

# Загрузка платежи из Excel
def upload_payments(request):
    start = datetime.now()
    data = pd.read_excel(r'media/payments/july/hazorasp.xlsx',
                         dtype=str)

    data = data.fillna('')
    data.columns = [
        'code_reg', 'mfo', 'name_client', 'summa_credit', 'date_vidachi',
        'ostatok_nach_prcnt', 'kredit_schet', 'ostatok_scheta', 'date_pogash',
        'summa_pogash', 'prognoz_pogash', 'schet_prosr', 'ostatok_prosr',
        'code_val', 'vid_kreditovaniya', 'istochnik_kredit', 'unique_niki']

    cursor = connection.cursor()
    cursor.execute("select NVL(max(id),0) from CREDITS_TEMPDATA2")
    maxID = cursor.fetchone()[0] + 1
    data.insert(0, 'MONTH_CODE', 1)
    data.insert(0, 'ID', range(maxID, maxID + len(data)))

    objs = []
    for index, row in data.iterrows():
        objs.append(
            TempData2.objects.create(
                id=row['ID'],
                MONTH_CODE=row['MONTH_CODE'],
                CODE_REG=row['code_reg'],
                MFO=row['mfo'],
                NAME_CLIENT=row['name_client'],
                SUMMA_CREDIT=row['summa_credit'],
                DATE_VIDACHI=row['date_vidachi'],
                OSTATOK_NACH_PRCNT=row['ostatok_nach_prcnt'],
                KREDIT_SCHET=row['kredit_schet'],
                OSTATOK_SCHETA=row['ostatok_scheta'],
                DATE_POGASH=row['date_pogash'],
                SUMMA_POGASH=row['summa_pogash'],
                PROGNOZ_POGASH=row['prognoz_pogash'],
                SCHET_PROSR=row['schet_prosr'],
                OSTATOK_PROSR=row['ostatok_prosr'],
                CODE_VAL=row['code_val'],
                VID_KREDITOVANIYA=row['vid_kreditovaniya'],
                ISTOCHNIK_KREDIT=row['istochnik_kredit'],
                UNIQUE_NIKI=row['unique_niki']
            )
        )

    message = "<b>Result:</b><hr>"
    try:
        # TempData.objects.bulk_create(objs)
        message += "<pre>"
        message += "SUCCESS"
        message += "</pre>"
    except Exception as e:
        message += "<p>Ошибка</p><pre>"
        message += str(e)
        message += "</pre>"
    finally:
        message += "<hr><b>Тест закончен.</b><br><code>time: "
        end = datetime.now()
        tdelta = end - start
        minutes = tdelta.total_seconds() / 60
        message += '{:.4f} minutes'.format(minutes)

    return HttpResponse(message)
