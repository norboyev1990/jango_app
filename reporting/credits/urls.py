from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('overview/', views.npls, name='overview'),
    path('npls/', views.npls, name='npl-list'),
    path('toxics/', views.toxics, name='toxic-list'),
    path('overdues/', views.overdues, name='overdue-list'),
    path('indicators/', views.indicators, name='general-indicators'),
    path('byterms/', views.byterms, name='break-by-terms'),
    path('bysubjects/', views.bysubjects, name='break-by-subjects'),
    path('bysegments/', views.bysegments, name='break-by-segments'),
    path('bycurrency/', views.bycurrency, name='break-by-currency'),
    path('bybranches/', views.bybranches, name='break-by-branches'),
    path('bypercentagent/', views.bypercentage_national, name='break-by-percentage-national'),
    path('bypercentagefr/', views.bypercentage_foreign, name='break-by-percentage-foreign'),
    path('bypercentagentul/', views.bypercentage_national_ul, name='break-by-percentage-national-ul'),
    path('bypercentagefrul/', views.bypercentage_foreign_ul, name='break-by-percentage-foreign-ul'),
    path('byaverageweightul/', views.byaverageweight_ul, name='break-by-average-weight-ul'),
    path('byaverageweightfl/', views.byaverageweight_fl, name='break-by-average-weight-fl'),
    path('byretailproduct/', views.byretailproduct, name='break-by-retail-product'),
    path('byoverduebranch/', views.byoverduebranch, name='break-by-overdue-branch'),
    path('exportall/', views.export_all_tables, name='export-all-tables'),

    path('uploadex/', views.upload_excel, name='upload-excel'),
    path('uploadprs/', views.upload_prs, name='upload-prs'),
    path('uploadpay/', views.upload_payments, name='upload-payments'),
    path('uploadclients/', views.upload_problems, name='upload-problems'),
]