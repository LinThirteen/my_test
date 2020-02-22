import logging
from datetime import datetime
import json

# Create your views here.
from time import strftime, localtime

from django.db.models import Count
from django.http import HttpResponseNotFound
from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from admin.views import logger
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from . import models
from . import constants
from . import paginator_script
from users.models import Users, Detail
from haystack.views import SearchView as _SearchView

logger = logging.getLogger('django')


# 主页面
@method_decorator(cache_page(timeout=300, cache='index_page_cache'), name='dispatch')
class IndexView(View):

    def get(self, request):
        # 推荐书籍/ #排行榜
        all_stories = models.Stories.objects. \
            only('title', 'clicks', 'image_url', 'price').filter(is_delete=False)
        ranking = all_stories.order_by('-clicks')[0:constants.SHOW_RANKING_COUNT]

        # 页面右侧推荐
        recommend_frist = all_stories[0]
        recommend_secoend = all_stories[1]
        recommend_third = all_stories[2]

        # 公告
        announcement = models.Announcement.objects.filter(is_delete=False).only('content').order_by('priority', )

        # 作者写的书排序
        author_write = Users.objects.prefetch_related("detail").annotate(num=Count('stories')).order_by(
            '-num')[0:constants.SHOW_WRITE_COUNT]

        # 初始推荐8本书
        story_queryset = ranking[0:constants.SHOW_RECOEMMEND_STORY_COUNT]

        # author_write = author_write.select_related('stories')
        # 序列化每个小说作家
        author_write_list = []
        for author_detail in author_write:
            author_write_list.append({
                'author_image': author_detail.detail.image_url,
                'author_introduce': author_detail.detail.introduce,
                'author_name': author_detail.username,
            })

        return render(request, 'stories/index.html', locals())


# js异步加载轮播图和首页分类
class Banner_CategoryView(View):

    def get(self, request):
        # 按优先级排序轮播图
        banner = models.Banner.objects.select_related('stories').only('image_url', 'priority', 'stories__id',
                                                                      'stories__title', 'stories__price'). \
                     filter(is_delete=False)[0:constants.SHOW_BANNER_COUNT]

        tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)[0:constants.SHOW_TAGS_COUNT]
        # category = models.Stories.objects.filter(is_delete=False).only('title','id','image_url').order_by('-clicks')

        # 序列化输出(轮播图）
        banner_list = []
        for b in banner:
            banner_list.append({
                'image_url': b.image_url,
                'stories_id': b.stories.id,
                'stories_title': b.stories.title,
                'stories_price': b.stories.price,
            })

        # 小说分类
        tags_list = []
        for t in tags:
            tags_list.append(
                {
                    'tag_id': t.id,
                    'tag_name': t.name,
                }
            )

        # 序列化轮播图和小说分类
        data = {
            'banner': banner_list,
            'tag': tags_list,
            # 'category':category_list
        }

        return to_json_data(data=data)


# 首页滚动加载
class StoryListView(View):

    def get(self, request):

        try:
            page = int(request.GET.get('page', 1))

        except Exception as e:
            logger.error("当前页数错误:\n{}".format(e))
            page = 1

        # 取第8本到最后一本小说
        story_queryset = models.Stories.objects.select_related('tag', 'author'). \
            only('title', 'clicks', 'tag_id', 'image_url', 'author__username', 'price').filter(
            is_delete=False).order_by('-clicks')

        # 将全部小说分成每页8条
        paginator = Paginator(story_queryset, constants.SHOW_RECOEMMEND_STORY_COUNT)

        try:

            story_info = paginator.page(page)  # 第page页全部8条内容

        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logger.info("用户访问的页数大于总页数")
            story_info = paginator.page(paginator.num_pages)

        story_info_list = []

        for s in story_info:
            story_info_list.append({
                'id': s.id,
                'title': s.title,
                'image_url': s.image_url,
                'price': s.price,
                'clicks': s.clicks,

            })

        # 返回给前端数据
        data = {
            'total_pages': paginator.num_pages,  # 总页数
            'stories': story_info_list

        }
        return to_json_data(data=data)


