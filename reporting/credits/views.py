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

    
    
    gdpData = [],
    
    gdp = DataByGeocode.objects.raw(Query.named_query_npls_by_branches(), [report.id])

    for c in gdp:
        gdpData.append(c)
    

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
        "gdpData": json.dumps(gdpData)
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
    
    cursor.execute(Query.named_query_npls(), [report.id])
    data = []
    for row in CursorByName(cursor):
        data.append(row)
    
    df = pd.DataFrame(data[1:])
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        writer.close()
        response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
        response["Content-Disposition"] = 'attachment; filename="Indicators.xlsx"'
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
