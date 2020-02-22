from django.urls import path, re_path

from . import views

app_name = "verifications"

urlpatterns = [
    # re_path(r'^image_codes/(?P<image_code_id>[\w-]+)/$', view=views.ImageCodeView.as_view(), name="image_code"),
    # image_code_id为uuid格式
    path('image_codes/<uuid:image_code_id>/', views.ImageCode.as_view(), name='image_code'),
    re_path('check_username/(?P<username>\w{5,20})/', views.CheckUsernameView.as_view(), name='check_username'),
    re_path('checks_username/(?P<username>.*[\u4e00-\u9fa5]+.*)/', views.CheckUsernameView.as_view(), name='checks_username'),
    path('sms_codes/', views.SmsCodesView.as_view(), name='sms_codes'),
    re_path('mobiles/(?P<Mobile_phone>1[3-9]\d{9})/', views.CheckMobileView.as_view(), name='check_mobiles'),
    re_path('forget/(?P<Mobile_phone>1[3-9]\d{9})/', views.ForgetMobileView.as_view(), name='forget_mobiles'),
    path('forget_sms_codes/', views.ForgetSmsCodesView.as_view(), name='forget_sms_codes'),



]