# 点击首页分类切换
class CategoryView(View):

    def get(self, request):
        try:

            tag_id = int(request.GET.get("tag_id", ""))
            if not tag_id:
                return render(request, '500.html', )

        except Exception as e:
            logger.error("标签错误：\n{}".format(e))
            tag_id = 1

        # 获取所有小说
        category = models.Stories.objects.filter(is_delete=False, price=0, tag_id=tag_id).only('title', 'id',
                                                                                               'image_url').order_by(
            '-clicks')[0:constants.SHOW_TAGS_COUNT]

        category_stories = []
        for s in category:
            category_stories.append({
                'stories_id': s.id,
                'stories_title': s.title,
                'stories_image': s.image_url
            })

        data = {
            "category_stories": category_stories
        }
        return to_json_data(data=data)


# 分类页面
# @method_decorator(cache_page(timeout=300, cache='classify_page_cache'), name='dispatch')
class Classify(View):

    def get(self, request):

        classify_story = models.Stories.objects.select_related('tag').only('title', 'id', 'price', 'clicks',
                                        'image_url', 'tag_id', 'tag__name', 'tag_id').filter(is_delete=False)
        # 去掉重复的所有小说中全部的tag
        classify_tag = set((tag.tag_id, tag.tag.name) for tag in classify_story)
        classify_tags = []

        # 获取分类的名字和id
        for tag in classify_tag:
            classify_tags.append({
                'tag_id': tag[0],
                'tag_name': tag[1]
            })

        #获取分页数
        try:
            page = int(request.GET.get('page', 1))

        except Exception as e:
            logger.info('当前页数错误：\n{}'.format(e))
            page = 1

        try:
            tag_id = int(request.GET.get('tag_id', 0))

        except Exception as e:
            #默认为0
            logger.info('当前分类错误：\n{}'.format(e))
            tag_id = 0

        # 选定的小说类型进行过滤
        classify_story = classify_story.filter(is_delete=False, tag_id=tag_id).only('tag__name', 'tag_id', 'title',
                                                                                    "price", 'image_url', 'id',
                                                                                    'clicks') or classify_story.filter(
            is_delete=False)
        #
        # classify_story =  classify_story.filter(is_delete=False)

        # 分页
        paginator = Paginator(classify_story, constants.CLASSIFY_STORY_COUNT)
        # 选定的类型
        classify_name = classify_story.first().tag.name

        try:
            # 获取当前页面
            story_info = paginator.page(page)

        except EmptyPage:
            logger.info("用户访问的页数大于总页数")
            story_info = paginator.page(paginator.num_pages)

        # 导入自己写的分页包用来美化页面
        paginator_data = paginator_script.get_paginator_data(paginator, story_info)

        return render(request, 'stories/classify.html', locals())


# 购买书籍页面
class BuyIndexView(View):

    def get(self, request, story_id):
        if not request.user.is_authenticated:
            return render(request, 'users/login.html')

        all_stories = models.Stories.objects.select_related('author'). \
            only('title', 'clicks', 'image_url', 'author__username', 'price', 'id').filter(is_delete=False)
        ranking = all_stories.order_by('-clicks')[0:constants.SHOW_RANKING_COUNT]
        # 推荐
        recommend_frist = all_stories.order_by("-update_time")[0]
        recommend_secoend = all_stories.order_by("-update_time")[1]
        recommend_third = all_stories.order_by("-update_time")[2]

        # 公告
        announcement = models.Announcement.objects.filter(is_delete=False).only('content').order_by('priority')
        # 作者写的书排序
        author_write = Users.objects.prefetch_related("detail").annotate(num=Count('stories')).order_by(
            '-num')[0:constants.SHOW_WRITE_COUNT]

        # author_write = author_write.select_related('stories')
        author_write_list = []
        for author_detail in author_write:
            author_write_list.append({
                'author_image': author_detail.detail.image_url,
                'author_introduce': author_detail.detail.introduce,
                'author_name': author_detail.username,
            })

        # 购买书籍的详细信息
        story_detail = all_stories.filter(id=story_id).first()
        if request.user.vip:
            story_detail.price = float('%.2f' % (story_detail.price * 0.8))

        story_detail.clicks = int(story_detail.clicks) + 1
        story_detail.save(update_fields=['clicks'])

        if story_detail:
            comments = models.Comments.objects.select_related('author', 'parent', "author__detail"). \
                only('content', 'author__username', 'update_time', 'author_id',
                     'parent__author__username', 'parent__content', 'parent__update_time'). \
                filter(is_delete=False, stories_id=story_id)

            # 序列化输出
            comments_list = []
            for comm in comments:
                comments_list.append(comm.to_dict_data())

            return render(request, 'stories/buy_index.html', locals())
        else:
            # raise Http404("<新闻{}>不存在😢".format(news_id))
            return HttpResponseNotFound('<h1>Page not found</h1>')
            # return render(request, '404.html')


