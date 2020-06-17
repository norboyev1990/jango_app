from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('npls/', views.npls, name='npl-list'),
    path('toxics/', views.toxics, name='toxic-list'),
    path('overdues/', views.overdues, name='overdue-list'),
    path('indicators/', views.indicators, name='general-indicators'),
    path('byterms/', views.byterms, name='break-by-terms'),
    path('bysubjects/', views.bysubjects, name='break-by-subjects'),
    path('bysegments/', views.bysegments, name='break-by-segments'),
    path('bycurrency/', views.bycurrency, name='break-by-currency'),
    path('bybranches/', views.bybranches, name='break-by-branches'),
    path('bypercentage/', views.bypercentage, name='break-by-percentage'),
    path('byaverageweight/', views.byaverageweight, name='break-by-average-weight'),
    path('byretailproduct/', views.byretailproduct, name='break-by-retail-product'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('upload/', views.upload, name='upload'),
    path('export/', views.test_export, name='export'),
]