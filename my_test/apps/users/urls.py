from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('start/',views.StartView.as_view(),name='start'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/',views.RegisterView.as_view(),name='register'),
    path('forget_login/',views.Forget_Login_View.as_view(),name='forget_login'),
    path('logout/',views.LoginoutView.as_view(),name='logout'),


    path('detail/',views.DetailView.as_view(),name='detail'),
    path('detail_phone/', views.DetailPhoneView.as_view(), name='detail_phone'),
    path('detail_put/', views.DetailPutView.as_view(), name='detail_put'),


    path('upload_token/', views.UploadToken.as_view(), name='upload_token'),  # 七牛云上传图片需要调用token
    path('shopping/', views.ShoppingView.as_view(), name='shopping'),


    path('write/', views.WriteView.as_view(), name='write'),
    path('write_edit/<int:stories_id>/', views.WriteEditView.as_view(), name='write_edit'),
    path('write_chapter/<int:chapter_id>/', views.WriteEditView.as_view(), name='write_chapter'),


    path('chapter_edit/<int:chapter_id>/', views.WriteEditView.as_view(), name='chapter_edit'),
    path('chapter_add/<int:stories_id>/', views.Chapter_AddView.as_view(), name='chapter_add'),

    path('story_publish/', views.StoryPublishView.as_view(), name='story_publish'),
    path('story_change/<int:story_id>/', views.StoryChangeView.as_view(), name='story_change'),
    #
    path('story_put/<int:stories_id>/', views.StoryChangeView.as_view(), name='story_put'),
    path('story_post/', views.StoryChangeView.as_view(), name='story_post'),


    # path('text/', views.Text.as_view(), name='text'),

]