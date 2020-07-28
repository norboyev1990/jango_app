import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from .functions import CursorByName
from .queries import Query
from django.db import connection
from .tables import *
import json

# Create your views here.
def index(request):
    return HttpResponse('Payments Page')

def report_top(request):

    sMonth = pd.to_datetime(request.session['data_month'])
    
    cursor = connection.cursor()
    cursor.execute(Query.report_top())

    dictionary = {}
    for row in CursorByName(cursor):
        info = dictionary.get(row['UNIQUE_CODE'])
        info = row if info is None else info
        info.update({'COL%s' % row['PERIOD_2']: row['TOTAL']})
        info.update({'NAT%s' % row['PERIOD_2']: row['NATIONAL']})
        dictionary.update({row['UNIQUE_CODE']: info})
    
    list = []
    for row in dictionary:
        list.append(dictionary[row])


    table = ReportTopTable(list)
    context = {'table': table, 'title': 'Отчет #1'}
    return render(request, 'payments/view.html', context)

def report_all(request):

    sMonth = pd.to_datetime(request.session['data_month'])
    cursor = connection.cursor()
    cursor.execute(Query.report_all())

    dictionary = {}
    for row in CursorByName(cursor):
        info = dictionary.get(row['SCHET'])
        info = row if info is None else info
        info.update({'COL%s' % row['PERIOD_1']: row['TOTAL']})
        dictionary.update({row['SCHET']: info})
    
    list = []
    for row in dictionary:
        list.append(dictionary[row])


    table = AllReportTable(list)
    context = {'table': table, 'title': 'Отчет #2'}
    return render(request, 'payments/view.html', context)

def report_all_test(request):

    sMonth = pd.to_datetime(request.session['data_month'])
    cursor = connection.cursor()
    cursor.execute(Query.report_all())

    dictionary = {}
    for row in CursorByName(cursor):
        info = dictionary.get(row['PERIOD_1'])
        info = row if info is None else info
        info.update({'COL%s' % row['SCHET']: row['TOTAL']})
        dictionary.update({row['PERIOD_1']: info})
    
    list = []
    for row in dictionary:
        list.append(dictionary[row])


    table = AllReportTable2(list)
    context = {'table': table, 'title': 'Отчет #2'}
    return render(request, 'payments/view.html', context)

def report_by_client(request):

    sMonth = pd.to_datetime(request.session['data_month'])
    cursor = connection.cursor()
    cursor.execute(Query.report_by_client())

    dictionary = {}
    for row in CursorByName(cursor):
        info = dictionary.get(row['IS_FL'])
        info = row if info is None else info
    
        info.update({'NAT%s' % row['PERIOD_2']: row['NATION']})
        info.update({'COL%s' % row['PERIOD_2']: row['TOTAL']})
        dictionary.update({row['IS_FL']: info})
    
    list = []
    for row in dictionary:
        list.append(dictionary[row])


    table = ReportByClientTable(list)
    context = {'table': table, 'title': 'Отчет #3'}
    return render(request, 'payments/view.html', context)

def report_by_currency(request,crncy='000'):

    sMonth = pd.to_datetime(request.session['data_month'])
    cursor = connection.cursor()
    cursor.execute(Query.report_by_currency(),[crncy])

    dictionary = {}
    for row in CursorByName(cursor):
        info = dictionary.get(row['SCHET'])
        info = row if info is None else info
    
        info.update({'COL%s' % row['PERIOD_1']: row['TOTAL']})
        dictionary.update({row['SCHET']: info})
    
    list = []
    for row in dictionary: 
        list.append(dictionary[row])


    table = AllReportTable(list)
    context = {'table': table, 'title': 'Отчет #4'}
    return render(request, 'payments/view.html', context)