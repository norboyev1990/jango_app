import pandas as pd
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db import connection
from .queries import *
from .models import *
from .tables import *


def setReviewMonthInSession(request):
    if (request.POST.get('data_month')):
        request.session['data_month'] = request.POST.get('data_month')
        HttpResponseRedirect(request.path_info)

    if 'data_month' not in request.session:
        request.session['data_month'] = '2020-04'

def index(request):
    setReviewMonthInSession(request)
    sMonth = pd.to_datetime(request.session['data_month'])

    table = ClientsTable(Clients.objects.raw(Query.findClients(), [4]))
    table.paginate(page=request.GET.get("page", 1), per_page=10)   
    context = {
        'table': table
    }
    return render(request, 'clients/index.html', context)

def view(request, id):
    client = Clients.objects.raw(Query.findClientByID())
    context = {
        'client': client
    }
    return render(request, 'clients/view.html', context)