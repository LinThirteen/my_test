from django.urls import path
from . import views

app_name = 'doc'

urlpatterns = [
    path('',views.DocView.as_view(),name='doc'),
    path('doc_down/',views.DocdownView.as_view(),name='doc_down'),
    path('<int:doc_id>/', views.DocDownload.as_view(), name='doc_download'),


]