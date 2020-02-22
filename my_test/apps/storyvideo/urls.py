from django.urls import path
from .import views

app_name = 'storyvideo'

urlpatterns = [
    path('', views.storyvideo_list, name='storyvideo'),
    path('<int:video_id>/', views.VideoDetailView.as_view(), name='video_detail'),

]