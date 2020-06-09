from django_tables2 import SingleTableView
from .tables import ReportDataTable
from django.shortcuts import render
from .models import ListReports, ReportData

from openpyxl import load_workbook
import pandas as pd
from pandas import DataFrame
import numpy as np
from datetime import datetime
# Create your views here.

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
    data = pd.DataFrame(list(ReportData.objects.all().values()))
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
    query = '''WITH RECURSIVE 
                UNIQUES(id, credit_schet) as (
                    select t.id, SUBSTR(t.credit_schet,10,8)  from credits_reportdata t
                    left join credits_clienttype ct on t.balans_schet = ct.code
                    where (julianday('2020-01-01') - julianday(t.date_obraz_pros) > 90
                        or t.ostatok_sudeb is not null or t.ostatok_vneb_prosr is not null)
                        and ct.SUBJ = 'J'
                    UNION
                    select t2.id, UNIQUES.credit_schet from credits_reportdata t2, UNIQUES
                    where SUBSTR(t2.credit_schet,10,8) = UNIQUES.credit_schet

                    
                )
                SELECT RD.ID,
                    UN.credit_schet AS UNIQUE_CODE,
                    RD.NAME_CLIENT,
                    SUM(RD.VSEGO_ZADOLJENNOST) AS BALANCE
                FROM UNIQUES UN
                LEFT JOIN CREDITS_REPORTDATA RD ON RD.ID = UN.id
                GROUP BY UNIQUE_CODE, RD.NAME_CLIENT, MFO
                ORDER BY BALANCE DESC
                LIMIT 10
                
            '''
    table = ReportDataTable(ReportData.objects.raw(query))
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    context = {'table': table}
    return render(request, 'credits/portfolio.html', context)

class ReportDataListView(SingleTableView):
    model = ReportData
    table_class = ReportDataTable
    template_name = 'credits/report.html'
