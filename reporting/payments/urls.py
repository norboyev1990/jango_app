from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='payments-index'),
    path('report_top/', views.report_top, name='payments-report-top'),
    path('report_all/', views.report_all, name='payments-report-all'),
    path('report_all_test/', views.report_all_test, name='payments-report-test'),
    path('report_byclient/', views.report_by_client, name='payments-report-byclient'),
    path('report_bycurrency/', views.report_by_currency, name='payments-report-bycurrency'),
]