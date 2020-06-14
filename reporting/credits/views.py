from django_tables2 import SingleTableView
from .tables import ReportDataTable, OverallInfoTable, ByTermTable, BySubjectTable
from django.shortcuts import render
from .models import ListReports, ReportData
from django.db import connection
from openpyxl import load_workbook
import pandas as pd
from pandas import DataFrame
import numpy as np
from datetime import datetime
# Create your views here.

class CursorByName():
    def __init__(self, cursor):
        self._cursor = cursor
    
    def __iter__(self):
        return self

    def __next__(self):
        row = self._cursor.__next__()

        return { description[0]: row[col] for col, description in enumerate(self._cursor.description) }
        
npl_clients_list_yur = []
npl_clients_list_fiz = []
sudeb_clients_list_yur = []
sudeb_clients_list_fiz = []
prosr_clients_list_yur = []
prosr_clients_list_fiz = []
bad_loan_list_yur = []
bad_loan_list_fiz = []

def index(request):
    return render(request, 'credits/index.html')

def set_value(row_number, assigned_value): 
        return assigned_value[row_number]
def sroki(srok):
    if srok > 10:
        return "свыше 10 лет"
    elif (7 <= srok <= 10):
        return "от 7-ми до 10 лет"
    elif (5 <= srok <= 7):
        return "от 5-ти до 7 лет"
    elif (2 < srok <= 5):
        return "от 2-х до 5 лет"
    else:
        return "до 2-х лет"

def korzina(prosrochka):
    if (prosrochka == 0):
        return 'станд'
    elif (prosrochka > 90):
        return '90+'
    elif (prosrochka > 60):
        return '61-90'
    elif (prosrochka > 30):
        return '31-60'
    else:
        return '0-30'

def label_race_two(row):
    if row['unique_code'] in (npl_clients_list_yur) and row['yur_fiz'] == 'ЮЛ':
        return 'Yes'
    if row['passport'] in (npl_clients_list_fiz) and row['yur_fiz'] == 'ФЛ':
        return 'Yes'
    if row['unique_code'] in (sudeb_clients_list_yur) and row['yur_fiz'] == 'ЮЛ':
        return 'Yes'
    if row['passport'] in (sudeb_clients_list_fiz) and row['yur_fiz'] == 'ФЛ':
        return 'Yes'
    if row['unique_code'] in (prosr_clients_list_yur) and row['yur_fiz'] == 'ЮЛ':
        return 'Yes'
    if row['passport'] in (prosr_clients_list_fiz) and row['yur_fiz'] == 'ФЛ':
        return 'Yes'
    return 'No'

def label_race(row):
        if row['unique_code'] in (bad_loan_list_yur) and row['yur_fiz'] == 'ЮЛ':
            return 'Yes'
        if row['passport'] in (bad_loan_list_fiz) and row['yur_fiz'] == 'ФЛ':
            return 'Yes'
        return 'No'
def date_check(date):
    res = None
    if (pd.notnull(date)):
        res = pd.to_datetime(date)
    return res
def number_check(number):
    res = None
    if (pd.notnull(number)):
        res = number
    return res
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
    