# 前端ajax异步处理小说评论
class StoryCommentView(View):

    def post(self, request, story_id):
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])

        if not models.Stories.objects.only('id').filter(is_delete=False, id=story_id).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg="小说不存在！")

        # 从前端获取参数
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        content = dict_data.get('content')
        if not dict_data.get('content'):
            return to_json_data(errno=Code.PARAMERR, errmsg="评论内容不能为空！")

        parent_id = dict_data.get('parent_id')
        try:
            if parent_id:
                parent_id = int(parent_id)
                if not models.Comments.objects.only('id'). \
                        filter(is_delete=False, id=parent_id, stories_id=story_id).exists():
                    return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        except Exception as e:
            logging.info("前端传过来的parent_id异常：\n{}".format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg="未知异常")

        # 保存到数据库
        story_content = models.Comments()
        story_content.content = content
        story_content.stories_id = story_id
        story_content.author = request.user
        story_content.parent_id = parent_id if parent_id else None
        story_content.save()
        return to_json_data(data=story_content.to_dict_data())


# 搜索界面
class Search(_SearchView):
    template = 'stories/search.html'

    def create_response(self):
        # 接受前台用户输入的查询的值

        kw = self.request.GET.get('q', '')
        # 如果没有值，显示热门新闻数据
        if not kw:
            show = True
            # stories = models.Stories.objects.select_related('tag').only('title', 'image_url', 'tag__id').filter(
            #     is_delete=False).order_by('-clicks')
            all_stories = models.Stories.objects.select_related('author', 'tag'). \
                only('title', 'clicks', 'image_url', 'author__username', 'price', 'tag_id', 'digest',
                     'create_time').filter(is_delete=False).order_by('-clicks')
            # 参数  分页
            paginator = Paginator(all_stories, 4)
            try:
                page = paginator.page(int(self.request.GET.get('page', 1)))
            # 假如传的不是整数
            except PageNotAnInteger:
                #  默认返回第一页
                page = paginator.page(1)
            except EmptyPage:
                page = paginator.page(paginator.num_pages).previous_page_number()

            # all_stories = models.Stories.objects.select_related('author'). \
            #     only('title', 'clicks', 'image_url', 'author__username', 'price').filter(is_delete=False)
            ranking = all_stories[0:constants.SHOW_RANKING_COUNT]

            # 推荐
            recommend_frist = all_stories.order_by("-update_time")[0]
            recommend_secoend = all_stories.order_by("-update_time")[1]
            recommend_third = all_stories.order_by("-update_time")[2]

            # 公告
            announcement = models.Announcement.objects.filter(is_delete=False).only('content').order_by('priority')

            # 作者写的书排序
            author_write = Users.objects.prefetch_related("detail").annotate(num=Count('stories')).order_by(
                '-num')[0:constants.SHOW_WRITE_COUNT]

            # author_write = author_write.select_related('stories')
            author_write_list = []
            for author_detail in author_write:
                author_write_list.append({
                    'author_image': author_detail.detail.image_url,
                    'author_introduce': author_detail.detail.introduce,
                    'author_name': author_detail.username,
                })

            return render(self.request, self.template, locals())


        # 如果有值，则输出与值相关的内容
        else:
            kw = self.request.GET.get('q', '')

            show = False

            # right_side
            all_stories = models.Stories.objects.select_related('author'). \
                only('title', 'clicks', 'image_url', 'author__username', 'price').filter(is_delete=False)
            ranking = all_stories.order_by('-clicks')[0:constants.SHOW_RANKING_COUNT]

            # 推荐
            recommend_frist = all_stories[0]
            recommend_secoend = all_stories[1]
            recommend_third = all_stories[2]

            # 公告
            announcement = models.Announcement.objects.filter(is_delete=False).only('content').order_by('priority')

            # 作者写的书排序
            author_write = Users.objects.prefetch_related("detail").annotate(num=Count('stories')).order_by(
                '-num')[0:constants.SHOW_WRITE_COUNT]

            # author_write = author_write.select_related('stories')
            author_write_list = []
            for author_detail in author_write:
                author_write_list.append({
                    'author_image': author_detail.detail.image_url,
                    'author_introduce': author_detail.detail.introduce,
                    'author_name': author_detail.username,
                })

            # 将right_的内容序列化
            content = {
                'author_write_list': author_write_list,
                'ranking': ranking,
                'recommend_frist': recommend_frist,
                'recommend_secoend': recommend_secoend,
                'recommend_third': recommend_third,
                'kw': kw

            }

            # 往父类的get_context()里面加入content里面的键值
            context = dict(self.get_context(), **content)

            return render(self.request, self.template, context)  # super().create_response()


