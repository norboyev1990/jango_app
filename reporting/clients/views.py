from django.shortcuts import render
from .queries import *
from .models import *
from .tables import *

# Create your views here.
def index(request):
    table = ClientsTable(Clients.objects.raw(Query.findClients(), [86]))
    table.paginate(page=request.GET.get("page", 1), per_page=10)   
    context = {
        'table': table
    }
    return render(request, 'clients/index.html', context)

def view(request):
    return render(request, 'clients/view.html')