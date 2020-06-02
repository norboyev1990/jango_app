from django.shortcuts import render
from django.views import generic

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'credits/index.html'
    context_object_name = 'latest_question_name'