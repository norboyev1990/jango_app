from django_tables2 import SingleTableView
from .functions import CursorByName
from .queries import Query
from .tables import *
from django.shortcuts import render
from .models import *
from django.db import connection
import pandas as pd
from pandas import DataFrame
import numpy as np
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from io import BytesIO
from openpyxl import *
# Create your views here.

def setReviewMonthInSession(request):
    if (request.POST.get('data_month')):
        request.session['data_month'] = request.POST.get('data_month')
        return HttpResponseRedirect(request.path_info)
    
    if 'data_month' not in request.session:
        request.session['data_month'] = '2020-04'

def index(request):
    setReviewMonthInSession(request)

    date = pd.to_datetime(request.session['data_month'])
    yearValue = date.year
    monthCode = date.month

    cursor = connection.cursor()
    cursor.execute(Query.named_query_indicators(), {'month2':monthCode, 'month1':monthCode-1})
    data = [2]
    for row in CursorByName(cursor):
        data.append(row)

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
        "npls_page": "active"
    }

    return render(request, 'credits/index.html', context)

def npls(request): 
    
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    
    table = NplClientsTable(NplClients.objects.raw(Query.named_query_npls(), [report.id]))
    table.paginate(page=request.GET.get("page", 1), per_page=10)            

    context = {
        "page_title": "NPL кредиты",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "npls_page": "active"
    }

    return render(request, 'credits/view.html', context)

def toxics(request):

    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)

    table = ToxicCreditsTable(ToxicCredits.objects.raw(Query.named_query_toxics(), [report.id]))
    table.paginate(page=request.GET.get("page", 1), per_page=10)            

    context = {
        "page_title": "Токсичные кредиты",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "toxics_page" : "active"
    }

    return render(request, 'credits/view.html', context)

def overdues(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])
    report = ListReports.objects.get(REPORT_MONTH=sMonth.month, REPORT_YEAR=sMonth.year)
    
    table = OverdueCreditsTable(OverdueCredits.objects.raw(Query.named_query_overdues(), [report.id]))
    table.paginate(page=request.GET.get("page", 1), per_page=10)            

    context = {
        "page_title": "Просроченные кредиты",
        "data_table": table,
        "data_month": sMonth.strftime('%Y-%m'),
        "overdues_page": "active"
    }

    return render(request, 'credits/view.html', context)

def indicators(request):
    setReviewMonthInSession(request)
    date = pd.to_datetime(request.session['data_month'])
    yearValue = date.year
    monthCode = date.month

    cursor = connection.cursor()
    cursor.execute(Query.named_query_indicators(), {'month2':monthCode, 'month1':monthCode-1})
    data = [2]
    for row in CursorByName(cursor):
        data.append(row)
    
    column_date1 = date.strftime("%d.%m.%Y")
    column_date2 = date.strftime("%d.%m.%Y")
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
    # table.set_column_title(_column_name='old_value', _column_new_name=column_date1)
    # table.set_column_title(_column_name='new_value', _column_new_name=column_date2)
    table.paginate(page=request.GET.get("page", 1), per_page=10)            

    context = {
        "page_title": "Общие показатели",
        "data_table": table,
        "data_month": request.session['data_month'],
        "indicators_page": "active"
    }

    return render(request, 'credits/view.html', context)

def byterms(request):
    setReviewMonthInSession(request)
    cursor = connection.cursor()
    cursor.execute(Query.named_query_indicators())
    data = [2]
    for row in CursorByName(cursor):
        data.append(row)

    context = {
        "page_title": "В разбивке по срокам",
        "data_table": table,
        "data_month": request.session['data_month'],
        "byterms_page": "active"
    }

    return render(request, 'credits/view.html', context)

def bysubjects(request):
    setReviewMonthInSession(request)
    cursor = connection.cursor()
    cursor.execute(Query.named_query_bysubjects())
    
    listBySubject = [5]
    for row in CursorByName(cursor):
        row['LOAN']     = int(row['LOAN'])
        row['RATION']   = '{:.1%}'.format(row['RATION'])
        row['NPL_LOAN'] = int(row['NPL_LOAN'])
        row['TOX_LOAN'] = int(row['TOX_LOAN'])
        row['TOX_NPL']  = int(row['TOX_NPL'])
        row['WEIGHT']   = '{:.1%}'.format(row['WEIGHT'])
        row['RESERVE']  = int(row['RESERVE'])
        row['COATING']  = '{:.1%}'.format(row['COATING'])
        listBySubject.append(row) 
        
    total = {}
    total['TITLE']    = 'Итого'
    total['LOAN']       = sum(c['LOAN'] for c in listBySubject[1:6])
    total['RATION']     = '100%' 
    total['NPL_LOAN']   = sum(c['NPL_LOAN'] for c in listBySubject[1:6]) 
    total['TOX_LOAN']   = sum(c['TOX_LOAN'] for c in listBySubject[1:6]) 
    total['TOX_NPL']    = sum(c['TOX_NPL'] for c in listBySubject[1:6]) 
    total['WEIGHT']     = '{:.1%}'.format(total['TOX_NPL']/total['LOAN']) 
    total['RESERVE']    = sum(c['RESERVE'] for c in listBySubject[1:6]) 
    total['COATING']    = '{:.1%}'.format(total['RESERVE']/total['TOX_NPL']) 
    listBySubject.append(total)

    table = BySubjectTable(listBySubject[1:])
    table.paginate(page=request.GET.get("page", 1), per_page=10)

    context = {
        "page_title": "В разбивке по субъектам",
        "data_table": table,
        "data_month": request.session['data_month'],
        "bysubjects_page": "active"
    }

    return render(request, 'credits/view.html', context)

def bysegments(request):
    setReviewMonthInSession(request)
    cursor = connection.cursor()
    cursor.execute(Query.named_query_bysegments())
    listBySegment = [5]
    for row in CursorByName(cursor):
        row['LOAN']     = int(row['LOAN'])
        row['RATION']   = '{:.1%}'.format(row['RATION'])
        row['NPL_LOAN'] = int(row['NPL_LOAN'])
        row['TOX_LOAN'] = int(row['TOX_LOAN'])
        row['TOX_NPL']  = int(row['TOX_NPL'])
        row['WEIGHT']   = '{:.1%}'.format(row['WEIGHT'])
        row['RESERVE']  = int(row['RESERVE'])
        row['COATING']  = '{:.1%}'.format(row['COATING'])
        listBySegment.append(row) 
    
    total = {}
    total['TITLE']      = 'Итого'
    total['LOAN']       = sum(c['LOAN'] for c in listBySegment[1:])
    total['RATION']     = '100%' 
    total['NPL_LOAN']   = sum(c['NPL_LOAN'] for c in listBySegment[1:]) 
    total['TOX_LOAN']   = sum(c['TOX_LOAN'] for c in listBySegment[1:]) 
    total['TOX_NPL']    = sum(c['TOX_NPL'] for c in listBySegment[1:]) 
    total['WEIGHT']     = '{:.1%}'.format(total['TOX_NPL']/total['LOAN']) 
    total['RESERVE']    = sum(c['RESERVE'] for c in listBySegment[1:]) 
    total['COATING']    = '{:.1%}'.format(total['RESERVE']/total['TOX_NPL']) 
    listBySegment.append(total)

    table = BySubjectTable(listBySegment[1:])
    context = {
        "page_title": "В разбивке по сегментам",
        "data_table": table,
        "data_month": request.session['data_month'],
        "bysegments_page": "active"
    }

    return render(request, 'credits/view.html', context)

def bycurrency(request):
    setReviewMonthInSession(request)
    cursor = connection.cursor()
    cursor.execute(Query.named_query_bycurrency())

    listByCurrency = [5]
    for row in CursorByName(cursor):
        row['LOAN']     = int(row['LOAN'])
        row['RATION']   = '{:.1%}'.format(row['RATION'])
        row['NPL_LOAN'] = int(row['NPL_LOAN'])
        row['TOX_LOAN'] = int(row['TOX_LOAN'])
        row['TOX_NPL']  = int(row['TOX_NPL'])
        row['WEIGHT']   = '{:.1%}'.format(row['WEIGHT'])
        row['RESERVE']  = int(row['RESERVE'])
        row['COATING']  = '{:.1%}'.format(row['COATING'])
        listByCurrency.append(row) 
    
    total = {}
    total['TITLE']      = 'Итого'
    total['LOAN']       = sum(c['LOAN'] for c in listByCurrency[1:])
    total['RATION']     = '100%' 
    total['NPL_LOAN']   = sum(c['NPL_LOAN'] for c in listByCurrency[1:]) 
    total['TOX_LOAN']   = sum(c['TOX_LOAN'] for c in listByCurrency[1:]) 
    total['TOX_NPL']    = sum(c['TOX_NPL'] for c in listByCurrency[1:]) 
    total['WEIGHT']     = '{:.1%}'.format(total['TOX_NPL']/total['LOAN']) 
    total['RESERVE']    = sum(c['RESERVE'] for c in listByCurrency[1:]) 
    total['COATING']    = '{:.1%}'.format(total['RESERVE']/total['TOX_NPL']) 
    listByCurrency.append(total)

    table = BySubjectTable(listByCurrency[1:])

    context = {
        "page_title": "В разбивке по валютам",
        "data_table": table,
        "data_month": request.session['data_month'],
        "bycurrency_page": "active"
    }

    return render(request, 'credits/view.html', context)

