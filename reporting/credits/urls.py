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
    path('exportall/', views.export_all_tables, name='export-all-tables'),
    
    path('search/', views.search, name='search-client'),
    path('contracts/', views.contracts, name='contract-list'),
    path('contracts/<int:id>/', views.contract_detail, name='contract-detail'),
    path('upload/', views.upload, name='upload'),
    path('uploadex/', views.upload_excel, name='upload-excel'),
    path('export/', views.test_export, name='export'),
    path('client_page/', views.client_page, name='client_page'),
    

    

]