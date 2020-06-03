from django.shortcuts import render
from openpyxl import load_workbook
import pandas as pd
from pandas import DataFrame
# Create your views here.
def index(request):
    return render(request, 'credits/index.html')
def test(request):
    #wb = load_workbook(filename = 'media/excel/january.xlsx')
    #sheet_ranges = wb['report']
    df = pd.read_excel (r'media/excel/january.xlsx')
    context = {'mylist': df.to_html(encoding="true"), 'type': type(df)}
    return render(request, 'credits/test.html', context)