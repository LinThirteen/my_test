from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('index/',views.IndexView.as_view(),name='index'),
    path('index/banner/', views.Banner_CategoryView.as_view(), name='banner'),
    path('category/', views.CategoryView.as_view(), name='category'),
    path('index_story/', views.StoryListView.as_view(), name='index_story'),
    path('classify/',views.Classify.as_view(),name='classify'),
    path('buy_index/<int:story_id>/', views.BuyIndexView.as_view(), name='buy_index'),

    path('story_comment/<int:story_id>/', views.StoryCommentView.as_view(), name='story_comment'),

    path('search/', views.Search(), name='search'),

    path('read/<int:story_id>/', views.Read_storyView.as_view(), name='read'),
    path('read_chapter/<int:chapter_id>/', views.Read_storyView.as_view(), name='read_chapter'),

    # path('buy_index/', views.BuyIndexView.as_view(), name='buy_indexs'),<int:story_id>

]