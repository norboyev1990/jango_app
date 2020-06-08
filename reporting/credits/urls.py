from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('test/', views.test, name='test'),
    path('upload/', views.upload, name='upload'),
    path('report/', views.ReportDataListView.as_view())
]