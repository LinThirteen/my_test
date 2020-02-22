from django.urls import path
from . import views

# app的名字
app_name = 'admin'

   #模板中找的是name=而不是‘xx/'
urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),  # 将这条路由命名为index


    path('tags/', views.Stories_TagsView.as_view(), name='tags'),
    path('tags/<int:tag_id>/', views.Stories_TagsView.as_view(), name='tags'),

    path('announcement/', views.AnnouncementView.as_view(), name='announcement'),
    path('announcement_update/<int:announcement_id>/', views.AnnouncementView.as_view(), name='announcement_update'),

    path('fdfs/images/', views.StoryUploadImage.as_view(), name='upload_image'),


    path('banner/', views.BannerView.as_view(), name='banner'),
    path('banners/<int:banner_id>/', views.BannerEditView.as_view(), name='banners_edit'),
    path('banners/add/', views.BannerAddView.as_view(), name='banners_add'),

    path('stories/', views.StoryManageView.as_view(), name='stories_manage'),
    path('stories/<int:stories_id>/', views.StoryManageView.as_view(), name='stories_manage'),
    path('stories_publish/', views.StoryPublishView.as_view(), name='stories_publish'),
    path('stories_publish/<int:stories_id>/', views.StoryPublishView.as_view(), name='stories_publish'),
    path('stories_edit/<int:stories_id>/', views.StoryEditView.as_view(), name='stories_edit'),


    path('normal_user/', views.NormalView.as_view(), name='normal_user'),
    path('normal_user/<int:user_id>/', views.NormalView.as_view(), name='normal_user'),

    path('vip_user/', views.VIPView.as_view(), name='vip_user'),
    path('vip_user/<int:user_id>/', views.VIPView.as_view(), name='vip_user'),

    path('illegal_user/', views.IllegalView.as_view(), name='illegal_user'),
    path('illegal_user/<int:user_id>/', views.IllegalView.as_view(), name='illegal_user'),
    
    path('docs_manage/', views.DownloadView.as_view(), name='docs_manage'),
    path('docs_manage/<int:stories_id>/', views.DownloadView.as_view(), name='docs_manage'),
    path('docs_put/', views.DownloadPubView.as_view(), name='docs_put'),


    path('news_by_tagid/<int:story_id>/news/', views.DownloadStoryView.as_view(), name='news_by_tagid'),
    path('story_by_tagid/<int:tag_id>/story/', views.DownloadStoryView.as_view(), name='story_by_tagid'),


    path('video_manage/', views.VideoManageView.as_view(), name='video_manage'),
    path('video_edit/<int:video_id>/', views.VideoEditView.as_view(), name='video_edit'),
    path('video_put/', views.VideoPubView.as_view(), name='video_put'),

    # path('news/pub/', views.NewsPubView.as_view(), name='news_pub'),
    # path('news/images/', views.NewsUploadImage.as_view(), name='upload_image'),
    path('token/', views.UploadToken.as_view(), name='upload_token'),  # 七牛云上传图片需要调用token

    path('docs/files/', views.DocsUploadFile.as_view(), name='upload_text'),     #小说下载

    path('order_form/', views.OrderFormView.as_view(), name='order_form'),
    path('order_list/', views.OrederListView.as_view(), name='order_list'),
    path('order_delete/<int:goods_id>/', views.OrederListView.as_view(), name='order_delete'),
    path('order_put/<int:goods_id>/', views.OrederListView.as_view(), name='order_put'),



    path('groups/', views.GroupsManageView.as_view(), name='groups_manage'),
    path('groups/<int:group_id>/', views.GroupsEditView.as_view(), name='groups_edit'),
    path('groups/add/', views.GroupsAddView.as_view(), name='groups_add'),

    path('users/', views.UsersManageView.as_view(), name='users_manage'),
    path('users/<int:user_id>/', views.UsersEditView.as_view(), name='users_edit'),

    # path('upload_token/', views.UploadToken.as_view(), name='upload_token'),

]