def bybranches(request):
    setReviewMonthInSession(request)
    cursor = connection.cursor()
    cursor.execute(Query.named_query_bybranches())
    listBySegment = [24]
    for row in CursorByName(cursor):
        row['LOAN']     = int(row['LOAN'])
        row['RATION']   = '{:.1%}'.format(row['RATION'])
        row['NPL_LOAN'] = int(row['NPL_LOAN'])
        row['TOX_LOAN'] = int(row['TOX_LOAN'])
        row['TOX_NPL']  = int(row['TOX_NPL'])
        row['WEIGHT']   = '{:.1%}'.format(row['WEIGHT'])
        row['RESERVE']  = int(row['RESERVE'])
        row['COATING']  = '{:.1%}'.format(row['COATING'])
        listBySegment.append(row) 
    
    total = {}
    total['TITLE']      = 'Итого'
    total['LOAN']       = sum(c['LOAN'] for c in listBySegment[1:])
    total['RATION']     = '100%' 
    total['NPL_LOAN']   = sum(c['NPL_LOAN'] for c in listBySegment[1:]) 
    total['TOX_LOAN']   = sum(c['TOX_LOAN'] for c in listBySegment[1:]) 
    total['TOX_NPL']    = sum(c['TOX_NPL'] for c in listBySegment[1:]) 
    total['WEIGHT']     = '{:.1%}'.format(total['TOX_NPL']/total['LOAN']) 
    total['RESERVE']    = sum(c['RESERVE'] for c in listBySegment[1:]) 
    total['COATING']    = '{:.1%}'.format(total['RESERVE']/total['TOX_NPL']) 
    listBySegment.append(total)

    table = BySubjectTable(listBySegment[1:])
    # table.paginate(page=request.GET.get("page", 1), per_page=10)
    context = {
        "page_title" : "В разбивке по филиалам",
        "data_table" : table,
        "data_month" : request.session['data_month'],
        "bybranches_page" : "active"
    }

    return render(request, 'credits/view.html', context)

def bypercentage(request):
    setReviewMonthInSession(request)
    cursor = connection.cursor()
    cursor.execute(Query.named_query_bypercentage_national())

    data = [24]
    for row in CursorByName(cursor):
        data.append(row) 
    
    listData = data[1:]

    total_ull = sum(c['ULL_LOAN'] for c in listData)
    total_uls = sum(c['ULS_LOAN'] for c in listData)
    total_fll = sum(c['FLL_LOAN'] for c in listData)
    total_fls = sum(c['FLS_LOAN'] for c in listData)

    for item in listData:
        item['ULL_LOAN'] = int(item['ULL_LOAN'])
        item['ULS_LOAN'] = int(item['ULS_LOAN'])
        item['FLL_LOAN'] = int(item['FLL_LOAN'])
        item['FLS_LOAN'] = int(item['FLS_LOAN'])
        item['ULL_PERCENT'] = '{:.1%}'.format(item['ULL_LOAN']/total_ull) if not (total_ull == 0) else '0,0%'
        item['ULS_PERCENT'] = '{:.1%}'.format(item['ULS_LOAN']/total_uls) if not (total_uls == 0) else '0,0%'
        item['FLL_PERCENT'] = '{:.1%}'.format(item['FLL_LOAN']/total_fll) if not (total_fll == 0) else '0,0%'
        item['FLS_PERCENT'] = '{:.1%}'.format(item['FLS_LOAN']/total_fls) if not (total_fls == 0) else '0,0%'

    total = {
        'TITLE':        'Итого',
        'ULL_LOAN':     int(total_ull),
        'ULS_LOAN':     int(total_uls),
        'FLL_LOAN':     int(total_fll),
        'FLS_LOAN':     int(total_fls),
        'ULL_PERCENT':  '100%' if not (total_ull == 0) else '0,0%',
        'ULS_PERCENT':  '100%' if not (total_uls == 0) else '0,0%',
        'FLL_PERCENT':  '100%' if not (total_fll == 0) else '0,0%',
        'FLS_PERCENT':  '100%' if not (total_fls == 0) else '0,0%'
    }

    listData.append(total)

    table = ByPercentageTable(listData)

    context = {
        "page_title" : "В разбивке по процентной ставке",
        "data_table" : table,
        "data_month" : request.session['data_month'],
        "bypercentage_page" : "active"
    }

    return render(request, 'credits/view.html', context)

def byaverageweight(request):
    setReviewMonthInSession(request)
    cursor = connection.cursor()
    cursor.execute(Query.named_query_byaverageweight_ul())
    
    data = [24]
    for row in CursorByName(cursor):
        data.append(row) 
    
    listData = data[1:]

    for item in listData:
        item['UZS_AVERAGE'] = '{:.2f}'.format(item['UZS_AVERAGE'])
        item['USD_AVERAGE'] = '{:.2f}'.format(item['USD_AVERAGE'])
        item['EUR_AVERAGE'] = '{:.2f}'.format(item['EUR_AVERAGE'])
        item['JPY_AVERAGE'] = '{:.2f}'.format(item['JPY_AVERAGE'])

    table = ByAverageULTable(listData)

    context = {
        "page_title" : "В разбивке по средневзвешенной процентной ставке",
        "data_table" : table,
        "data_month" : request.session['data_month'],
        "byaverageweight_page" : "active"
    }

    return render(request, 'credits/view.html', context)

def byretailproduct(request):
    setReviewMonthInSession(request)
    return render(request, 'credits/index.html')

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