# 免费小说阅读界面
class Read_storyView(View):

    def get(self, request, story_id):
        # 如果没有登录则重定向到登录界面
        if not request.user.is_authenticated:
            return render(request, 'users/login.html')

        # 界面的right_side信息
        all_stories = models.Stories.objects.select_related('author'). \
            only('title', 'clicks', 'image_url', 'author__username', 'price').filter(is_delete=False)

        ranking = all_stories.order_by('-clicks')[0:constants.SHOW_RANKING_COUNT]

        # 推荐
        recommend_frist = all_stories.order_by("-update_time")[0]
        recommend_secoend = all_stories.order_by("-update_time")[1]
        recommend_third = all_stories.order_by("-update_time")[2]

        # 公告
        announcement = models.Announcement.objects.filter(is_delete=False).only('content').order_by('priority',
                                                                                                    '-update_time')

        # 作者写的书排序
        author_write = Users.objects.prefetch_related("detail").annotate(num=Count('stories')).order_by(
            '-num')[0:constants.SHOW_WRITE_COUNT]

        # 序列化作者的个人信息
        author_write_list = []
        for author_detail in author_write:
            author_write_list.append({
                'author_image': author_detail.detail.image_url,
                'author_introduce': author_detail.detail.introduce,
                'author_name': author_detail.username,
            })

        #
        # chapter = models.Chapter.objects.select_related("story"). \
        #     only('id', "content", 'chapter_title', 'chapter', 'story__title', 'story__digest',
        #          'story__image_url').filter(story_id=story_id).order_by('id')

        # 获取书籍的全部章节
        chapter = models.Chapter.objects.select_related("story", "story__author"). \
            only('id', "content", 'chapter_title', 'chapter', 'story__title', 'story__digest',
                 'story__image_url', "story__author__username").filter(story_id=story_id).order_by('id')

        # 如果没有章节信息就返回500.html界面
        if not chapter:
            return render(request, 'users/500.html')

        # 取第一章节用于前端展示文章摘要和作者等信息
        chapters = chapter.first()

        story_detail = all_stories.filter(id=story_id).first()

        # 给书籍的点击量+1
        story_detail.clicks = int(story_detail.clicks) + 1
        story_detail.save(update_fields=['clicks'])

        if story_detail:
            comments = models.Comments.objects.select_related('author', 'parent'). \
                only('content', 'author__username', 'update_time',
                     'parent__author__username', 'parent__content', 'parent__update_time'). \
                filter(is_delete=False, stories_id=story_id)

            # 序列化输出
            comments_list = []
            for comm in comments:
                comments_list.append(comm.to_dict_data())

        return render(request, 'stories/read_story.html', locals())

    def post(self, request, chapter_id):

        content = models.Chapter.objects.defer("create_time", "update_time").filter(id=chapter_id).first()

        if not content:
            return to_json_data(errno=Code.PARAMERR, errmsg='章节不存在')

        data = {
            "chapter_title": content.chapter_title,
            "contents": content.content,
            "chapter": content.chapter,
        }
        return to_json_data(data=data)