def test(request):
    #wb = load_workbook(filename = 'media/excel/january.xlsx')
    #sheet_ranges = wb['report']
    # data = pd.read_excel (r'media/excel/january.xlsx', dtype={"МФО": 'str', 'КодРег': 'str', 'БалансСчет':'str', 'КодВал': 'str', 'ИНН/Паспорт': 'str' })
    data = pd.DataFrame(list(ReportData.objects.filter(REPORT_id=86).values()))
    data.columns = ['id', 'report_id', 'number', 'code_reg', 'mfo', 'name_client', 'balans_schet', 'credit_schet', 'date_resheniya', 'code_val', 'sum_dog_nom', 'sum_dog_ekv', 'date_dogovor', 'date_factual', 'date_pogash', 'srok', 'dog_number_date', 'credit_procent', 'prosr_procent', 'ostatok_cred_schet', 'ostatok_peresm', 'date_prodl', 'date_pogash_posle_prodl', 'ostatok_prosr', 'date_obraz_pros', 'ostatok_sudeb', 'kod_pravoxr_org', 'priznak_resheniya', 'date_pred_resh', 'vsego_zadoljennost', 'class_kachestva', 'ostatok_rezerv', 'ostatok_nach_prcnt', 'ostatok_nach_prosr_prcnt', 'ocenka_obespecheniya', 'obespechenie', 'opisanie_obespechenie', 'istochnik sredtsvo', 'vid_kreditovaniya' , 'purpose_credit', 'vishest_org_client', 'otrasl_kreditovaniya', 'otrasl_clienta', 'class_kredit_spos', 'predsedatel_kb', 'adress_client', 'un_number_contract', 'inn_passport', 'ostatok_vneb_prosr', 'konkr_nazn_credit', 'borrower_type', 'svyazanniy', 'maliy_biznes', 'register_number', 'oked', 'code_conract']
    keys = ['00069','00073','00972','00120','01027','00140','00194','00206','01021','00231','00264','01004','00358','00373','00416',
            '00417','00873','00958','00963','00969','00411','00539','00631','00904','00971','00581','01169','00625']

    values = ['Андижанский', 'Асакинский', 'Фарход', 'Бухарский', 'Бухарский г','Джизакский','Кашкадарьинский',
            'Навоийский','Зарафшанский','Наманганский','Самаркандский','Афросиёб','Сурхандарьинский','Сирдарьинский','Ташкентский г.', 'Автотранспортный',
            'Головной офис','Сергелийский','Юнусабадский','Шайхантахурский','Ташкентский обл.','Ферганский','Кокандский','Олтиарикский', 'Маргиланский',
            'Хорезмский','Хозараспский', 'Каракалпакский']
    event_dictionary = dict(zip(keys, values))
    data.drop(data.loc[data['mfo'] == 'МФО'].index, inplace=True)
    data['Filial'] = data['mfo'].apply(set_value, args =(event_dictionary, ))
    data['balans_schet'] = data['balans_schet'].astype('str')
    dict_client_type = {'12401': 'ЮЛ' , '12501': 'ФЛ', '12503': 'ФЛ', '12521': 'ФЛ', '12601': 'ИП', '12621': 'ИП', '12701': 'ЮЛ' ,
       '12901': 'ЮЛ', '13001': 'ЮЛ', '13101': 'ЮЛ', '13121': 'ЮЛ', '13201': 'ЮЛ', '14301': 'ЮЛ', '14403': 'ЮЛ',
       '14801': 'ЮЛ', '14901': 'ФЛ', '14902': 'ФЛ', '14903': 'ФЛ', '14921': 'ФЛ', '15001': 'ИП', '15021': 'ИП',
       '15101': 'ЮЛ', '15201': 'ЮЛ', '15301': 'ЮЛ', '15321': 'ЮЛ', '15401': 'ЮЛ', '15501': 'ЮЛ', '15521': 'ЮЛ',
       '15607': 'ЮЛ', '15609': 'ЮЛ', '15613': 'ЮЛ'}
    data['status_client'] = data['balans_schet'].apply(set_value, args =(dict_client_type, ))

    dict_valyuta = {'000' : 'UZS', '840': 'USD', '978': 'EUR', '392': 'JPY'}
    data['valyuta'] = data['code_val'].apply(set_value, args = (dict_valyuta, ))
    # Преобразовать столбцы строкового типа в формат даты и времени
    data['date_pogash'] = pd.to_datetime(data['date_pogash'])
    data['date_dogovor'] = pd.to_datetime(data['date_dogovor'])
    data['date_pogash_posle_prodl'] = pd.to_datetime(data['date_pogash_posle_prodl'])
    # Добавление нового столбцы "Срок кредита" и "Сроки"
    data['srok_kredita'] = np.where(data['date_pogash_posle_prodl'].isna(), pd.to_numeric((data['date_pogash'] - data['date_dogovor']) / np.timedelta64(1, 'Y')), pd.to_numeric((data['date_pogash_posle_prodl'] - data['date_dogovor']) / np.timedelta64(1, 'Y')))
    data['srok_kredita'] = data['srok_kredita'].round(1)
    data['sroki'] = data.apply(lambda x: sroki(x['srok_kredita']), axis=1)
    # Изменить тип
    data['vsego_zadoljennost'] = data['vsego_zadoljennost'].astype('float64')
    data['sum_dog_ekv'] = data['sum_dog_ekv'].astype('float64')
    data['ostatok_peresm'] = data['ostatok_peresm'].astype('float64')
    # Добавление нового столбца Код
    data['Code'] = data['otrasl_clienta'].str.split('-', expand=True)[0]
    data.loc[:, 'Code'][0:2]
    data['Code'] = data['otrasl_clienta'].str[:2]
    data['Code'] = data['Code'].str.replace('0-', '0')
    data['Code'] = data['Code'].astype('int64')
    # Разделить Инн/паспорт
    data[['inn','passport']] = data['inn_passport'].str.split(",",expand=True,)
    #
    keys = ['0', '99', '71', '15', '17','13','84','61','87','90','21','91','52','14','82','18','16','92','81','66','80',
            '19','22','51','63', '83','72','12', '31','29','11','85','93','96','98','97','95','69','95']

    values = [ 'Прочие','ФЛ','Торговля','Промышленность','Промышленность','Промышленность','Прочие','Строительство','Прочие','ЖКХ',
            'Селськое хозяйство','Прочие','Транспорт','Промышленность','Прочие','Промышленность','Промышленность','Прочие','Заготовки',
            'Строительство','Прочие','Промышленность','Селськое хозяйство','Транспорт','Строительство','Прочие','Торговля','Промышленность',
            'Прочие','Селськое хозяйство','Промышленность','Прочие','Прочие','Прочие','Прочие','Прочие','Прочие','Строительство','Строительство']
    segment_dictionary = dict(zip(keys, values))
    #
    data['Code'] = data['Code'].astype('str')
    data['segment'] = data['Code'].apply(set_value, args =(segment_dictionary, ))
    data['ostatok_peresm'] = data['ostatok_peresm'].fillna(0)
    data['ostatok_peresm'] = data['ostatok_peresm'].astype('float64')
    data['credit_schet']  = data['credit_schet'].astype('str')
    #Добавление нового столбца "Уникальный код"
    data['unique_code'] = data['credit_schet'].str[9:17]
    data['yur_fiz'] = np.where(data['status_client'] == 'ИП', 'ЮЛ', data['status_client'])
    fiz_data = data[data['yur_fiz'] == 'ФЛ']
    yur_data = data[data['yur_fiz'] == 'ЮЛ']
    # Добавление нового столбца "Просроченные дни"
    data['date_obraz_pros'] = pd.to_datetime(data['date_obraz_pros'])
    data['prosrochka_dni'] = round(pd.to_numeric((pd.to_datetime('2020-01-01') - data['date_obraz_pros']) / np.timedelta64(1, 'D')))
    data['prosrochka_dni'] = data['prosrochka_dni'].fillna(0)
    data['prosrochka_dni'] = data['prosrochka_dni'].astype('int64')
    # Добавление нового столбца "Сегмент бизнеса"
    data['segment_biznesa'] = data['status_client'].apply(lambda x: 'РБ' if x == 'ФЛ' else 'МСБ')
    df_segment_biznesa_yur = yur_data[['unique_code', 'sum_dog_ekv', 'status_client']]

    group_clients_yur = df_segment_biznesa_yur.groupby(['unique_code', 'status_client'], as_index = False).sum()
    greater_seven_mlrd_yur = group_clients_yur[group_clients_yur['sum_dog_ekv'] > 7e10]
    less_seven_mlrd_yur = group_clients_yur[group_clients_yur['sum_dog_ekv'] < 7e10]

    greater_seven_mlrd_yur = greater_seven_mlrd_yur['unique_code'].reset_index()
    greater_seven_mlrd_lst_yur = greater_seven_mlrd_yur['unique_code'].tolist()

    df_segment_biznesa_fiz = fiz_data[['passport', 'sum_dog_ekv', 'status_client']]

    group_clients_fiz = df_segment_biznesa_fiz.groupby(['passport', 'status_client'], as_index = False).sum()
    greater_seven_mlrd_fiz = group_clients_fiz[group_clients_fiz['sum_dog_ekv'] > 7e10]
    less_seven_mlrd_fiz = group_clients_fiz[group_clients_fiz['sum_dog_ekv'] < 7e10]

    greater_seven_mlrd_fiz = greater_seven_mlrd_fiz['passport'].reset_index()
    greater_seven_mlrd_lst_fiz = greater_seven_mlrd_fiz['passport'].tolist()

    data['segment_business'] = np.where((data['unique_code'].isin(greater_seven_mlrd_lst_yur)), 'КБ', data['segment_biznesa'])
    data = data.drop(['segment_biznesa'], axis=1)
    # Добавление нового столбца "Корзины"
    data['korziny'] = data.apply(lambda x: korzina(x['prosrochka_dni']), axis=1 )
    # Добавление нового столбца "NPL + sudeb"
    npl_clients = data[data['korziny']=='90+']
    npl_clients_list_yur = npl_clients['unique_code'].tolist()
    npl_clients_list_fiz = npl_clients['passport'].tolist()
    data['ostatok_sudeb'] = data['ostatok_sudeb'].fillna(0)
    sudeb_clients = data[data['ostatok_sudeb'] != 0]
    sudeb_clients_list_yur = sudeb_clients['unique_code'].tolist()
    sudeb_clients_list_fiz = sudeb_clients['passport'].tolist()
    data['ostatok_vneb_prosr'] = data['ostatok_vneb_prosr'].fillna(0)
    prosr_clients = data[data['ostatok_vneb_prosr'] != 0]
    prosr_clients_list_yur = prosr_clients['unique_code'].tolist()
    prosr_clients_list_fiz = prosr_clients['passport'].tolist()

    data['npl + sudeb'] = data.apply(lambda row: label_race_two(row), axis=1)

    # Добавление нового столбца "Токсичные кредиты"
    data['bad_loans'] = data.apply(lambda x: 'Yes' if (x['ostatok_peresm'] != 0 and x['npl + sudeb'] != 'Yes' ) else 'No', axis=1)
    bad_loans = data[data['bad_loans']== 'Yes']
    bad_loan_all_yur = bad_loans['unique_code'].reset_index()
    bad_loan_list_yur = bad_loan_all_yur['unique_code'].tolist()
    bad_loan_all_fiz = bad_loans['passport'].reset_index()
    bad_loan_list_fiz = bad_loan_all_fiz['passport'].tolist()

    data['bad_loans']= data.apply(lambda row: label_race(row),axis=1)
    #data = data.drop(['bad_loan'], axis=1)

    bad = data[data['bad_loans'] == 'Yes']
    good = data[data['bad_loans'] == 'No']

    data['ostatok_prosr'] = data['ostatok_prosr'].astype('float64')
    data['ostatok_prosr'] = data['ostatok_prosr'].fillna(0)
    group_npl = data[data['npl + sudeb'] == 'Yes']
    npl_clients = data[data['korziny'] == '90+']
    # Инвест проект
    data['priznak_invest_proekt'] =  data['obespechenie'].str[:2] 
    invest_proekt= data[data['priznak_invest_proekt'] == '42']
    invest_proekt_list = invest_proekt['unique_code'].tolist()
    invest_proekt_list2 = invest_proekt['passport'].tolist()
    data['yur_fiz_invest'] = np.where(data['status_client'] == 'ИП', 'ЮЛ', data['status_client'])
    data['yur_fiz_invest'] = np.where((data['unique_code'].isin(invest_proekt_list)), 'Инвест. проект', data['yur_fiz_invest'])
    top_clients = data.groupby(['name_client', 'Filial'])['sum_dog_ekv'].sum().to_frame(name = 'sum').reset_index()
    top_clients = top_clients.sort_values(by='sum', ascending=False).reset_index()

    # ТОП-10 заемщиков (NPL)
    group_npl = npl_clients.groupby(['unique_code', 'name_client', 'Filial'])['vsego_zadoljennost'].sum().to_frame(name = 'sum').reset_index()
    top_npl = group_npl.sort_values(by='sum', ascending=False).reset_index()
    top_npl = top_npl.drop('index', axis=1)
    top_npl.columns = ['Уникальный код', 'Наименование заёмщика', 'Филиал', 'Остаток кредита']
    top_npl_clients = top_npl.head(10)
    top_npl_clients['Остаток кредита'] = top_npl_clients['Остаток кредита'] / 1000000

    group_prosr = data.groupby(['name_client', 'Filial'])['ostatok_nach_prosr_prcnt'].sum().to_frame(name = 'sum').reset_index()
    top_prosr = group_prosr.sort_values(by='sum', ascending=False).reset_index()
    top_prosr = top_prosr.drop('index', axis=1)
    top_prosr.columns = ['Наименование заёмщика', 'Филиал', 'Остаток кредита']
    top_prosr_clients = top_prosr.head(10)
    top_prosr_clients['Остаток кредита'] = top_prosr_clients['Остаток кредита'] /1000000

    context = {'mylist': top_prosr_clients.to_html(classes='table table-striped').replace('border="1"','border="0"')}
    return render(request, 'credits/test.html', context)

def portfolio(request):
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
                            (NPL_LOAN+TOX_LOAN)/TOTALS AS WEIGHT,
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
    context = {'table': table, 'page_title': page_title}
    return render(request, 'credits/portfolio.html', context)

class ReportDataListView(SingleTableView):
    model = ReportData
    table_class = ReportDataTable
    template_name = 'credits/report.html'