def portfolio(request):
    if (request.POST.get('month_review')):
        request.session['month_review'] = request.POST.get('month_review')
    if 'month_review' not in request.session:
        request.session['month_review'] = 'June, 2020' 

    if (request.GET.get('q') == 'toxic'):
        page_title = 'Топ 10 токсичные кредиты'
        query = '''SELECT R.id, 
                        SUBSTR(CREDIT_SCHET,10,8) AS UNIQUE_CODE, 
                        COUNT(*),
                        NAME_CLIENT AS BORROWER,
                        B.NAME AS BRANCH_NAME,
                        ROUND(SUM(VSEGO_ZADOLJENNOST)/1000000, 2) AS LOAN_BALANCE,
                        JULIANDAY('2020-02-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) AS DAY_COUNT,
                        SUM(OSTATOK_SUDEB) AS SUDEB,
                        SUM(OSTATOK_VNEB_PROSR) AS PROSR,
                        SUM(OSTATOK_PERESM) AS PERESM
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                    WHERE R.REPORT_ID = 82
                    GROUP BY UNIQUE_CODE, NAME_CLIENT
                    HAVING PERESM IS NOT NULL and (DAY_COUNT < 90 or DAY_COUNT IS NULL)  and PROSR IS NULL and SUDEB IS NULL
                    ORDER BY LOAN_BALANCE DESC
                    LIMIT 10
                '''
    elif (request.GET.get('q') == 'prosr'):
        page_title = 'Топ 10 просроченные кредиты'
        query = '''SELECT R.id, 
                        CASE T.SUBJ
                            WHEN 'J' THEN SUBSTR(CREDIT_SCHET,10,8)
                            ELSE SUBSTR(INN_PASSPORT,11,9)
                        END	AS UNIQUE_CODE,
                        NAME_CLIENT AS BORROWER,
                        B.NAME AS BRANCH_NAME,
                        ROUND(SUM(OSTATOK_NACH_PROSR_PRCNT)/1000000, 2) AS LOAN_BALANCE
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                    WHERE REPORT_id = 82
                    GROUP BY UNIQUE_CODE
                    ORDER BY LOAN_BALANCE DESC
                    LIMIT 10
                '''
    elif (request.GET.get('q') == 'overall'):
        page_title = 'Общие показатели'
        cursor = connection.cursor()
        cursor.execute('''WITH NPL_VIEW (REPORT_MONTH, SUMMA_NPL) AS (
                                SELECT REPORT_MONTH, SUM(LOAN_BALANCE) FROM (
                                    SELECT 
                                        L.REPORT_MONTH,
                                        CASE T.SUBJ WHEN 'J' THEN SUBSTR(CREDIT_SCHET,10,8) ELSE SUBSTR(INN_PASSPORT,11,9) END	AS UNIQUE_CODE,
                                        JULIANDAY(DATE('now','start of year','+'||(L.REPORT_MONTH-1)||' month')) - JULIANDAY(MIN(R.DATE_OBRAZ_PROS)) AS DAY_COUNT,
                                        SUM(VSEGO_ZADOLJENNOST) AS LOAN_BALANCE
                                    FROM CREDITS_REPORTDATA R
                                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                    LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                                    LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                                    WHERE L.REPORT_MONTH in (4,3)
                                    GROUP BY L.REPORT_MONTH, UNIQUE_CODE
                                    HAVING DAY_COUNT > 90 OR SUM(OSTATOK_SUDEB) IS NOT NULL OR SUM(OSTATOK_VNEB_PROSR) IS NOT NULL
                                )
                                GROUP BY REPORT_MONTH
                            ),
                            
                            TOXIC_VIEW (REPORT_MONTH, SUMMA_TOXIC) AS (
                                SELECT REPORT_MONTH, SUM(LOAN_BALANCE) FROM (
                                    SELECT
                                        L.REPORT_MONTH,
                                        CASE T.SUBJ WHEN 'J' THEN SUBSTR(R.CREDIT_SCHET,10,8) ELSE SUBSTR(R.INN_PASSPORT,11,9) END AS UNIQUE_CODE,
                                        JULIANDAY(DATE('now','start of year','+'||(L.REPORT_MONTH-1)||' month')) - JULIANDAY(MIN(R.DATE_OBRAZ_PROS)) AS DAY_COUNT,
                                        SUM(R.VSEGO_ZADOLJENNOST) AS LOAN_BALANCE
                                    FROM CREDITS_REPORTDATA R
                                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                    LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                                    WHERE L.REPORT_MONTH in (4,3)
                                    GROUP BY L.REPORT_MONTH, UNIQUE_CODE
                                    HAVING SUM(R.OSTATOK_PERESM) IS NOT NULL AND (DAY_COUNT < 90 OR DAY_COUNT IS NULL)  
                                    AND SUM(R.OSTATOK_VNEB_PROSR) IS NULL AND SUM(R.OSTATOK_SUDEB) IS NULL
                                )
                                GROUP BY REPORT_MONTH
                            )
                        SELECT RD.id, 
                            L.REPORT_MONTH, 
                            SUM(VSEGO_ZADOLJENNOST)                 AS CREDIT,
                            N.SUMMA_NPL                             AS NPL, 
                            N.SUMMA_NPL / SUM(VSEGO_ZADOLJENNOST)   AS NPL_WEIGHT,
                            T.SUMMA_TOXIC                           AS TOXIC,
                            T.SUMMA_TOXIC / SUM(VSEGO_ZADOLJENNOST) AS TOXIC_WEIGHT,
                            T.SUMMA_TOXIC + N.SUMMA_NPL             AS TOXIC_NPL,
                            SUM(OSTATOK_REZERV)                     AS RESERVE,
                            SUM(OSTATOK_REZERV) / (T.SUMMA_TOXIC + N.SUMMA_NPL) AS RESERVE_COATING,
                            SUM(OSTATOK_PROSR)                      AS OVERDUE,
                            SUM(OSTATOK_PROSR) / SUM(VSEGO_ZADOLJENNOST) AS OVERDUE_WEIGHT
                        FROM CREDITS_REPORTDATA RD
                        LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = RD.REPORT_ID
                        LEFT JOIN NPL_VIEW N ON N.REPORT_MONTH = L.REPORT_MONTH
                        LEFT JOIN TOXIC_VIEW T ON T.REPORT_MONTH = L.REPORT_MONTH
                        WHERE L.REPORT_MONTH in (4,3)
                        GROUP BY L.REPORT_MONTH''')
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
        context = {'table': table, 'page_title': page_title}
        return render(request, 'credits/portfolio.html', context)
    elif (request.GET.get('q') == 'by_term'):
        page_title = 'В разбивке по срокам'
        cursor = connection.cursor()
        cursor.execute('''WITH MYVIEW (ID, TERM, VSEGO_ZADOLJENNOST) AS (
                            SELECT ID,
                            CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                                THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                END	AS TERM,
                                VSEGO_ZADOLJENNOST
                            FROM credits_reportdata
                            WHERE REPORT_id = 86
                        )
                            
                        SELECT 
                            CASE WHEN TERM <= 2 THEN '1_GROUP_2'
                                WHEN TERM > 2 AND TERM <= 5 THEN '2_GROUP_2_5'
                                WHEN TERM > 5 AND TERM <= 7 THEN '3_GROUP_5_7'
                                WHEN TERM > 7 AND TERM <= 10 THEN '4_GROUP_7_10'
                                ELSE '5_GROUP_10' END AS GROUPS,
                            COUNT(ID) AS COUNT,
                            ROUND(SUM(VSEGO_ZADOLJENNOST)/1000000, 0) AS SUMMA	
                        FROM MYVIEW
                        GROUP BY GROUPS
                        ORDER BY GROUPS DESC
                    ''')
        data = [8]
        for row in CursorByName(cursor):
            data.append(row)
        
        cursor.execute('''SELECT 
                            CASE WHEN TERM <= 2 THEN '1_GROUP_2'
                                WHEN TERM > 2 AND TERM <= 5 THEN '2_GROUP_2_5'
                                WHEN TERM > 5 AND TERM <= 7 THEN '3_GROUP_5_7'
                                WHEN TERM > 7 AND TERM <= 10 THEN '4_GROUP_7_10'
                                ELSE '5_GROUP_10' END AS GROUPS,
                            COUNT(ID) AS COUNT,
                            ROUND(SUM(VSEGO_ZADOLJENNOST)/1000000, 0) AS SUMMA	
                        FROM (
                            SELECT R2.* 
                            FROM (
                                    SELECT
                                        CASE T.SUBJ WHEN 'J' 
                                            THEN SUBSTR(CREDIT_SCHET,10,8)
                                            ELSE SUBSTR(INN_PASSPORT,11,9) 
                                            END	AS UNIQUE_CODE
                                    FROM credits_reportdata R
                                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                    WHERE REPORT_id=86 AND (JULIANDAY('2020-04-01') - JULIANDAY(DATE_OBRAZ_PROS) > 90
                                        OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL)
                                    GROUP BY UNIQUE_CODE
                                ) R1
                            LEFT JOIN (
                                    SELECT R.ID,
                                        CASE WHEN T.SUBJ = 'J' 
                                            THEN SUBSTR(CREDIT_SCHET,10,8)
                                            ELSE SUBSTR(INN_PASSPORT,11,9) 
                                            END	AS UNIQUE_CODE,
                                        CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                                            THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                            ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                            END	AS TERM,
                                        VSEGO_ZADOLJENNOST
                                    FROM credits_reportdata R
                                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                    WHERE REPORT_id = 86 
                                ) R2 ON R2.UNIQUE_CODE = R1.UNIQUE_CODE
                            )
                        GROUP BY GROUPS
                        ORDER BY GROUPS DESC
                    ''')
        data_npl = [8]
        for row in CursorByName(cursor):
            data_npl.append(row)

        cursor.execute('''SELECT CASE WHEN TERM <= 2 THEN '1_GROUP_2'
                                WHEN TERM > 2 AND TERM <= 5 THEN '2_GROUP_2_5'
                                WHEN TERM > 5 AND TERM <= 7 THEN '3_GROUP_5_7'
                                WHEN TERM > 7 AND TERM <= 10 THEN '4_GROUP_7_10'
                                ELSE '5_GROUP_10' END AS GROUPS,
                            ROUND(SUM(VSEGO_ZADOLJENNOST)/1000000, 0) AS SUMMA
                        FROM (
                            SELECT R2.* 
                            FROM (
                                    SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE, 
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) AS DAY_COUNT,
                                    SUM(OSTATOK_SUDEB) AS SUDEB,
                                    SUM(OSTATOK_VNEB_PROSR) AS PROSR,
                                    SUM(OSTATOK_PERESM) AS PERESM
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE R.REPORT_ID = 86
                                GROUP BY UNIQUE_CODE, NAME_CLIENT
                                HAVING PERESM IS NOT NULL and (DAY_COUNT < 90 or DAY_COUNT IS NULL)  and PROSR IS NULL and SUDEB IS NULL
                                ) R1
                            LEFT JOIN (
                                    SELECT R.ID,
                                    NAME_CLIENT,
                                        CASE T.SUBJ WHEN 'J' 
                                            THEN SUBSTR(CREDIT_SCHET,10,8)
                                            ELSE SUBSTR(INN_PASSPORT,11,9) 
                                            END	AS UNIQUE_CODE,
                                        CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                                            THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                            ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                            END	AS TERM,
                                        VSEGO_ZADOLJENNOST
                                    FROM credits_reportdata R
                                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                    WHERE REPORT_id = 86
                                ) R2 ON R2.UNIQUE_CODE = R1.UNIQUE_CODE	
                            )

                        GROUP BY GROUPS
                        ORDER BY GROUPS DESC
                    ''')
        data_tox = [8]
        for row in CursorByName(cursor):
            data_tox.append(row)

        cursor.execute('''WITH MYVIEW (ID, TERM, OSTATOK_REZERV) AS (
                            SELECT ID,
                            CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                                THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                END	AS TERM,
                                OSTATOK_REZERV
                            FROM credits_reportdata
                            WHERE REPORT_id = 86
                        )
                            
                        SELECT 
                            CASE WHEN TERM <= 2 THEN '1_GROUP_2'
                                WHEN TERM > 2 AND TERM <= 5 THEN '2_GROUP_2_5'
                                WHEN TERM > 5 AND TERM <= 7 THEN '3_GROUP_5_7'
                                WHEN TERM > 7 AND TERM <= 10 THEN '4_GROUP_7_10'
                                ELSE '5_GROUP_10' END AS GROUPS,
                            COUNT(ID) AS COUNT,
                            ROUND(SUM(OSTATOK_REZERV)/1000000, 0) AS SUMMA	
                        FROM MYVIEW
                        GROUP BY GROUPS
                        ORDER BY GROUPS DESC
                    ''')
        data_rezerv = [8]
        for row in CursorByName(cursor):
            data_rezerv.append(row)
            
        listCreditPortfolio = [
            {"name": "свыше 10 лет"},
            {"name": "от 7-ми до 10 лет"},
            {"name": "от 5-ти до 7 лет"},
            {"name": "от 2-х до 5 лет"},
            {"name": "до 2-х лет"},
            {"name": "Итого"},
        ]
        
        total_portfel   = sum(c['SUMMA'] for c in data[1:6])
        total_npl       = sum(c['SUMMA'] for c in data_npl[1:6])
        total_toxic     = sum(c['SUMMA'] for c in data_tox[1:6])
        total_rezerv    = sum(c['SUMMA'] for c in data_rezerv[1:6])

        for i in range(0,len(listCreditPortfolio)-1): 
            listCreditPortfolio[i]['portfel']   = data[i+1]['SUMMA']
            listCreditPortfolio[i]['ration']    = '{:.1%}'.format(data[i+1]['SUMMA']/total_portfel)
            listCreditPortfolio[i]['npl']       = data_npl[i+1]['SUMMA']
            listCreditPortfolio[i]['toxic']     = data_tox[i+1]['SUMMA']
            listCreditPortfolio[i]['npl_toxic'] = data_npl[i+1]['SUMMA']+data_tox[i+1]['SUMMA']
            listCreditPortfolio[i]['weight']    = '{:.1%}'.format(listCreditPortfolio[i]['npl_toxic']/listCreditPortfolio[i]['portfel'])
            listCreditPortfolio[i]['rezerv']    = data_rezerv[i+1]['SUMMA']
            listCreditPortfolio[i]['coating']   = '{:.1%}'.format(listCreditPortfolio[i]['rezerv']/listCreditPortfolio[i]['npl_toxic'])

        
        
        listCreditPortfolio[5]['portfel']   = total_portfel
        listCreditPortfolio[5]['ration']    = '100.0%'
        listCreditPortfolio[5]['npl']       = total_npl
        listCreditPortfolio[5]['toxic']     = total_toxic
        listCreditPortfolio[5]['npl_toxic'] = total_npl + total_toxic
        listCreditPortfolio[5]['weight']    = '{:.1%}'.format((total_npl + total_toxic)/total_portfel)
        listCreditPortfolio[5]['rezerv']    = total_rezerv
        listCreditPortfolio[5]['coating']   = '{:.1%}'.format(total_rezerv/(total_npl + total_toxic))


        table = ByTermTable(listCreditPortfolio)
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        context = {'table': table, 'page_title': page_title}
        return render(request, 'credits/portfolio.html', context)
    elif (request.GET.get('q') == 'by_subject'):
        page_title = 'В разбивке по субъектам'
        cursor = connection.cursor()
        cursor.execute('''WITH 
                            MAIN_TABLE (GROUPS, TITLE, TOTAL_LOAN) AS (
                                SELECT 
                                    CASE T.NAME 
                                        WHEN 'ЮЛ' THEN 1 
                                        WHEN 'ИП' THEN 2 
                                        ELSE 3 END AS GROUPS,
                                    T.NAME AS TITLE, 
                                    SUM(VSEGO_ZADOLJENNOST)
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86
                                GROUP BY GROUPS),
                                
                            REPORT_DATA_TABLE (GROUPS, VSEGO_ZADOLJENNOST, OSTATOK_REZERV, UNIQUE_CODE) AS (
                                SELECT 
                                    CASE T.NAME 
                                        WHEN 'ЮЛ' THEN 1 
                                        WHEN 'ИП' THEN 2 
                                        ELSE 3 END AS GROUPS,
                                    VSEGO_ZADOLJENNOST, 
                                    OSTATOK_REZERV,
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86),
                                
                            NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID=86 AND (JULIANDAY('2020-04-01') - JULIANDAY(DATE_OBRAZ_PROS) > 90
                                    OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL)
                                GROUP BY UNIQUE_CODE
                            ),

                            NPL_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM NPL_UNIQUE_TABLE NPL
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = NPL.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),

                            TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE R.REPORT_ID = 86
                                GROUP BY UNIQUE_CODE, NAME_CLIENT
                                HAVING 
                                    SUM(OSTATOK_PERESM) IS NOT NULL AND 
                                    SUM(OSTATOK_VNEB_PROSR) IS NULL AND 
                                    SUM(OSTATOK_SUDEB) IS NULL AND (
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 OR 
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL)
                            ),

                            TOX_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM TOX_UNIQUE_TABLE TOX
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = TOX.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),

                            REZ_TABLE (GROUPS, TOTAL_RESERVE) AS (
                                SELECT GROUPS, SUM(OSTATOK_REZERV) 
                                FROM REPORT_DATA_TABLE D
                                GROUP BY GROUPS
                            )

                            SELECT *, 
                            LOAN/TOTALS AS RATION,
                            NPL_LOAN+TOX_LOAN AS TOX_NPL,
                            (NPL_LOAN+TOX_LOAN)/TOTALS AS WEIGHT,
                            RESERVE/(NPL_LOAN+TOX_LOAN) AS COATING
                            FROM (	
                            SELECT 
                                M.TITLE,
                                M.GROUPS,
                                M.TOTAL_LOAN/1000000 AS LOAN,
                                N.TOTAL_LOAN/1000000 AS NPL_LOAN,
                                CASE WHEN T.TOTAL_LOAN IS NOT NULL 
                                    THEN T.TOTAL_LOAN/1000000
                                    ELSE 0 END AS TOX_LOAN,
                                R.TOTAL_RESERVE/1000000 AS RESERVE,
                                (SELECT SUM(TOTAL_LOAN)/1000000 FROM MAIN_TABLE) AS TOTALS
                            FROM MAIN_TABLE M
                            LEFT JOIN NPL_TABLE N ON N.GROUPS = M.GROUPS
                            LEFT JOIN TOX_TABLE T ON T.GROUPS = M.GROUPS
                            LEFT JOIN REZ_TABLE R ON R.GROUPS = M.GROUPS
                            )
                            ORDER BY GROUPS
                    ''')
        listBySegment = [5]
        for row in CursorByName(cursor):
            row['LOAN']     = int(row['LOAN'])
            row['RATION']   = '{:.1%}'.format(row['RATION'])
            row['NPL_LOAN'] = int(row['NPL_LOAN'])
            row['TOX_LOAN'] = int(row['TOX_LOAN'])
            row['TOX_NPL']  = int(row['TOX_NPL'])
            row['WEIGHT']   = '{:.1%}'.format(row['WEIGHT'])
            row['RESERVE']  = int(row['RESERVE'])
            row['COATING']  = '{:.1%}'.format(row['COATING'])
            listBySegment.append(row) 
        
        total = {}
        total['TITLE']    = 'Итого'
        total['LOAN']       = sum(c['LOAN'] for c in listBySegment[1:6])
        total['RATION']     = '100%' 
        total['NPL_LOAN']   = sum(c['NPL_LOAN'] for c in listBySegment[1:6]) 
        total['TOX_LOAN']   = sum(c['TOX_LOAN'] for c in listBySegment[1:6]) 
        total['TOX_NPL']    = sum(c['TOX_NPL'] for c in listBySegment[1:6]) 
        total['WEIGHT']     = '{:.1%}'.format(total['TOX_NPL']/total['LOAN']) 
        total['RESERVE']    = sum(c['RESERVE'] for c in listBySegment[1:6]) 
        total['COATING']    = '{:.1%}'.format(total['RESERVE']/total['TOX_NPL']) 
        listBySegment.append(total)

        table = BySubjectTable(listBySegment[1:5])
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        context = {'table': table, 'page_title': page_title}
        return render(request, 'credits/portfolio.html', context)
    elif (request.GET.get('q') == 'by_segment'):
        page_title = 'В разбивке по сегментам'
        cursor = connection.cursor()
        cursor.execute('''WITH 
                            MAIN_TABLE (GROUPS, TITLE, TOTAL_LOAN) AS (
                                SELECT 
                                    CASE WHEN T.SUBJ = 'J' THEN 
                                        CASE WHEN SUBSTR(OBESPECHENIE,1,2) == '42' 
                                        THEN 1 ELSE 2 END ELSE 3 
                                        END	AS GROUPS,
                                    CASE WHEN T.SUBJ = 'J' THEN 
                                        CASE WHEN SUBSTR(OBESPECHENIE,1,2) == '42' 
                                        THEN 'Инв. проект' ELSE 'ЮЛ' END ELSE 'ФЛ' 
                                        END	AS TITLE,
                                    SUM(VSEGO_ZADOLJENNOST)
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86
                                GROUP BY GROUPS),
                                
                            REPORT_DATA_TABLE (GROUPS, VSEGO_ZADOLJENNOST, OSTATOK_REZERV, UNIQUE_CODE) AS (
                                SELECT 
                                    CASE WHEN T.SUBJ = 'J' THEN 
                                        CASE WHEN SUBSTR(OBESPECHENIE,1,2) == '42' 
                                        THEN 1 ELSE 2 END ELSE 3 
                                        END	AS GROUPS,
                                    VSEGO_ZADOLJENNOST, 
                                    OSTATOK_REZERV,
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86),
                                
                            NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID=86 AND (JULIANDAY('2020-04-01') - JULIANDAY(DATE_OBRAZ_PROS) > 90
                                    OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL)
                                GROUP BY UNIQUE_CODE
                            ),
                            
                            NPL_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM NPL_UNIQUE_TABLE NPL
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = NPL.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),
                            
                            TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE R.REPORT_ID = 86
                                GROUP BY UNIQUE_CODE, NAME_CLIENT
                                HAVING 
                                    SUM(OSTATOK_PERESM) IS NOT NULL AND 
                                    SUM(OSTATOK_VNEB_PROSR) IS NULL AND 
                                    SUM(OSTATOK_SUDEB) IS NULL AND (
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 OR 
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL)
                            ),
                            
                            TOX_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM TOX_UNIQUE_TABLE TOX
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = TOX.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),
                            
                            REZ_TABLE (GROUPS, TOTAL_RESERVE) AS (
                                SELECT GROUPS, SUM(OSTATOK_REZERV) 
                                FROM REPORT_DATA_TABLE D
                                GROUP BY GROUPS
                            )
                            
                        SELECT *, 
                        LOAN/TOTALS AS RATION,
                        NPL_LOAN+TOX_LOAN AS TOX_NPL,
                        (NPL_LOAN+TOX_LOAN)/LOAN AS WEIGHT,
                        RESERVE/(NPL_LOAN+TOX_LOAN) AS COATING
                        FROM (	
                            SELECT 
                                M.TITLE,
                                M.GROUPS,
                                M.TOTAL_LOAN/1000000 AS LOAN,
                                N.TOTAL_LOAN/1000000 AS NPL_LOAN,
                                CASE WHEN T.TOTAL_LOAN IS NOT NULL 
                                    THEN T.TOTAL_LOAN/1000000
                                    ELSE 0 END AS TOX_LOAN,
                                R.TOTAL_RESERVE/1000000 AS RESERVE,
                                (SELECT SUM(TOTAL_LOAN)/1000000 FROM MAIN_TABLE) AS TOTALS
                            FROM MAIN_TABLE M
                            LEFT JOIN NPL_TABLE N ON N.GROUPS = M.GROUPS
                            LEFT JOIN TOX_TABLE T ON T.GROUPS = M.GROUPS
                            LEFT JOIN REZ_TABLE R ON R.GROUPS = M.GROUPS
                        )
                        ORDER BY GROUPS

                    ''')
        listBySegment = [5]
        for row in CursorByName(cursor):
            row['LOAN']     = int(row['LOAN'])
            row['RATION']   = '{:.1%}'.format(row['RATION'])
            row['NPL_LOAN'] = int(row['NPL_LOAN'])
            row['TOX_LOAN'] = int(row['TOX_LOAN'])
            row['TOX_NPL']  = int(row['TOX_NPL'])
            row['WEIGHT']   = '{:.1%}'.format(row['WEIGHT'])
            row['RESERVE']  = int(row['RESERVE'])
            row['COATING']  = '{:.1%}'.format(row['COATING'])
            listBySegment.append(row) 
        
        total = {}
        total['TITLE']      = 'Итого'
        total['LOAN']       = sum(c['LOAN'] for c in listBySegment[1:6])
        total['RATION']     = '100%' 
        total['NPL_LOAN']   = sum(c['NPL_LOAN'] for c in listBySegment[1:6]) 
        total['TOX_LOAN']   = sum(c['TOX_LOAN'] for c in listBySegment[1:6]) 
        total['TOX_NPL']    = sum(c['TOX_NPL'] for c in listBySegment[1:6]) 
        total['WEIGHT']     = '{:.1%}'.format(total['TOX_NPL']/total['LOAN']) 
        total['RESERVE']    = sum(c['RESERVE'] for c in listBySegment[1:6]) 
        total['COATING']    = '{:.1%}'.format(total['RESERVE']/total['TOX_NPL']) 
        listBySegment.append(total)

        table = BySubjectTable(listBySegment[1:5])
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        context = {'table': table, 'page_title': page_title}
        return render(request, 'credits/portfolio.html', context) 
    elif (request.GET.get('q') == 'by_currency'):
        page_title = 'В разбивке по валютам'
        cursor = connection.cursor()
        cursor.execute('''WITH 
                            MAIN_TABLE (GROUPS, TITLE, TOTAL_LOAN) AS (
                                SELECT 
                                    CASE WHEN CODE_VAL == '000' 
                                        THEN 1 ELSE 2 
                                        END AS GROUPS,
                                    CASE WHEN CODE_VAL == '000' 
                                        THEN 'Национальная валюта'
                                        ELSE 'Иностранная валюта' 
                                        END AS TITLE,
                                    SUM(VSEGO_ZADOLJENNOST)
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86
                                GROUP BY GROUPS),
                                
                            REPORT_DATA_TABLE (GROUPS, VSEGO_ZADOLJENNOST, OSTATOK_REZERV, UNIQUE_CODE) AS (
                                SELECT 
                                    CASE WHEN CODE_VAL == '000' 
                                        THEN 1 ELSE 2 
                                        END AS GROUPS,
                                    VSEGO_ZADOLJENNOST, 
                                    OSTATOK_REZERV,
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86),
                                
                            NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID=86 AND (JULIANDAY('2020-04-01') - JULIANDAY(DATE_OBRAZ_PROS) > 90
                                    OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL)
                                GROUP BY UNIQUE_CODE
                            ),
                            
                            NPL_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM NPL_UNIQUE_TABLE NPL
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = NPL.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),
                            
                            TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE R.REPORT_ID = 86
                                GROUP BY UNIQUE_CODE, NAME_CLIENT
                                HAVING 
                                    SUM(OSTATOK_PERESM) IS NOT NULL AND 
                                    SUM(OSTATOK_VNEB_PROSR) IS NULL AND 
                                    SUM(OSTATOK_SUDEB) IS NULL AND (
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 OR 
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL)
                            ),
                            
                            TOX_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM TOX_UNIQUE_TABLE TOX
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = TOX.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),
                            
                            REZ_TABLE (GROUPS, TOTAL_RESERVE) AS (
                                SELECT GROUPS, SUM(OSTATOK_REZERV) 
                                FROM REPORT_DATA_TABLE D
                                GROUP BY GROUPS
                            )
                            
                        SELECT *, 
                        LOAN/TOTALS AS RATION,
                        NPL_LOAN+TOX_LOAN AS TOX_NPL,
                        (NPL_LOAN+TOX_LOAN)/LOAN AS WEIGHT,
                        RESERVE/(NPL_LOAN+TOX_LOAN) AS COATING
                        FROM (	
                            SELECT 
                                M.TITLE,
                                M.GROUPS,
                                M.TOTAL_LOAN/1000000 AS LOAN,
                                N.TOTAL_LOAN/1000000 AS NPL_LOAN,
                                CASE WHEN T.TOTAL_LOAN IS NOT NULL 
                                    THEN T.TOTAL_LOAN/1000000
                                    ELSE 0 END AS TOX_LOAN,
                                R.TOTAL_RESERVE/1000000 AS RESERVE,
                                (SELECT SUM(TOTAL_LOAN)/1000000 FROM MAIN_TABLE) AS TOTALS
                            FROM MAIN_TABLE M
                            LEFT JOIN NPL_TABLE N ON N.GROUPS = M.GROUPS
                            LEFT JOIN TOX_TABLE T ON T.GROUPS = M.GROUPS
                            LEFT JOIN REZ_TABLE R ON R.GROUPS = M.GROUPS
                        )
                        ORDER BY GROUPS
                    ''')
        listBySegment = [5]
        for row in CursorByName(cursor):
            row['LOAN']     = int(row['LOAN'])
            row['RATION']   = '{:.1%}'.format(row['RATION'])
            row['NPL_LOAN'] = int(row['NPL_LOAN'])
            row['TOX_LOAN'] = int(row['TOX_LOAN'])
            row['TOX_NPL']  = int(row['TOX_NPL'])
            row['WEIGHT']   = '{:.1%}'.format(row['WEIGHT'])
            row['RESERVE']  = int(row['RESERVE'])
            row['COATING']  = '{:.1%}'.format(row['COATING'])
            listBySegment.append(row) 
        
        total = {}
        total['TITLE']      = 'Итого'
        total['LOAN']       = sum(c['LOAN'] for c in listBySegment[1:6])
        total['RATION']     = '100%' 
        total['NPL_LOAN']   = sum(c['NPL_LOAN'] for c in listBySegment[1:6]) 
        total['TOX_LOAN']   = sum(c['TOX_LOAN'] for c in listBySegment[1:6]) 
        total['TOX_NPL']    = sum(c['TOX_NPL'] for c in listBySegment[1:6]) 
        total['WEIGHT']     = '{:.1%}'.format(total['TOX_NPL']/total['LOAN']) 
        total['RESERVE']    = sum(c['RESERVE'] for c in listBySegment[1:6]) 
        total['COATING']    = '{:.1%}'.format(total['RESERVE']/total['TOX_NPL']) 
        listBySegment.append(total)

        table = BySubjectTable(listBySegment[1:5])
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        context = {'table': table, 'page_title': page_title}
        return render(request, 'credits/portfolio.html', context) 
    elif (request.GET.get('q') == 'by_branch'):
        page_title = 'В разбивке по филиалам'
        cursor = connection.cursor()
        cursor.execute('''WITH 
                            MAIN_TABLE (GROUPS, TITLE, TOTAL_LOAN) AS (
                                SELECT 
                                    B.SORT AS GROUPS,
                                    B.NAME AS TITLE, 
                                    SUM(VSEGO_ZADOLJENNOST)
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                                WHERE REPORT_ID = 86
                                GROUP BY GROUPS),
                                
                            REPORT_DATA_TABLE (GROUPS, VSEGO_ZADOLJENNOST, OSTATOK_REZERV, UNIQUE_CODE) AS (
                                SELECT 
                                    B.SORT AS GROUPS,
                                    VSEGO_ZADOLJENNOST, 
                                    OSTATOK_REZERV,
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                                WHERE REPORT_ID = 86),
                                
                            NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID=86 AND (JULIANDAY('2020-04-01') - JULIANDAY(DATE_OBRAZ_PROS) > 90
                                    OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL)
                                GROUP BY UNIQUE_CODE
                            ),

                            NPL_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM NPL_UNIQUE_TABLE NPL
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = NPL.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),

                            TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE R.REPORT_ID = 86
                                GROUP BY UNIQUE_CODE, NAME_CLIENT
                                HAVING 
                                    SUM(OSTATOK_PERESM) IS NOT NULL AND 
                                    SUM(OSTATOK_VNEB_PROSR) IS NULL AND 
                                    SUM(OSTATOK_SUDEB) IS NULL AND (
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 OR 
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL)
                            ),

                            TOX_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM TOX_UNIQUE_TABLE TOX
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = TOX.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),

                            REZ_TABLE (GROUPS, TOTAL_RESERVE) AS (
                                SELECT GROUPS, SUM(OSTATOK_REZERV) 
                                FROM REPORT_DATA_TABLE D
                                GROUP BY GROUPS
                            )

                            SELECT *, 
                            LOAN/TOTALS AS RATION,
                            NPL_LOAN+TOX_LOAN AS TOX_NPL,
                            (NPL_LOAN+TOX_LOAN)/LOAN AS WEIGHT,
                            RESERVE/(NPL_LOAN+TOX_LOAN) AS COATING
                            FROM (	
                            SELECT 
                                M.TITLE,
                                M.GROUPS,
                                CASE WHEN M.TOTAL_LOAN IS NOT NULL 
                                    THEN M.TOTAL_LOAN/1000000
                                    ELSE 0 END AS LOAN,
                                CASE WHEN N.TOTAL_LOAN IS NOT NULL 
                                    THEN N.TOTAL_LOAN/1000000
                                    ELSE 0 END AS NPL_LOAN,
                                CASE WHEN T.TOTAL_LOAN IS NOT NULL 
                                    THEN T.TOTAL_LOAN/1000000
                                    ELSE 0 END AS TOX_LOAN,
                                CASE WHEN R.TOTAL_RESERVE IS NOT NULL 
                                    THEN R.TOTAL_RESERVE/1000000
                                    ELSE 0 END AS RESERVE,
                                (SELECT SUM(TOTAL_LOAN)/1000000 FROM MAIN_TABLE) AS TOTALS
                            FROM MAIN_TABLE M
                            LEFT JOIN NPL_TABLE N ON N.GROUPS = M.GROUPS
                            LEFT JOIN TOX_TABLE T ON T.GROUPS = M.GROUPS
                            LEFT JOIN REZ_TABLE R ON R.GROUPS = M.GROUPS
                            )
                            ORDER BY GROUPS
                    ''')
        listBySegment = [24]
        for row in CursorByName(cursor):
            row['LOAN']     = int(row['LOAN'])
            row['RATION']   = '{:.1%}'.format(row['RATION'])
            row['NPL_LOAN'] = int(row['NPL_LOAN'])
            row['TOX_LOAN'] = int(row['TOX_LOAN'])
            row['TOX_NPL']  = int(row['TOX_NPL'])
            row['WEIGHT']   = '{:.1%}'.format(row['WEIGHT'])
            row['RESERVE']  = int(row['RESERVE'])
            row['COATING']  = '{:.1%}'.format(row['COATING'])
            listBySegment.append(row) 
        
        total = {}
        total['TITLE']      = 'Итого'
        total['LOAN']       = sum(c['LOAN'] for c in listBySegment[1:24])
        total['RATION']     = '100%' 
        total['NPL_LOAN']   = sum(c['NPL_LOAN'] for c in listBySegment[1:24]) 
        total['TOX_LOAN']   = sum(c['TOX_LOAN'] for c in listBySegment[1:24]) 
        total['TOX_NPL']    = sum(c['TOX_NPL'] for c in listBySegment[1:24]) 
        total['WEIGHT']     = '{:.1%}'.format(total['TOX_NPL']/total['LOAN']) 
        total['RESERVE']    = sum(c['RESERVE'] for c in listBySegment[1:24]) 
        total['COATING']    = '{:.1%}'.format(total['RESERVE']/total['TOX_NPL']) 
        listBySegment.append(total)

        table = BySubjectTable(listBySegment[1:25])
        table.paginate(page=request.GET.get("page", 1), per_page=10)
        context = {'table': table, 'page_title': page_title}
        return render(request, 'credits/portfolio.html', context) 
    elif (request.GET.get('q') == 'by_percentage'):
        page_title = 'В разбивке по процентной ставке'
        page_description = 'Description'
        cursor = connection.cursor()
        cursor.execute('''WITH RECURSIVE
                            MAIN_TABLE (GROUPS, TITLE) AS (
                                SELECT 1, '20 и более'
                                UNION
                                SELECT GROUPS + 1,
                                    CASE GROUPS +1
                                        WHEN 2 THEN '16 - 20' 
                                        WHEN 3 THEN '11 - 15' 
                                        WHEN 4 THEN '6 - 10' 
                                        ELSE '0 - 5' END AS TITLE	
                                FROM MAIN_TABLE LIMIT 5),
                                
                            REPORT_DATA_TABLE (GROUPS, SUBJECT, PERIOD, VSEGO_ZADOLJENNOST, UNIQUE_CODE) AS (
                                SELECT 
                                    CASE WHEN CREDIT_PROCENT > 20 THEN 1
                                        WHEN CREDIT_PROCENT > 15 THEN 2 
                                        WHEN CREDIT_PROCENT > 10 THEN 3 
                                        WHEN CREDIT_PROCENT > 5 THEN 4 
                                        ELSE 5 END AS GROUPS,
                                    T.SUBJ,
                                    SROK,
                                    VSEGO_ZADOLJENNOST, 
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86 AND CODE_VAL = '000'),

                            UL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '3%'
                                GROUP BY GROUPS
                            ),
                            
                            UL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '1%'
                                GROUP BY GROUPS
                            ),
                            
                            FL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '3%'
                                GROUP BY GROUPS
                            ),
                            
                            FL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '1%'
                                GROUP BY GROUPS
                            )	
                        SELECT 
                            M.TITLE,
                            M.GROUPS,
                            IFNULL(ULL.TOTAL_LOAN/1000000,0) AS ULL_LOAN,
                            IFNULL(ULS.TOTAL_LOAN/1000000,0) AS ULS_LOAN,
                            IFNULL(FLL.TOTAL_LOAN/1000000,0) AS FLL_LOAN,
                            IFNULL(FLS.TOTAL_LOAN/1000000,0) AS FLS_LOAN
                        FROM MAIN_TABLE M
                        LEFT JOIN UL_LONG_TABLE ULL  ON ULL.GROUPS = M.GROUPS
                        LEFT JOIN UL_SHORT_TABLE ULS ON ULS.GROUPS = M.GROUPS
                        LEFT JOIN FL_LONG_TABLE FLL  ON FLL.GROUPS = M.GROUPS
                        LEFT JOIN FL_SHORT_TABLE FLS ON FLS.GROUPS = M.GROUPS
                        ORDER BY M.GROUPS DESC
                    ''')
        
        data = [24]
        for row in CursorByName(cursor):
            data.append(row) 
        
        listData = data[1:]

        total_ull = sum(c['ULL_LOAN'] for c in listData)
        total_uls = sum(c['ULS_LOAN'] for c in listData)
        total_fll = sum(c['FLL_LOAN'] for c in listData)
        total_fls = sum(c['FLS_LOAN'] for c in listData)

        for item in listData:
            item['ULL_LOAN'] = int(item['ULL_LOAN'])
            item['ULS_LOAN'] = int(item['ULS_LOAN'])
            item['FLL_LOAN'] = int(item['FLL_LOAN'])
            item['FLS_LOAN'] = int(item['FLS_LOAN'])
            item['ULL_PERCENT'] = '{:.1%}'.format(item['ULL_LOAN']/total_ull) if not (total_ull == 0) else '0,0%'
            item['ULS_PERCENT'] = '{:.1%}'.format(item['ULS_LOAN']/total_uls) if not (total_uls == 0) else '0,0%'
            item['FLL_PERCENT'] = '{:.1%}'.format(item['FLL_LOAN']/total_fll) if not (total_fll == 0) else '0,0%'
            item['FLS_PERCENT'] = '{:.1%}'.format(item['FLS_LOAN']/total_fls) if not (total_fls == 0) else '0,0%'

        total = {
            'TITLE':        'Итого',
            'ULL_LOAN':     int(total_ull),
            'ULS_LOAN':     int(total_uls),
            'FLL_LOAN':     int(total_fll),
            'FLS_LOAN':     int(total_fls),
            'ULL_PERCENT':  '100%' if not (total_ull == 0) else '0,0%',
            'ULS_PERCENT':  '100%' if not (total_uls == 0) else '0,0%',
            'FLL_PERCENT':  '100%' if not (total_fll == 0) else '0,0%',
            'FLS_PERCENT':  '100%' if not (total_fls == 0) else '0,0%'
        }

        listData.append(total)

        table1 = ByPercentageTable(listData)
        table1.paginate(page=request.GET.get("page", 1), per_page=10)
        
        cursor.execute('''WITH RECURSIVE
                            MAIN_TABLE (GROUPS, TITLE) AS (
                                SELECT 1, '20 и более'
                                UNION
                                SELECT GROUPS + 1,
                                    CASE GROUPS +1
                                        WHEN 2 THEN '16 - 20' 
                                        WHEN 3 THEN '11 - 15' 
                                        WHEN 4 THEN '6 - 10' 
                                        ELSE '0 - 5' END AS TITLE	
                                FROM MAIN_TABLE LIMIT 5),
                                
                            REPORT_DATA_TABLE (GROUPS, SUBJECT, PERIOD, VSEGO_ZADOLJENNOST, UNIQUE_CODE) AS (
                                SELECT 
                                    CASE WHEN CREDIT_PROCENT > 20 THEN 1
                                        WHEN CREDIT_PROCENT > 15 THEN 2 
                                        WHEN CREDIT_PROCENT > 10 THEN 3 
                                        WHEN CREDIT_PROCENT > 5 THEN 4 
                                        ELSE 5 END AS GROUPS,
                                    T.SUBJ,
                                    SROK,
                                    VSEGO_ZADOLJENNOST, 
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86 AND CODE_VAL <> '000'),

                            UL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '3%'
                                GROUP BY GROUPS
                            ),
                            
                            UL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '1%'
                                GROUP BY GROUPS
                            ),
                            
                            FL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '3%'
                                GROUP BY GROUPS
                            ),
                            
                            FL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '1%'
                                GROUP BY GROUPS
                            )
                        SELECT 
                            M.TITLE,
                            M.GROUPS,
                            IFNULL(ULL.TOTAL_LOAN/1000000,0) AS ULL_LOAN,
                            IFNULL(ULS.TOTAL_LOAN/1000000,0) AS ULS_LOAN,
                            IFNULL(FLL.TOTAL_LOAN/1000000,0) AS FLL_LOAN,
                            IFNULL(FLS.TOTAL_LOAN/1000000,0) AS FLS_LOAN
                        FROM MAIN_TABLE M
                        LEFT JOIN UL_LONG_TABLE ULL  ON ULL.GROUPS = M.GROUPS
                        LEFT JOIN UL_SHORT_TABLE ULS ON ULS.GROUPS = M.GROUPS
                        LEFT JOIN FL_LONG_TABLE FLL  ON FLL.GROUPS = M.GROUPS
                        LEFT JOIN FL_SHORT_TABLE FLS ON FLS.GROUPS = M.GROUPS
                        ORDER BY M.GROUPS DESC
                    ''')
        
        data = [24]
        for row in CursorByName(cursor):
            data.append(row) 
        
        listData = data[1:]

        total_ull = sum(c['ULL_LOAN'] for c in listData)
        total_uls = sum(c['ULS_LOAN'] for c in listData)
        total_fll = sum(c['FLL_LOAN'] for c in listData)
        total_fls = sum(c['FLS_LOAN'] for c in listData)

        for item in listData:
            item['ULL_LOAN'] = int(item['ULL_LOAN'])
            item['ULS_LOAN'] = int(item['ULS_LOAN'])
            item['FLL_LOAN'] = int(item['FLL_LOAN'])
            item['FLS_LOAN'] = int(item['FLS_LOAN'])
            item['ULL_PERCENT'] = '{:.1%}'.format(item['ULL_LOAN']/total_ull) if not (total_ull == 0) else '0,0%'
            item['ULS_PERCENT'] = '{:.1%}'.format(item['ULS_LOAN']/total_uls) if not (total_uls == 0) else '0,0%'
            item['FLL_PERCENT'] = '{:.1%}'.format(item['FLL_LOAN']/total_fll) if not (total_fll == 0) else '0,0%'
            item['FLS_PERCENT'] = '{:.1%}'.format(item['FLS_LOAN']/total_fls) if not (total_fls == 0) else '0,0%'

        total = {
            'TITLE':        'Итого',
            'ULL_LOAN':     int(total_ull),
            'ULS_LOAN':     int(total_uls),
            'FLL_LOAN':     int(total_fll),
            'FLS_LOAN':     int(total_fls),
            'ULL_PERCENT':  '100%' if not (total_ull == 0) else '0,0%',
            'ULS_PERCENT':  '100%' if not (total_uls == 0) else '0,0%',
            'FLL_PERCENT':  '100%' if not (total_fll == 0) else '0,0%',
            'FLS_PERCENT':  '100%' if not (total_fls == 0) else '0,0%'
        }

        listData.append(total)

        table2 = ByPercentageTable(listData)
        table2.paginate(page=request.GET.get("page", 1), per_page=10)

        #table3
        cursor.execute('''WITH RECURSIVE
                            MAIN_TABLE (GROUPS, TITLE) AS (
                                SELECT 1, '20 и более'
                                UNION
                                SELECT GROUPS + 1,
                                    CASE GROUPS +1
                                        WHEN 2 THEN '16 - 20' 
                                        WHEN 3 THEN '11 - 15' 
                                        WHEN 4 THEN '6 - 10' 
                                        ELSE '0 - 5' END AS TITLE	
                                FROM MAIN_TABLE LIMIT 5),
                                
                            REPORT_DATA_TABLE (GROUPS, TERM, VSEGO_ZADOLJENNOST) AS (
                                SELECT 
                                    CASE WHEN CREDIT_PROCENT > 20 THEN 1
                                        WHEN CREDIT_PROCENT > 15 THEN 2 
                                        WHEN CREDIT_PROCENT > 10 THEN 3 
                                        WHEN CREDIT_PROCENT > 5 THEN 4 
                                        ELSE 5 END AS GROUPS,
                                    CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                                        THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                        ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                        END	AS TERM,
                                    VSEGO_ZADOLJENNOST
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE T.SUBJ = 'J' AND REPORT_ID = 86 AND CODE_VAL = '000'),

                            TERMLESS_2 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM <= 2 OR TERM IS NULL
                                GROUP BY GROUPS
                            ),
                            
                            TERMLESS_5 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM <= 5 AND TERM > 2
                                GROUP BY GROUPS
                            ),
                            
                            TERMLESS_7 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM <= 7 AND TERM > 5
                                GROUP BY GROUPS
                            ),
                            
                            TERMLESS_10 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM <= 10 AND TERM > 7
                                GROUP BY GROUPS
                            ),
                            
                            TERMMORE_10 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM > 10
                                GROUP BY GROUPS
                            )

                        SELECT 
                            M.TITLE,
                            M.GROUPS,
                            IFNULL(T2.TOTAL_LOAN/1000000,0) AS T2_LOAN,
                            IFNULL(T5.TOTAL_LOAN/1000000,0) AS T5_LOAN,
                            IFNULL(T7.TOTAL_LOAN/1000000,0) AS T7_LOAN,
                            IFNULL(T10.TOTAL_LOAN/1000000,0) AS T10_LOAN,
                            IFNULL(T11.TOTAL_LOAN/1000000,0) AS T11_LOAN
                        FROM MAIN_TABLE M
                        LEFT JOIN TERMLESS_2 T2  ON T2.GROUPS = M.GROUPS
                        LEFT JOIN TERMLESS_5 T5  ON T5.GROUPS = M.GROUPS
                        LEFT JOIN TERMLESS_7 T7  ON T7.GROUPS = M.GROUPS
                        LEFT JOIN TERMLESS_10 T10  ON T10.GROUPS = M.GROUPS
                        LEFT JOIN TERMMORE_10 T11  ON T11.GROUPS = M.GROUPS
                        ORDER BY M.GROUPS DESC
                    ''')
        
        data = [24]
        for row in CursorByName(cursor):
            data.append(row) 
        
        listData = data[1:]

        total_t2 = sum(c['T2_LOAN'] for c in listData)
        total_t5 = sum(c['T5_LOAN'] for c in listData)
        total_t7 = sum(c['T7_LOAN'] for c in listData)
        total_t10 = sum(c['T10_LOAN'] for c in listData)
        total_t11 = sum(c['T11_LOAN'] for c in listData)

        for item in listData:
            item['T2_LOAN'] = int(item['T2_LOAN'])
            item['T5_LOAN'] = int(item['T5_LOAN'])
            item['T7_LOAN'] = int(item['T7_LOAN'])
            item['T10_LOAN'] = int(item['T10_LOAN'])
            item['T11_LOAN'] = int(item['T11_LOAN'])
            item['T2_PERCENT'] = '{:.1%}'.format(item['T2_LOAN']/total_t2) if not (total_t2 == 0) else '0,0%'
            item['T5_PERCENT'] = '{:.1%}'.format(item['T5_LOAN']/total_t5) if not (total_t5 == 0) else '0,0%'
            item['T7_PERCENT'] = '{:.1%}'.format(item['T7_LOAN']/total_t7) if not (total_t7 == 0) else '0,0%'
            item['T10_PERCENT'] = '{:.1%}'.format(item['T10_LOAN']/total_t10) if not (total_t10 == 0) else '0,0%'
            item['T11_PERCENT'] = '{:.1%}'.format(item['T11_LOAN']/total_t11) if not (total_t11 == 0) else '0,0%'

        total = {
            'TITLE':        'Итого',
            'T2_LOAN':     int(total_t2),
            'T5_LOAN':     int(total_t5),
            'T7_LOAN':     int(total_t7),
            'T10_LOAN':     int(total_t10),
            'T11_LOAN':     int(total_t11),
            'T2_PERCENT':  '100%' if not (total_t2 == 0) else '0,0%',
            'T5_PERCENT':  '100%' if not (total_t5 == 0) else '0,0%',
            'T7_PERCENT':  '100%' if not (total_t7 == 0) else '0,0%',
            'T10_PERCENT':  '100%' if not (total_t10 == 0) else '0,0%',
            'T11_PERCENT':  '100%' if not (total_t11 == 0) else '0,0%',
           
        }

        listData.append(total)

        table3 = ByPercentageULTable(listData)
        table3.paginate(page=request.GET.get("page", 1), per_page=10)

        #table4
        cursor.execute('''WITH RECURSIVE
                            MAIN_TABLE (GROUPS, TITLE) AS (
                                SELECT 1, '20 и более'
                                UNION
                                SELECT GROUPS + 1,
                                    CASE GROUPS +1
                                        WHEN 2 THEN '16 - 20' 
                                        WHEN 3 THEN '11 - 15' 
                                        WHEN 4 THEN '6 - 10' 
                                        ELSE '0 - 5' END AS TITLE	
                                FROM MAIN_TABLE LIMIT 5),
                                
                            REPORT_DATA_TABLE (GROUPS, TERM, VSEGO_ZADOLJENNOST) AS (
                                SELECT 
                                    CASE WHEN CREDIT_PROCENT > 20 THEN 1
                                        WHEN CREDIT_PROCENT > 15 THEN 2 
                                        WHEN CREDIT_PROCENT > 10 THEN 3 
                                        WHEN CREDIT_PROCENT > 5 THEN 4 
                                        ELSE 5 END AS GROUPS,
                                    CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                                        THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                        ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                        END	AS TERM,
                                    VSEGO_ZADOLJENNOST
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE T.SUBJ = 'J' AND REPORT_ID = 86 AND CODE_VAL <> '000'),

                            TERMLESS_2 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM <= 2 OR TERM IS NULL
                                GROUP BY GROUPS
                            ),
                            
                            TERMLESS_5 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM <= 5 AND TERM > 2
                                GROUP BY GROUPS
                            ),
                            
                            TERMLESS_7 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM <= 7 AND TERM > 5
                                GROUP BY GROUPS
                            ),
                            
                            TERMLESS_10 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM <= 10 AND TERM > 7
                                GROUP BY GROUPS
                            ),
                            
                            TERMMORE_10 (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE TERM > 10
                                GROUP BY GROUPS
                            )
                        SELECT 
                            M.TITLE,
                            M.GROUPS,
                            IFNULL(T2.TOTAL_LOAN/1000000,0) AS T2_LOAN,
                            IFNULL(T5.TOTAL_LOAN/1000000,0) AS T5_LOAN,
                            IFNULL(T7.TOTAL_LOAN/1000000,0) AS T7_LOAN,
                            IFNULL(T10.TOTAL_LOAN/1000000,0) AS T10_LOAN,
                            IFNULL(T11.TOTAL_LOAN/1000000,0) AS T11_LOAN
                        FROM MAIN_TABLE M
                        LEFT JOIN TERMLESS_2 T2  ON T2.GROUPS = M.GROUPS
                        LEFT JOIN TERMLESS_5 T5  ON T5.GROUPS = M.GROUPS
                        LEFT JOIN TERMLESS_7 T7  ON T7.GROUPS = M.GROUPS
                        LEFT JOIN TERMLESS_10 T10  ON T10.GROUPS = M.GROUPS
                        LEFT JOIN TERMMORE_10 T11  ON T11.GROUPS = M.GROUPS
                        ORDER BY M.GROUPS DESC
                    ''')
        
        data = [24]
        for row in CursorByName(cursor):
            data.append(row) 
        
        listData = data[1:]

        total_t2 = sum(c['T2_LOAN'] for c in listData)
        total_t5 = sum(c['T5_LOAN'] for c in listData)
        total_t7 = sum(c['T7_LOAN'] for c in listData)
        total_t10 = sum(c['T10_LOAN'] for c in listData)
        total_t11 = sum(c['T11_LOAN'] for c in listData)

        for item in listData:
            item['T2_LOAN'] = int(item['T2_LOAN'])
            item['T5_LOAN'] = int(item['T5_LOAN'])
            item['T7_LOAN'] = int(item['T7_LOAN'])
            item['T10_LOAN'] = int(item['T10_LOAN'])
            item['T11_LOAN'] = int(item['T11_LOAN'])
            item['T2_PERCENT'] = '{:.1%}'.format(item['T2_LOAN']/total_t2) if not (total_t2 == 0) else '0,0%'
            item['T5_PERCENT'] = '{:.1%}'.format(item['T5_LOAN']/total_t5) if not (total_t5 == 0) else '0,0%'
            item['T7_PERCENT'] = '{:.1%}'.format(item['T7_LOAN']/total_t7) if not (total_t7 == 0) else '0,0%'
            item['T10_PERCENT'] = '{:.1%}'.format(item['T10_LOAN']/total_t10) if not (total_t10 == 0) else '0,0%'
            item['T11_PERCENT'] = '{:.1%}'.format(item['T11_LOAN']/total_t11) if not (total_t11 == 0) else '0,0%'

        total = {
            'TITLE':        'Итого',
            'T2_LOAN':     int(total_t2),
            'T5_LOAN':     int(total_t5),
            'T7_LOAN':     int(total_t7),
            'T10_LOAN':     int(total_t10),
            'T11_LOAN':     int(total_t11),
            'T2_PERCENT':  '100%' if not (total_t2 == 0) else '0,0%',
            'T5_PERCENT':  '100%' if not (total_t5 == 0) else '0,0%',
            'T7_PERCENT':  '100%' if not (total_t7 == 0) else '0,0%',
            'T10_PERCENT':  '100%' if not (total_t10 == 0) else '0,0%',
            'T11_PERCENT':  '100%' if not (total_t11 == 0) else '0,0%',
        }

        listData.append(total)

        table4 = ByPercentageULTable(listData)
        table4.paginate(page=request.GET.get("page", 1), per_page=10)


        context = {
            'table1': table1, 
            'table2': table2, 
            'table3': table3, 
            'table4': table4, 
            'page_title': page_title, 
            'page_description': page_description
        }
        return render(request, 'credits/percentage.html', context) 
    elif (request.GET.get('q') == 'by_average'):
        page_title = 'В разбивке по средневзвешенной процентной ставке'
        cursor = connection.cursor()
        cursor.execute('''WITH
                            MAIN_TABLE (GROUPS, TITLE) AS (
                                SELECT 1, 'Долгосрочные'
                                UNION
                                SELECT 2, 'Краткосрочные'
                            ),
                                
                            REPORT_DATA_TABLE (GROUPS, NAME_VALUTA, SUM_CREDIT, VSEGO_ZADOLJENNOST) AS (
                                SELECT 
                                    CASE WHEN SUBSTR(SROK,1,1) = '3' 
                                        THEN 1 ELSE 2 END AS GROUPS,
                                    C.NAME,
                                    CREDIT_PROCENT * VSEGO_ZADOLJENNOST,
                                    VSEGO_ZADOLJENNOST
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                LEFT JOIN CREDITS_CURRENCY C ON C.CODE = R.CODE_VAL
                                WHERE REPORT_ID = 86 AND T.SUBJ = 'J'),

                            VALUTA_UZS (GROUPS, AVERAGE) AS (
                                SELECT GROUPS, SUM(SUM_CREDIT)/SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE NAME_VALUTA = 'UZS'
                                GROUP BY GROUPS
                            ),
                            
                            VALUTA_USD (GROUPS, AVERAGE) AS (
                                SELECT GROUPS, SUM(SUM_CREDIT)/SUM(VSEGO_ZADOLJENNOST)
                                FROM REPORT_DATA_TABLE D
                                WHERE NAME_VALUTA = 'USD'
                                GROUP BY GROUPS
                            ),
                            
                            VALUTA_EUR (GROUPS, AVERAGE) AS (
                                SELECT GROUPS, SUM(SUM_CREDIT)/SUM(VSEGO_ZADOLJENNOST)
                                FROM REPORT_DATA_TABLE D
                                WHERE NAME_VALUTA = 'EUR'
                                GROUP BY GROUPS
                            ),
                            
                            VALUTA_JPY (GROUPS, AVERAGE) AS (
                                SELECT GROUPS, SUM(SUM_CREDIT)/SUM(VSEGO_ZADOLJENNOST)
                                FROM REPORT_DATA_TABLE D
                                WHERE NAME_VALUTA = 'JPY'
                                GROUP BY GROUPS
                            )

                        SELECT 
                            M.TITLE,
                            M.GROUPS,
                            IFNULL(UZS.AVERAGE,0) AS UZS_AVERAGE,
                            IFNULL(USD.AVERAGE,0) AS USD_AVERAGE,
                            IFNULL(EUR.AVERAGE,0) AS EUR_AVERAGE,
                            IFNULL(JPY.AVERAGE,0) AS JPY_AVERAGE
                        FROM MAIN_TABLE M
                        LEFT JOIN VALUTA_UZS UZS  ON UZS.GROUPS = M.GROUPS
                        LEFT JOIN VALUTA_USD USD  ON USD.GROUPS = M.GROUPS
                        LEFT JOIN VALUTA_EUR EUR  ON EUR.GROUPS = M.GROUPS
                        LEFT JOIN VALUTA_JPY JPY  ON JPY.GROUPS = M.GROUPS
                        ORDER BY M.GROUPS
                    ''')
        data = [24]
        for row in CursorByName(cursor):
            data.append(row) 
        
        listData = data[1:]

        for item in listData:
            item['UZS_AVERAGE'] = '{:.2f}'.format(item['UZS_AVERAGE'])
            item['USD_AVERAGE'] = '{:.2f}'.format(item['USD_AVERAGE'])
            item['EUR_AVERAGE'] = '{:.2f}'.format(item['EUR_AVERAGE'])
            item['JPY_AVERAGE'] = '{:.2f}'.format(item['JPY_AVERAGE'])

        table = ByAverageULTable(listData)
        table.paginate(page=request.GET.get("page", 1), per_page=10)

        #table 2
        cursor.execute('''SELECT VID_KREDITOVANIYA AS TITLE, 
                        ROUND(SUM(CREDIT_PROCENT*VSEGO_ZADOLJENNOST)/SUM(VSEGO_ZADOLJENNOST),1) AS BALANS,
                        SUM(CREDIT_PROCENT*VSEGO_ZADOLJENNOST) CREDIT,
                        SUM(VSEGO_ZADOLJENNOST) LOAN
                        FROM CREDITS_REPORTDATA R
                        LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                        WHERE R.REPORT_ID = 86 AND T.SUBJ = 'P'
                        GROUP BY VID_KREDITOVANIYA
                    ''')
        data = [24]
        for row in CursorByName(cursor):
            data.append(row) 
        
        listData = data[1:]
        total_credit = sum(c['CREDIT'] for c in listData)
        total_loan   = sum(c['LOAN'] for c in listData)
        listData.append({
            'TITLE':'Итого',
            'BALANS': '{:.1f}'.format(total_credit/total_loan)
        })

        table2 = ByAverageFLTable(listData)
        table2.paginate(page=request.GET.get("page", 1), per_page=10)

        context = {
            'table': table, 
            'table2': table2, 
            'page_title': page_title}
        return render(request, 'credits/average.html', context) 
    else:
        page_title = 'Топ 10 NPL клиенты'
        query = '''SELECT R.id, 
                        CASE T.SUBJ
                            WHEN 'J' THEN SUBSTR(CREDIT_SCHET,10,8)
                            ELSE SUBSTR(INN_PASSPORT,11,9)
                        END	AS UNIQUE_CODE,
                        NAME_CLIENT AS BORROWER,
                        B.NAME AS BRANCH_NAME,
                        ROUND(SUM(VSEGO_ZADOLJENNOST)/1000000, 2) AS LOAN_BALANCE,
                        JULIANDAY('2020-02-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) AS DAY_COUNT,
                        SUM(OSTATOK_SUDEB) AS SUDEB,
                        SUM(OSTATOK_VNEB_PROSR) AS PROSR
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                    WHERE REPORT_id = 82
                    GROUP BY UNIQUE_CODE
                    HAVING DAY_COUNT > 90 OR SUDEB IS NOT NULL OR PROSR IS NOT NULL 
                    ORDER BY LOAN_BALANCE DESC
                    LIMIT 10
                '''
        
    table = ReportDataTable(ReportData.objects.raw(query))
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    context = {
        'table': table, 
        'page_title': page_title,
        'month_review': request.session['month_review']}
    return render(request, 'credits/portfolio.html', context)

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
