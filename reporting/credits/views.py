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
        return HttpResponseRedirect(request.path_info)
    
    if 'data_month' not in request.session:
        request.session['data_month'] = '2020-04'      

def index(request):
    setReviewMonthInSession(request)

    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)

    cursor = connection.cursor()
    cursor.execute(Query.named_query_indicators(), {'month2':sMonth.month, 'month1':sMonth.month-1})
    data = [2]
    for row in CursorByName(cursor):
        data.append(row)

    
    
    gdpData = {}
    gdpName = {}

    if (request.GET.get('q')=='tox'):
        geoTitle = "Токсичные кредиты"
        geoData = DataByGeocode.objects.raw(Query.named_query_toxics_by_branches(), [report.id])
    elif (request.GET.get('q')=='prs'):
        geoTitle = "Просрочка"
        geoData = DataByGeocode.objects.raw(Query.named_query_overdues_by_branches(), [report.id])
    else:
        geoTitle = "NPL клиенты"
        geoData = DataByGeocode.objects.raw(Query.named_query_npls_by_branches(), [report.id])

    for p in geoData:
        gdpData[p.GeoCode] = int(p.Balance)
        gdpName[p.GeoCode] = p.Title
    

    statistics = {
        'portfolio_value'   : int(data[2]['CREDIT']/1000000),
        'portfolio_percent' : '{:.1%}'.format((data[2]['CREDIT'] - data[1]['CREDIT']) / data[2]['CREDIT']),
        'portfolio_growth'  : data[2]['CREDIT'] - data[1]['CREDIT'], 
        'npl_value'         : int(data[2]['NPL']/1000000),
        'npl_percent'       : '{:.1%}'.format((data[2]['NPL'] - data[1]['NPL']) / data[2]['NPL']),
        'npl_growth'        : data[2]['NPL'] - data[1]['NPL'], 
        'toxic_value'       : int(data[2]['TOXIC']/1000000),
        'toxic_percent'     : '{:.1%}'.format((data[2]['TOXIC'] - data[1]['TOXIC']) / data[2]['TOXIC']),
        'toxic_growth'      : data[2]['TOXIC'] - data[1]['TOXIC'],
        'overdue_value'     : int(data[2]['OVERDUE']/1000000),
        'overdue_percent'   : '{:.1%}'.format((data[2]['OVERDUE'] - data[1]['OVERDUE']) / data[2]['OVERDUE']),
        'overdue_growth'    : data[2]['OVERDUE'] - data[1]['OVERDUE'],
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
    table = NplClientsTable(NplClients.objects.raw(Query.named_query_npls(), [report.id])[:top])
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
    table = ToxicCreditsTable(ToxicCredits.objects.raw(Query.named_query_toxics(), [report.id])[:top])
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
    table = OverdueCreditsTable(OverdueCredits.objects.raw(Query.named_query_overdues(), [report.id])[:top])
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

    cursor = connection.cursor()
    cursor.execute(Query.named_query_indicators(), {'month2':sMonth.month, 'month1':sMonth.month-1})
    data = [2]
    for row in CursorByName(cursor):
        data.append(row)

    listCreditPortfolio = [
            {"name": "Кредитный портфель",          "old_value": data[1]['CREDIT'],         "new_value": data[2]['CREDIT']},
            {"name": "* NPL",                       "old_value": data[1]['NPL'],            "new_value": data[2]['NPL']},
            {"name": "Удельный вес к портфелю",     "old_value": data[1]['NPL_WEIGHT'],     "new_value": data[2]['NPL_WEIGHT'],     "flag": True},
            {"name": "** Токсичные кредиты",        "old_value": data[1]['TOXIC'],          "new_value": data[2]['TOXIC']},
            {"name": "Удельный вес к портфелю",     "old_value": data[1]['TOXIC_WEIGHT'],   "new_value": data[2]['TOXIC_WEIGHT'],   "flag": True},
            {"name": "Токсичные кредиты + NPL",     "old_value": data[1]['TOXIC_NPL'],      "new_value": data[2]['TOXIC_NPL']},
            {"name": "Резервы",                     "old_value": data[1]['RESERVE'],        "new_value": data[2]['RESERVE']},
            {"name": "Покрытие ТК+NPL резервами",   "old_value": data[1]['RESERVE_COATING'],"new_value": data[2]['RESERVE_COATING'],"flag": True},
            {"name": "Просроченная задолженность",  "old_value": data[1]['OVERDUE'],        "new_value": data[2]['OVERDUE']},
            {"name": "Удельный вес к портфелю",     "old_value": data[1]['OVERDUE_WEIGHT'], "new_value": data[2]['OVERDUE_WEIGHT'], "flag": True},
        ]
            
    for item in listCreditPortfolio:
        val1 = item['old_value']
        val2 = item['new_value']
        flag = 'flag' in item.keys()
        item['old_value']  = '{:.1%}'.format(val1) if flag else int(val1 / 1000000)
        item['new_value']  = '{:.1%}'.format(val2) if flag else int(val2 / 1000000)
        item['difference'] = int((val2 - val1) / 1000000) if not flag else ''
        item['percentage'] = '{:.1%}'.format((val2 - val1) / val2) if not flag else '' 
    
    table = OverallInfoTable(listCreditPortfolio)
    table.paginate(page=request.GET.get("page", 1), per_page=10)            
    
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

    data = ByTerms.objects.raw(Query.named_query_byterms(), [report.id, report.id])
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

    data = ByTerms.objects.raw(Query.named_query_bysubjects(), [report.id, report.id])
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

    data = ByTerms.objects.raw(Query.named_query_bysegments(), [report.id, report.id])
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
    data = ByTerms.objects.raw(Query.named_query_bycurrency(), [report.id, report.id])
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
    data = ByTerms.objects.raw(Query.named_query_bybranches(), [report.id, report.id])
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

def bypercentage_national(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)

    table = ByPercentageTable(ByPercentage.objects.raw(Query.named_query_bypercentage_national(), [report.id]))

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

    table = ByPercentageTable(ByPercentage.objects.raw(Query.named_query_bypercentage_foreign(), [report.id]))

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
    table = ByPercentageULTable(ByPercentageUL.objects.raw(Query.named_query_bypercentage_national_ul(), [report.id]))

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
    table = ByPercentageULTable(ByPercentageUL.objects.raw(Query.named_query_bypercentage_foreign_ul(), [report.id]))
    
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

    cursor = connection.cursor()
    cursor.execute(Query.named_query_byaverageweight_ul(), [report.id])
    data = [5]
    for row in CursorByName(cursor):
        data.append(row) 
    listData = data[1:]
    for item in listData:
        item['UZS_AVERAGE'] = '{:.2f}'.format(item['UZS_AVERAGE'])
        item['USD_AVERAGE'] = '{:.2f}'.format(item['USD_AVERAGE'])
        item['EUR_AVERAGE'] = '{:.2f}'.format(item['EUR_AVERAGE'])
        item['JPY_AVERAGE'] = '{:.2f}'.format(item['JPY_AVERAGE'])
    table = ByAverageULTable(listData)

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

    cursor = connection.cursor()
    cursor.execute(Query.named_query_byaverageweight_fl(), [report.id])
    data = [10]
    for row in CursorByName(cursor):
        data.append(row) 
    listData = data[1:]
    total_credit = sum(c['CREDIT'] for c in listData)
    total_loan   = sum(c['LOAN'] for c in listData)
    table = ByAverageFLTable(listData)

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

def byretailproduct(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    data = ByRetailProduct.objects.raw(Query.named_query_byretailproduct(), [report.id, report.id])
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

def export_all_tables(request):
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    cursor = connection.cursor()
   
    #NPLS
    cursor.execute(Query.named_query_npls(), [report.id])
    npl_data = []
    for row in CursorByName(cursor):
        npl_data.append(row)
    
    npls_df = pd.DataFrame(npl_data[1:])
    npls_df = npls_df.head(10)
    npls_df.drop(['id', 'Number', 'SDATE'], axis=1, inplace = True)
    npls_df.rename(columns={"Name": "Наименование клиента", "Branch": "Филиал", "Balans": "Остаток Кредита"}, inplace =True)

    #TOXIC
    cursor.execute(Query.named_query_toxics(), [report.id])
    toxic = []
    for row in CursorByName(cursor):
        toxic.append(row)
    toxic_df = pd.DataFrame(toxic[1:])
    toxic_df = toxic_df.head(10)
    toxic_df.drop(['id', 'Number', 'SDate'], axis=1, inplace = True)
    toxic_df.rename(columns={"Name": "Наименование клиента", "Branch": "Филиал", "Balans": "Остаток Кредита"}, inplace =True)

    #OVERDUE
    cursor.execute(Query.named_query_overdues(), [report.id])
    overdues = []
    for row in CursorByName(cursor):
        overdues.append(row)
    overdues_df = pd.DataFrame(overdues[1:])
    overdues_df = overdues_df.head(10)
    overdues_df.drop(['id', 'Number'], axis=1, inplace = True)
    overdues_df.rename(columns={"Name": "Наименование клиента", "Branch": "Филиал", "Balans": "Остаток Кредита"}, inplace =True)
    
    #BYTERM
    cursor.execute(Query.named_query_byterms(), [report.id, report.id])
    byterm = []
    for row in CursorByName(cursor):
        byterm.append(row)
    byterm_df = pd.DataFrame(byterm)
    byterm_df.drop(['id'], axis=1, inplace = True)
    byterm_df = byterm_df.pivot_table(index='Title',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    byterm_df = byterm_df.reset_index()

    byterm_df.rename(columns={"Title": "Сроки", "NplBalans": "NPL", "NplToxic": "ТК+NPL", "PorBalans": "Кредитный портфель", "PorPercent": "Доля %", 
                                 "ResBalans": "Резервы", "ToxBalans": "Токсичные кредиты"}, inplace =True)

    byterm_df = byterm_df.set_index('Сроки')
    new_index = ['свыше 10 лет', 'от 7-ми до 10 лет', 'от 5-ти до 7 лет', 'от 2-х до 5 лет', 'до 2-х лет', 'total']
    byterm_df = byterm_df.reindex(new_index)
    byterm_df = byterm_df.rename({'total': 'Итого:'}, axis='index')
    byterm_df = byterm_df.reset_index()
    byterm_df['Удельный вес к своему портфелю'] =(byterm_df['ТК+NPL'] / byterm_df['Кредитный портфель']* 100).round(1).astype('str') + '%'
    byterm_df['Покрытие ТК+NPL резервами'] = (byterm_df['Резервы'] / byterm_df['ТК+NPL'] * 100).round(1).astype('str') + '%'
    byterm_df = byterm_df[["Сроки", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    byterm_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = byterm_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].round(0)
    

    #BYSUBJECTS
    cursor.execute(Query.named_query_bysubjects(), [report.id, report.id])
    bysubjects = []
    for row in CursorByName(cursor):
        bysubjects.append(row)
    bysubjects_df = pd.DataFrame(bysubjects)
    bysubjects_df.drop(['id'], axis=1, inplace = True)
    bysubjects_df = bysubjects_df.pivot_table(index='Title',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bysubjects_df = bysubjects_df.reset_index()

    bysubjects_df.rename(columns={"Title": "Статус", "NplBalans": "NPL", "PorBalans": "Кредитный портфель", "PorPercent": "Доля %", 
                                 "ResBalans": "Резервы", "ToxBalans": "Токсичные кредиты"}, inplace =True)

    bysubjects_df = bysubjects_df.set_index('Статус')
    new_index = ['ЮЛ', 'ИП', 'ФЛ', 'total']
    bysubjects_df = bysubjects_df.reindex(new_index)
    bysubjects_df = bysubjects_df.rename({'total': 'Итого:'}, axis='index')
    bysubjects_df = bysubjects_df.reset_index()
    bysubjects_df['Доля %'] = (bysubjects_df['Кредитный портфель'] / bysubjects_df['Кредитный портфель'].iloc[-1] * 100 ).round(1).astype('str') + '%'
    bysubjects_df['ТК+NPL'] = bysubjects_df['NPL'] + bysubjects_df['Токсичные кредиты']
    bysubjects_df['Удельный вес к своему портфелю'] =(bysubjects_df['ТК+NPL'] / bysubjects_df['Кредитный портфель']* 100).round(1).astype('str') + '%'
    bysubjects_df['Покрытие ТК+NPL резервами'] = (bysubjects_df['Резервы'] / bysubjects_df['ТК+NPL'] * 100).round(1).astype('str') + '%'
    bysubjects_df = bysubjects_df[["Статус", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    bysubjects_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = bysubjects_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].round(0)

    #BYSEGMENTS
    cursor.execute(Query.named_query_bysegments(), [report.id, report.id])
    bysegments = []
    for row in CursorByName(cursor):
        bysegments.append(row)
    bysegments_df = pd.DataFrame(bysegments)
    bysegments_df.drop(['id'], axis=1, inplace = True)
    bysegments_df = bysegments_df.pivot_table(index='Title',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bysegments_df = bysegments_df.reset_index()

    bysegments_df.rename(columns={"Title": "Сегмент", "NplBalans": "NPL", "PorBalans": "Кредитный портфель", "PorPercent": "Доля %", 
                                "ResBalans": "Резервы", "ToxBalans": "Токсичные кредиты"}, inplace =True)

    bysegments_df = bysegments_df.set_index('Сегмент')
    new_index = ['Инвест. проекты', 'ЮЛ', 'РБ', 'total']
    bysegments_df = bysegments_df.reindex(new_index)
    bysegments_df = bysegments_df.rename({'total': 'Итого:'}, axis='index')
    bysegments_df = bysegments_df.reset_index()
    bysegments_df['Доля %'] = (bysubjects_df['Кредитный портфель'] / bysegments_df['Кредитный портфель'].iloc[-1] * 100 ).round(1).astype('str') + '%'
    bysegments_df['ТК+NPL'] = bysegments_df['NPL'] + bysegments_df['Токсичные кредиты']
    bysegments_df['Удельный вес к своему портфелю'] =(bysegments_df['ТК+NPL'] / bysegments_df['Кредитный портфель']* 100).round(1).astype('str') + '%'
    bysegments_df['Покрытие ТК+NPL резервами'] = (bysegments_df['Резервы'] / bysegments_df['ТК+NPL'] * 100).round(1).astype('str') + '%'
    bysegments_df = bysegments_df[["Сегмент", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    bysegments_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = bysegments_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].round(0)

    #BYCURRENCY
    cursor.execute(Query.named_query_bycurrency(), [report.id, report.id])
    bycurrency = []
    for row in CursorByName(cursor):
        bycurrency.append(row)
    bycurrency_df = pd.DataFrame(bycurrency)
    bycurrency_df.drop(['id'], axis=1, inplace = True)
    bycurrency_df = bycurrency_df.pivot_table(index='Title',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bycurrency_df = bycurrency_df.reset_index()

    bycurrency_df.rename(columns={"Title": "Валюты", "NplBalans": "NPL", "PorBalans": "Кредитный портфель", "PorPercent": "Доля %", 
                                "ResBalans": "Резервы", "ToxBalans": "Токсичные кредиты"}, inplace =True)

    bycurrency_df = bycurrency_df.set_index('Валюты')
    new_index = ['Национальная валюта', 'Иностранная валюта', 'total']
    bycurrency_df = bycurrency_df.reindex(new_index)
    bycurrency_df = bycurrency_df.rename({'total': 'Итого:'}, axis='index')
    bycurrency_df = bycurrency_df.reset_index()
    bycurrency_df['Доля %'] = (bycurrency_df['Кредитный портфель'] / bycurrency_df['Кредитный портфель'].iloc[-1] * 100 ).round(1).astype('str') + '%'
    bycurrency_df['ТК+NPL'] = bycurrency_df['NPL'] + bycurrency_df['Токсичные кредиты']
    bycurrency_df['Удельный вес к своему портфелю'] =(bycurrency_df['ТК+NPL'] / bycurrency_df['Кредитный портфель']* 100).round(1).astype('str') + '%'
    bycurrency_df['Покрытие ТК+NPL резервами'] = (bycurrency_df['Резервы'] / bycurrency_df['ТК+NPL'] * 100).round(1).astype('str') + '%'
    bycurrency_df = bycurrency_df[["Валюты", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    bycurrency_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = bycurrency_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].round(0)

    #BYBRANCHES
    cursor.execute(Query.named_query_bybranches(), [report.id, report.id])
    bybranches = []
    for row in CursorByName(cursor):
        bybranches.append(row)
    bybranches_df = pd.DataFrame(bybranches)
    bybranches_df.drop(['id'], axis=1, inplace = True)
    bybranches_df = bybranches_df.pivot_table(index='Title',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bybranches_df = bybranches_df.reset_index()

    bybranches_df.rename(columns={"Title": "Филиалы", "PorBalans": "Кредитный портфель", "PorPercent": "Доля %", "NplBalans": "NPL",   
                                  "ToxBalans": "Токсичные кредиты" , "ResBalans": "Резервы"}, inplace =True)
    bybranches_df = bybranches_df.set_index('Филиалы')
    bybranches_df = bybranches_df.rename({'total': 'Итого:'}, axis='index')
    bybranches_df = bybranches_df.reset_index()
    bybranches_df['Доля %'] = (bybranches_df['Кредитный портфель'] / bybranches_df['Кредитный портфель'].iloc[-1] * 100 ).round(1).astype('str') + '%'
    bybranches_df['ТК+NPL'] = bybranches_df['NPL'] + bybranches_df['Токсичные кредиты']
    bybranches_df['Удельный вес к своему портфелю'] =(bybranches_df['ТК+NPL'] / bybranches_df['Кредитный портфель']* 100).round(1).astype('str') + '%'
    bybranches_df['Покрытие ТК+NPL резервами'] = (bybranches_df['Резервы'] / bybranches_df['ТК+NPL'] * 100).round(1).astype('str') + '%'
    bybranches_df = bybranches_df[["Филиалы", 'Кредитный портфель', 'Доля %', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Удельный вес к своему портфелю', 'Резервы', 'Покрытие ТК+NPL резервами']]
    bybranches_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']] = bybranches_df[['Кредитный портфель', 'NPL', 'Токсичные кредиты', 'ТК+NPL', 'Резервы']].round(0)

    #BY NATIONAL PERCENTAGE 
    cursor.execute(Query.named_query_bypercentage_national(), [report.id])
    bypercentage_national = []
    for row in CursorByName(cursor):
        bypercentage_national.append(row)
    bypercentage_national_df = pd.DataFrame(bypercentage_national)
    bypercentage_national_df.drop(['id', 'Number'], axis=1, inplace = True)
    bypercentage_national_df = bypercentage_national_df.pivot_table(index='Title',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bypercentage_national_df = bypercentage_national_df.reset_index()

    bypercentage_national_df.rename(columns={"Title": "Коридор", "FLLongPart": "Доля % ФЛД", "FLLongTerm": "ФЛ-Долгосрочный", "FLShortPart": "Доля % ФЛК", 
                                 "FLShortTerm": "ФЛ-Краткосрочный", "ULLongPart": "Токсичные кредиты", 'ULLongTerm': 'ЮЛ-Долгосрочный', 
                                 'ULShortPart': 'Доля % ЮЛД', 'ULShortTerm':'ЮЛ-Краткосрочный'}, inplace =True)

    bypercentage_national_df = bypercentage_national_df[["Коридор", 'ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']]
    bypercentage_national_df = bypercentage_national_df.set_index('Коридор')
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
    bypercentage_national_df[['ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']] = bypercentage_national_df[['ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']].round(0)

    #BY FOREGIN PERCENTAGE
    cursor.execute(Query.named_query_bypercentage_foreign(), [report.id])
    bypercentage_foreign = []
    for row in CursorByName(cursor):
        bypercentage_foreign.append(row)
    bypercentage_foreign_df = pd.DataFrame(bypercentage_foreign)
    bypercentage_foreign_df.drop(['id', 'Number'], axis=1, inplace = True)
    bypercentage_foreign_df = bypercentage_foreign_df.pivot_table(index='Title',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bypercentage_foreign_df = bypercentage_foreign_df.reset_index()

    bypercentage_foreign_df.rename(columns={"Title": "Коридор", "FLLongPart": "Доля % ФЛД", "FLLongTerm": "ФЛ-Долгосрочный", "FLShortPart": "Доля % ФЛК", 
                                 "FLShortTerm": "ФЛ-Краткосрочный", "ULLongPart": "Токсичные кредиты", 'ULLongTerm': 'ЮЛ-Долгосрочный', 
                                 'ULShortPart': 'Доля % ЮЛД', 'ULShortTerm':'ЮЛ-Краткосрочный'}, inplace =True)

    bypercentage_foreign_df = bypercentage_foreign_df[["Коридор", 'ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']]
    bypercentage_foreign_df = bypercentage_foreign_df.set_index('Коридор')
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
    bypercentage_foreign_df[['ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']] = bypercentage_foreign_df[['ЮЛ-Долгосрочный', 'ЮЛ-Краткосрочный', 'ФЛ-Долгосрочный', 'ФЛ-Краткосрочный']].round(0)
    
    #В национальной валюте по ЮЛ (по срокам кредитов)                                                                              
    cursor.execute(Query.named_query_bypercentage_national_ul(), [report.id])
    bypercentage_national_ul = []
    for row in CursorByName(cursor):
        bypercentage_national_ul.append(row)
    bypercentage_national_ul_df = pd.DataFrame(bypercentage_national_ul)
    bypercentage_national_ul_df.drop(['id', 'Number'], axis=1, inplace = True)
    bypercentage_national_ul_df = bypercentage_national_ul_df.pivot_table(index='Title',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bypercentage_national_ul_df = bypercentage_national_ul_df.reset_index()

    bypercentage_national_ul_df.rename(columns={"Title": "Коридор", "Term1": "до 2-х лет", "Term2": "от 2-х до 5 лет", "Term3": "от 5-ти до 7 лет", 
                                 "Term4": "от 7-ми до 10 лет", "Term5": "свыше 10 лет"}, inplace =True)

    bypercentage_national_ul_df = bypercentage_national_ul_df.set_index('Коридор')
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

    #В иностранной  валюте по ЮЛ (по срокам кредитов)                                                                              
    cursor.execute(Query.named_query_bypercentage_foreign_ul(), [report.id])
    bypercentage_foreign_ul = []
    for row in CursorByName(cursor):
        bypercentage_foreign_ul.append(row)
    bypercentage_foreign_ul_df = pd.DataFrame(bypercentage_foreign_ul)
    bypercentage_foreign_ul_df.drop(['id', 'Number'], axis=1, inplace = True)
    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.pivot_table(index='Title',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc=sum)
    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.reset_index()

    bypercentage_foreign_ul_df.rename(columns={"Title": "Коридор", "Term1": "до 2-х лет", "Term2": "от 2-х до 5 лет", "Term3": "от 5-ти до 7 лет", 
                                 "Term4": "от 7-ми до 10 лет", "Term5": "свыше 10 лет"}, inplace =True)

    bypercentage_foreign_ul_df = bypercentage_foreign_ul_df.set_index('Коридор')
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
    cursor.execute(Query.named_query_byweight_ul(), [report.id])
    byweight_ul = []
    for row in CursorByName(cursor):
        byweight_ul.append(row)
    byaverageweight_ul_df = pd.DataFrame(byweight_ul)
    byaverageweight_ul_df['sum_credit'] = byaverageweight_ul_df['CREDIT_PROCENT'] * byaverageweight_ul_df['VSEGO_ZADOLJENNOST']
    by_sred_vzv_yur = pd.pivot_table(byaverageweight_ul_df, values='VSEGO_ZADOLJENNOST', index=['SROK'],
                    columns=['VALUTE'], aggfunc=np.sum, fill_value=0, margins= True)

    by_sred_vzv_yur2 = pd.pivot_table(byaverageweight_ul_df, values='sum_credit', index=['SROK'],
                    columns=['VALUTE'], aggfunc=np.sum, fill_value=0, margins= True)
    
    test = by_sred_vzv_yur2.div(by_sred_vzv_yur).reset_index()
    by_sred_vzv = pd.DataFrame(test.to_records())
    by_sred_vzv = by_sred_vzv.set_index('SROK')
    by_sred_vzv = by_sred_vzv.drop(['index', 'All'], axis=1)
    new_index = ['3-Долгосрочный', '1-Краткосрочный', 'All']
    by_sred_vzv = by_sred_vzv.reindex(new_index)
    by_sred_vzv = by_sred_vzv[['UZS', 'USD', 'EUR', 'JPY']]
    by_sred_vzv = by_sred_vzv.rename({'srok': 'Срок', 'All': 'Итого'}, axis='index')
    by_sred_vzv.index.names = ['Срок']
    by_sred_vzv = by_sred_vzv.fillna(0)
    by_sred_vzv = by_sred_vzv.round(2)
    by_sred_vzv = by_sred_vzv.rename(index={'3-Долгосрочный': 'Долгосрочные', '1-Краткосрочный' : 'Краткосрочные' })
    by_sred_vzv = by_sred_vzv.reset_index()

    #В разбивке по средневзвешенной процентной ставке (Юридические лица)                                                                             
    cursor.execute(Query.named_query_byweight_fl(), [report.id])
    byweight_fl = []
    for row in CursorByName(cursor):
        byweight_fl.append(row)
    byaverageweight_fl_df = pd.DataFrame(byweight_fl)
    byaverageweight_fl_df['sum_credit'] = byaverageweight_fl_df['CREDIT_PROCENT'] * byaverageweight_fl_df['VSEGO_ZADOLJENNOST']
    by_sred_vzv_fiz = pd.pivot_table(byaverageweight_fl_df, values='VSEGO_ZADOLJENNOST', index=['VID_KREDITOVANIYA'],
                    columns=['VALUTE'], aggfunc=np.sum, fill_value=0, margins= True)

    by_sred_vzv_fiz2 = pd.pivot_table(byaverageweight_fl_df, values='sum_credit', index=['VID_KREDITOVANIYA'],
                    columns=['VALUTE'], aggfunc=np.sum, fill_value=0, margins= True)
    
    by_sred_vzv_fiz = by_sred_vzv_fiz2.div(by_sred_vzv_fiz).reset_index()
    by_sred_vzv_fiz = pd.DataFrame(by_sred_vzv_fiz.to_records())
    by_sred_vzv_fiz = by_sred_vzv_fiz.set_index('VID_KREDITOVANIYA')
    by_sred_vzv_fiz = by_sred_vzv_fiz.drop(['index', 'All'], axis=1)
    by_sred_vzv_fiz.index.names = ['Продукты']
    new_index = ['32-Микрозаем', '59-Образовательный кредит', '54-Овердрафт по пластиковым карточкам физических лиц', '24-Ипотечный кредит',
                '33-Кредиты, выданные по инициативе банка', '30-Потребительский кредит', '34-Автокредит', '25-Микрокредит', 'All']
    by_sred_vzv_fiz = by_sred_vzv_fiz.reindex(new_index)
    by_sred_vzv_fiz = by_sred_vzv_fiz.rename(index= {'32-Микрозаем' : 'Микрозаем', '59-Образовательный кредит' : 'Образовательный кредит', '54-Овердрафт по пластиковым карточкам физических лиц': 'Овердрафт по пластиковым карточкам физических лиц', '24-Ипотечный кредит' : 'Ипотечный кредит',
                '33-Кредиты, выданные по инициативе банка' : 'Кредиты, выданные по инициативе банка', '30-Потребительский кредит' : 'Потребительский кредит', '34-Автокредит': 'Автокредит', '25-Микрокредит': 'Микрокредит', 'All':'Итого' })

    by_sred_vzv_fiz =by_sred_vzv_fiz.fillna(0)
    by_sred_vzv_fiz =by_sred_vzv_fiz.round(1)
    by_sred_vzv_fiz = by_sred_vzv_fiz.reset_index()

    dfs = {'Топ NPL': npls_df, 'Топ ТК': toxic_df, 'Топ проср': overdues_df, 'В разбивке по срокам': byterm_df, 
        'В разбивке по субъектам': bysubjects_df, 'В разбивке по сегментам':bysegments_df, 'В разбивке по валютам': bycurrency_df, 
        'В разбивке по филиалам':bybranches_df, 'В разбивке по проц став нац.в' : bypercentage_national_df, 
        'В разбивке по проц став инстр.в' : bypercentage_foreign_df, 'В национальной валюте по ЮЛ': bypercentage_national_ul_df,
        'В иностранной валюте по ЮЛ': bypercentage_foreign_ul_df, 'В разбивке по срднвзв прц ЮЛ': by_sred_vzv, 'В разбивке по срднвзв прц ФЛ': by_sred_vzv_fiz}
   
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

def contracts(request):
    setReviewMonthInSession(request)
    table = ContractListTable(ReportData.objects.raw(Query.named_query_contracts()))
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    context = {
        "page_title" : "Договора",
        "data_table" : table,
        "data_month" : request.session['data_month'],
        "contracts_page" : "active",

    }

    return render(request, 'credits/contract-list.html', context)

def contract_detail(request):
    setReviewMonthInSession(request)
    return render(request, 'credits/index.html')

def search(request):
    setReviewMonthInSession(request)
    return render(request, 'credits/index.html')

def upload(request):
    c = ListReports.objects.create(REPORT_TITLE="JANUARY, 2020", REPORT_MONTH=1, REPORT_YEAR=2020, DATE_CREATED=datetime.now())
    
    data = pd.read_excel (r'media/excel/january.xlsx', 
        dtype={"NN":'int32', "МФО": 'str', 'КодРег': 'str', 'БалансСчет':'str', 'КодВал': 'str', 'ИНН/Паспорт': 'str'})
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
    
    #data = data[:]
    for index, row in data.iterrows():
        
        ReportData.objects.create(
            NUMBER = number_check(row['number']),
            CODE_REG = row['code_reg'], 
            MFO = row['mfo'],
            NAME_CLIENT = row['name_client'], 
            BALANS_SCHET = row['balans_schet'], 
            CREDIT_SCHET = row['credit_schet'], 
            CODE_VAL= row['code_val'],
            DATE_RESHENIYA= row['date_resheniya'],
            SUM_DOG_NOM = number_check(row['sum_dog_nom']), 
            SUM_DOG_EKV = number_check(row['sum_dog_ekv']), 
            DATE_DOGOVOR = date_check(row['date_dogovor']), 
            DATE_FACTUAL = date_check(row['date_factual']), 
            DATE_POGASH = date_check(row['date_pogash']), 
            SROK = row['srok'],
            DOG_NUMBER_DATE = row['dog_number_date'], 
            CREDIT_PROCENT= number_check(row['credit_procent']),
            PROSR_PROCENT = number_check(row['prosr_procent']), 
            OSTATOK_CRED_SCHET= number_check(row['ostatok_cred_schet']),
            OSTATOK_PERESM = number_check(row['ostatok_peresm']), 
            DATE_PRODL= row['date_prodl'],
            DATE_POGASH_POSLE_PRODL= date_check(row['date_pogash_posle_prodl']),
            OSTATOK_PROSR = number_check(row['ostatok_prosr']), 
            DATE_OBRAZ_PROS = date_check(row['date_obraz_pros']), 
            OSTATOK_SUDEB = number_check(row['ostatok_sudeb']),
            KOD_PRAVOXR_ORG = row['kod_pravoxr_org'], 
            PRIZNAK_RESHENIYA = row['priznak_resheniya'], 
            DATE_PRED_RESH = row['date_pred_resh'], 
            VSEGO_ZADOLJENNOST = number_check(row['vsego_zadoljennost']), 
            CLASS_KACHESTVA = row['class_kachestva'], 
            OSTATOK_REZERV = number_check(row['ostatok_rezerv']), 
            OSTATOK_NACH_PRCNT = number_check(row['ostatok_nach_prcnt']), 
            OSTATOK_NACH_PROSR_PRCNT = number_check(row['ostatok_nach_prosr_prcnt']), 
            OCENKA_OBESPECHENIYA = number_check(row['ocenka_obespecheniya']), 
            OBESPECHENIE = row['obespechenie'], 
            OPISANIE_OBESPECHENIE= row['opisanie_obespechenie'],
            ISTOCHNIK_SREDTSVO = row['istochnik sredtsvo'], 
            VID_KREDITOVANIYA  = row['vid_kreditovaniya'],  
            PURPOSE_CREDIT = row['purpose_credit'], 
            VISHEST_ORG_CLIENT= row['vishest_org_client'],
            OTRASL_KREDITOVANIYA = row['otrasl_kreditovaniya'], 
            OTRASL_CLIENTA = row['otrasl_clienta'], 
            CLASS_KREDIT_SPOS = row['class_kredit_spos'], 
            PREDSEDATEL_KB= row['predsedatel_kb'],
            ADRESS_CLIENT = row['adress_client'], 
            UN_NUMBER_CONTRACT = row['un_number_contract'], 
            INN_PASSPORT = row['inn_passport'], 
            OSTATOK_VNEB_PROSR = number_check(row['ostatok_vneb_prosr']), 
            KONKR_NAZN_CREDIT= row['konkr_nazn_credit'],
            BORROWER_TYPE = row['borrower_type'], 
            SVYAZANNIY = number_check(row['svyazanniy']), 
            MALIY_BIZNES = number_check(row['maliy_biznes']), 
            REGISTER_NUMBER = row['register_number'], 
            OKED = row['oked'],
            CODE_CONTRACT = row['code_contract'],
            REPORT=c)

def test_export(request):
    if (request.POST.get('data_month')):
        request.session['data_month'] = request.POST.get('data_month')
    
    if 'data_month' not in request.session:
        request.session['data_month'] = '2020-04'

    date = pd.to_datetime(request.session['data_month'])
    yearValue = date.year
    monthCode = date.month

    cursor = connection.cursor()
    cursor.execute(Query.named_query_indicators(), {'month2':monthCode, 'month1':monthCode-1})
    data = [2]
    for row in CursorByName(cursor):
        data.append(row)

    listCreditPortfolio = [
            {"name": "Кредитный портфель",          "old_value": data[1]['CREDIT'],         "new_value": data[2]['CREDIT']},
            {"name": "* NPL",                       "old_value": data[1]['NPL'],            "new_value": data[2]['NPL']},
            {"name": "Удельный вес к портфелю",     "old_value": data[1]['NPL_WEIGHT'],     "new_value": data[2]['NPL_WEIGHT']},
            {"name": "** Токсичные кредиты",        "old_value": data[1]['TOXIC'],          "new_value": data[2]['TOXIC']},
            {"name": "Удельный вес к портфелю",     "old_value": data[1]['TOXIC_WEIGHT'],   "new_value": data[2]['TOXIC_WEIGHT']},
            {"name": "Токсичные кредиты + NPL",     "old_value": data[1]['TOXIC_NPL'],      "new_value": data[2]['TOXIC_NPL']},
            {"name": "Резервы",                     "old_value": data[1]['RESERVE'],        "new_value": data[2]['RESERVE']},
            {"name": "Покрытие ТК+NPL резервами",   "old_value": data[1]['RESERVE_COATING'],"new_value": data[2]['RESERVE_COATING']},
            {"name": "Просроченная задолженность",  "old_value": data[1]['OVERDUE'],        "new_value": data[2]['OVERDUE']},
            {"name": "Удельный вес к портфелю",     "old_value": data[1]['OVERDUE_WEIGHT'], "new_value": data[2]['OVERDUE_WEIGHT']},
        ]
            
    for item in listCreditPortfolio:
        val1 = item['old_value']
        val2 = item['new_value']
        flag = 'flag' in item.keys()
        item['old_value']  = '{:.1%}'.format(val1) if flag else int(val1 / 1000000)
        item['new_value']  = '{:.1%}'.format(val2) if flag else int(val2 / 1000000)
        item['difference'] = int((val2 - val1) / 1000000) if not flag else ''
        item['percentage'] = '{:.1%}'.format((val2 - val1) / val2) if not flag else '' 

    df = pd.DataFrame(listCreditPortfolio)
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        writer.close()
        response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
        response["Content-Disposition"] = 'attachment; filename="Indicators.xlsx"'
        return response

def client_page(request):
    setReviewMonthInSession(request)
    return render(request, 'credits/client_page.html')
