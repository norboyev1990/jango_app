from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='export-index'),
    path('exportdocx/', views.export_all_docx, name='export_all_docx'),
    
]