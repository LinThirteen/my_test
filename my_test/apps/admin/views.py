import json
import logging
import qiniu
import random
import re


from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode

from admin import constants, paginator_script
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse, Http404

from django.shortcuts import render
from django.views import View
from django.db.models import Count, Sum, Max
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

from django.contrib.auth.models import Group, Permission
# from my_project import settings
from utils.fastdfs.fdfs import FDFS_Client
# from . import constants

from . import forms
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from utils.secrets import qiniu_secret_info
from my_test import settings
from stories.models import Tag, Announcement, Banner, Stories
from storyvideo.models import Storyvideo
from doc.models import Doc
from .models import OrderForm
from users import models
from utils.fastdfs.fdfs import FDFS_Client
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map


logger = logging.getLogger('django')


#后端主页面
class IndexView(LoginRequiredMixin,View):  # LoginRequiredMixin,
    """
    """
    #没登录就重定向到登录界面
    login_url = 'users:login'
    redirect_field_name = 'next'
    def get(self, request):
        #对后端数据处理进行组包用于可以化界面的展示
        # 人数&地址
        all_value = models.Users.objects.select_related("detail")
        join_time = all_value.filter(username=request.user).values('date_joined').first()
        join_time = join_time['date_joined'].strftime('%Y/%m/%d') if all_value else ''

        # 小说点击量&分点击量
        # 类总点击量
        tags_all = Tag.objects.select_related("stories").filter(is_delete=False)
        tags_list = list(tags_all.values('id', 'name').annotate(clicks=Sum("stories__clicks")). \
                         filter(is_delete=False).order_by('-clicks', 'update_time'))[0:10]
        #类分点击量
        rank_list = []
        for i in tags_list:
            rank_all = list(tags_all.values("name", "id","stories__title","stories__clicks")\
                .filter(is_delete=False, id=int(i["id"])).order_by("-stories__clicks"))[0:6]
            rank_list.append(rank_all)     #每类书的前6部小说

        ranks_list = []
        for j in rank_list:
            for clicks in j:
                ranks_list.append([str(clicks["name"]),str(clicks["stories__title"]),int(clicks["stories__clicks"])])

        # 数据分组
        group_list = [{"name":ranks_list[i][0],"id":ranks_list[i][0],"data":ranks_list[i:i + 6]} for i in range(0, len(ranks_list), 6)]
        # "name": i[0], "id": i[0],
        for i in group_list:
            for j in i["data"]:
                j.pop(0)

        # group_list = json.dumps(egroup_list)
        users_list = list(
            all_value.values("detail__address").annotate(counts=Count("detail__address")).order_by("-counts"))


        #过虑
        lists = []
        for i in users_list:
            if i["detail__address"]:
                i["detail__address"] = i["detail__address"].split("省")[-1].split("市")[0]
                lists.append(i)

        for i in lists:
            i["counts"] = round(int(i["counts"]) * random.uniform(8, 10), 2)
        users_list = sorted(lists, key=lambda x: x["counts"], reverse=True)

        return render(request, 'admin/index/admin_index.html', locals())


#小说分类管理界面
class Stories_TagsView(PermissionRequiredMixin,View):
    """
    """
    #权限校验
    permission_required = ('stories.add_tag', 'stories.view_tag')
    raise_exception = True

    #没有权限进入界面显示错误
    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(Stories_TagsView, self).handle_no_permission()

    def get(self, request):
        tags = Tag.objects.values('id', 'name').annotate(num_news=Count('stories')). \
            filter(is_delete=False).order_by('-num_news', 'update_time')
        # print(tags)
        return render(request, 'admin/stories/stories_tags.html', locals())


    #增加小说分类
    def post(self, request):
        # 获取数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        tag_name = dict_data.get('name')  # dict_data['name']也可以

        #对数据校验并操作数据库
        if tag_name and tag_name.strip():
            tag_tuple = Tag.objects.get_or_create(name=tag_name)
            tag_instance, tag_created_bolean = tag_tuple
            new_tag_dict = {
                "id": tag_instance.id,
                "name": tag_instance.name
            }
            return to_json_data(errmsg="标签创建成功", data=new_tag_dict) if tag_created_bolean else \
                to_json_data(errno=Code.DATAEXIST, errmsg="标签名已存在")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="标签名为空")


    #删除小说
    def delete(self, request, tag_id):
        tag = Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            # 真删
            # tag.delete()
            tag.is_delete = True
            tag.save(update_fields=['is_delete'])
            return to_json_data(errmsg="标签删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要删除的标签不存在")


    #更新小说分类名字
    def put(self, request, tag_id):
        #获取数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        tag_name = dict_data.get('name')
        tag = Tag.objects.only('id').filter(id=tag_id).first()

        #判断是否存在分类
        if tag:
            #对类名进行操作
            if tag_name and tag_name.strip():
                if not Tag.objects.only('id').filter(name=tag_name).exists():
                    tag.name = tag_name
                    tag.save(update_fields=['name'])
                    return to_json_data(errmsg="标签更新成功")
                else:
                    return to_json_data(errno=Code.DATAEXIST, errmsg="标签名已存在")
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg="标签名为空")

        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要更新的标签不存在")


#公告管理界面
class AnnouncementView(PermissionRequiredMixin,View):
    #后天管理人员的权限校验
    permission_required = ('stories.add_announcement', 'stories.view_announcement')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(AnnouncementView, self).handle_no_permission()

    #进入公告管理界面
    def get(self, request):
        announcment = list(
            Announcement.objects.defer('is_delete', 'update_time').filter(is_delete=False).order_by('priority',
                                                                                        '-update_time'))
        #对公告数据进行格式化
        announcment_list = []
        for announcment_detail in announcment:
            announcment_list.append({
                'id': announcment_detail.id,
                'content': announcment_detail.content,
                'create_time': announcment_detail.create_time.strftime('%Y-%m-%d'),
                'priority': announcment_detail.priority,
                'get_priority_display': announcment_detail.get_priority_display()
            })

        return render(request, 'admin/stories/announcement .html', locals())

    #更新公告信息
    def put(self, request, announcement_id):
        #从前端获取数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        try:
            #操作数据库
            dict_data = json.loads(json_data.decode('utf8'))
            contents = dict_data.get('content')
            update_content = Announcement.objects.filter(pk=announcement_id).first()
            update_content.content = contents
            update_content.create_time = datetime.now()
            update_content.save(update_fields=["content", "create_time"])

            return to_json_data(errmsg="修改成功！")

        except Exception as e:
            logger.info("公告修改失败：\n{}".format(e))
            return to_json_data(errmsg="修改失败")

    #


# 图片上传至FastDFS服务器功能实现
class StoryUploadImage(View):


    def post(self, request):
        image_file = request.FILES.get('image_file')  # 2018.png

        if not image_file:
            logger.info('获取图片失败')
            return to_json_data(errno=Code.NODATA, errmsg='获取图片失败')
        if image_file.content_type not in ('image/jpeg', 'image/png', 'image/jpg','image/gif'):
            return to_json_data(errno=Code.DATAERR, errmsg='不能上传非图片文件')

        try:
            image_ext_name = image_file.name.split('.')[-1]  # image_file.split('.')[-1]
        except Exception as e:
            logger.info('图片后缀名异常：{}'.format(e))
            image_ext_name = 'jpg'
        try:
            upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.error('图片上传异常{}'.format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg='图片上传异常')
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('图片上传到fdfs失败')
                return to_json_data(errno=Code.UNKOWNERR, errmsg='图片上传失败')
            else:
                image_name = upload_res.get('Remote file_id')
                image_url = settings.FASTDFS_SERVER_DOMAIN + image_name
                return to_json_data(data={'image_url': image_url}, errmsg='图片上传成功')


#将图片保存到七牛云
class UploadToken(View):
    """
    """

    def get(self, request):
        access_key = qiniu_secret_info.QI_NIU_ACCESS_KEY
        secret_key = qiniu_secret_info.QI_NIU_SECRET_KEY
        bucket_name = qiniu_secret_info.QI_NIU_BUCKET_NAME
        # 构建鉴权对象
        q = qiniu.Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)

        return JsonResponse({"uptoken": token})


#轮播图界面
class BannerView(PermissionRequiredMixin,View):
    #权限的校验
    permission_required = ('stories.add_banner', 'stories.view_banner')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(BannerView, self).handle_no_permission()

    #进入小说轮播图界面
    def get(self, request):
        banners = Banner.objects.only("id", "image_url", "priority").filter(is_delete=False).order_by("priority",
                                                                                                      "update_time")
        priority_dict = OrderedDict(Banner.PRI_CHOICES)

        return render(request, 'admin/stories/banner.html', locals())


#编辑轮播图
class BannerEditView(PermissionRequiredMixin,View):
    #权限校验
    permission_required = ('stories.add_banner', 'stories.view_banner')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(BannerEditView, self).handle_no_permission()


    #删除轮播图
    def delete(self, request, banner_id):
        banner = Banner.objects.only('id').filter(id=banner_id).first()
        if banner:
            banner.is_delete = True
            banner.save(update_fields=['is_delete'])
            return to_json_data(errmsg='轮播图删除成功！')
        else:
            return to_json_data(errno=Code.NODATA, errmsg='轮播图不存在')

    #更新轮播图
    def put(self, request, banner_id):
        banner = Banner.objects.only('id').filter(id=banner_id).first()
        if not banner:
            return to_json_data(errno=Code.PARAMERR,
                                errmsg='The rotation chart that needs to be updated does not exist')
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))

        #判断轮播图的优先级是否正确
        try:
            priority = int(dict_data['priority'])
            priority_list = [i for i, _ in Banner.PRI_CHOICES]
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级设置错误')
        except Exception as e:
            logger.info('轮播图优先级异常\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级设置错误')

        #获取轮播图片
        image_url = dict_data['image_url']
        if not image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg='图片为空')
        if banner.image_url == priority and banner.image_url == image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级未更改')


        #操作数据库
        banner.priority = priority
        banner.image_url = image_url
        banner.save(update_fields=['priority', 'image_url'])
        return to_json_data(errmsg='轮播图更新成功')


#增加轮播图界面
class BannerAddView(PermissionRequiredMixin,View):
    #权限进行校验
    permission_required = ('stories.add_banner', 'stories.view_banner')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(BannerAddView, self).handle_no_permission()

    #进入增加轮播图界面
    def get(self, request):
        tags = Tag.objects.values('id', 'name').annotate(num_stories=Count('stories')). \
            filter(is_delete=False).order_by('-num_stories', 'update_time')
        # 优先级列表
        # priority_list = {K: v for k, v in models.Banner.PRI_CHOICES}
        priority_dict = OrderedDict(Banner.PRI_CHOICES)

        return render(request, 'admin/stories/banner_add.html', locals())

    # 增加轮播图
    def post(self, request):
        #获取请求体数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        try:
            stories_id = int(dict_data.get('stories_id'))
        except Exception as e:
            logger.info('前端传过来的文章id参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        if not Stories.objects.filter(id=stories_id).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg='文章不存在')

        #对优先级进行判断
        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in Banner.PRI_CHOICES]
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')
        except Exception as e:
            logger.info('轮播图优先级异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')

        # 获取轮播图url
        image_url = dict_data.get('image_url')
        if not image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图url为空')

        # 创建轮播图
        banners_tuple = Banner.objects.get_or_create(stories_id=stories_id)
        banner, is_created = banners_tuple

        banner.priority = priority
        banner.image_url = image_url
        banner.save(update_fields=['priority', 'image_url'])
        return to_json_data(errmsg="轮播图创建成功")


# 小说管理界面
class StoryManageView(PermissionRequiredMixin,View):
    """
    # """
    #权限进行贾瑶瑶
    permission_required = ('stories.add_stories', 'stories.view_stories')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(StoryManageView, self).handle_no_permission()

    #进入小说管理界面
    def get(self, request):
        """
        获取文章列表信息
        """
        tags = Tag.objects.only('id', 'name').filter(is_delete=False)
        stories = Stories.objects.only('id', 'title', 'clicks', 'author__username', 'tag__name', 'update_time'). \
            select_related('author', 'tag').filter(is_delete=False)

        # 通过时间进行过滤
        try:
            start_time = request.GET.get('start_time', '')
            start_time = datetime.strptime(start_time, '%Y/%m/%d') if start_time else ''

            end_time = request.GET.get('end_time', '')
            end_time = datetime.strptime(end_time, '%Y/%m/%d') if end_time else ''
        except Exception as e:
            logger.info("用户输入的时间有误：\n{}".format(e))
            start_time = end_time = ''

        #对时间进行判断
        if start_time and not end_time:
            stories = stories.filter(update_time__gte=start_time)  # 大于等于

        if end_time and not start_time:
            stories = stories.filter(update_time__lte=end_time)  # 小于等于

        if start_time and end_time:
            stories = stories.filter(update_time__range=(start_time, end_time))

        # 通过title进行过滤
        title = request.GET.get('title', '')  # get html中name为title的value值
        if title:
            stories = stories.filter(title__icontains=title)
            # 'contains': 'LIKE BINARY %s',
            # 'icontains': 'LIKE %s',
            # 其中的BINARY是
            # 精确大小写
            # 而’icontains’中的’i’表示忽略大小写

        # 通过作者名进行过滤
        author_name = request.GET.get('author_name', '')
        if author_name:
            stories = stories.filter(author__username__icontains=author_name)

        # 通过标签id进行过滤
        try:
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.info("标签错误：\n{}".format(e))
            tag_id = 0
        stories = stories.filter(is_delete=False, tag_id=tag_id) or stories.filter(is_delete=False)

        # 获取第几页内容
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.info("当前页数错误：\n{}".format(e))
            page = 1
        paginator = Paginator(stories, constants.PER_PAGE_STORIES_COUNT)  # 分页对象
        try:
            stories_info = paginator.page(page)  # 第几页数据
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logging.info("用户访问的页数大于总页数。")
            stories_info = paginator.page(paginator.num_pages)  # 最后一页

        paginator_data = paginator_script.get_paginator_data(paginator, stories_info)


        #对数据进行格式化
        start_time = start_time.strftime('%Y/%m/%d') if start_time else ''
        end_time = end_time.strftime('%Y/%m/%d') if end_time else ''
        context = {
            'stories_info': stories_info,
            'tags': tags,
            'paginator': paginator,
            'start_time': start_time,
            "end_time": end_time,
            "title": title,
            "author_name": author_name,
            "tag_id": tag_id,
            "other_param": urlencode({
                "start_time": start_time,
                "end_time": end_time,
                "title": title,
                "author_name": author_name,
                "tag_id": tag_id,
            })
        }
        context.update(paginator_data)

        return render(request, 'admin/stories/stories_manage.html', context=context)

    def delete(self, request, stories_id):
        if not request.user.is_superuser:
            return to_json_data(errno=Code.ROLEERR, errmsg='权限不够,不能删除')
        stories = Stories.objects.only('id').filter(id=stories_id).first()
        if stories:
            stories.is_delete = True
            stories.save(update_fields=['is_delete'])
            return to_json_data(errmsg='文章删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要删除的文章不存在')

    def put(self, request, stories_id):
        stories = Stories.objects.only('id').filter(id=stories_id).first()
        if not stories:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的文章不存在')

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        form = forms.StoriesPubForm(data=dict_data)
        if form.is_valid():
            stories.title = form.cleaned_data.get('title')
            stories.digest = form.cleaned_data.get('digest')
            stories.image_url = form.cleaned_data.get('image_url')
            stories.tag = form.cleaned_data.get('tag')
            stories.save()
            return to_json_data(errmsg='文章更新成功')
        else:
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


#后台人员进入小说编辑界面
class StoryPublishView(PermissionRequiredMixin,View):
    #权限校验
    permission_required = ('stories.add_stories', 'stories.view_stories')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(StoryPublishView, self).handle_no_permission()


    def get(self, request):

        tags = Tag.objects.only('id', 'name').filter(is_delete=False)

        return render(request, 'admin/stories/stories_publish.html', locals())

    #新增小说
    def post(self, request):
        """
        新增小说
        """
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.StoriesPubForm(data=dict_data)
        if form.is_valid():
            stories_instance = form.save(commit=False)
            stories_instance.author_id = request.user.id
            # news_instance.author_id = 1     # for test
            stories_instance.save()
            return to_json_data(errmsg='文章创建成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

    #小说更新
    def put(self, request, stories_id):
        stories = Stories.objects.only('id').filter(id=stories_id).first()
        if not stories:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的小说不存在')

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        form = forms.StoriesPubForm(data=dict_data)
        if form.is_valid():
            stories.title = form.cleaned_data.get('title')
            stories.digest = form.cleaned_data.get('digest')
            stories.image_url = form.cleaned_data.get('image_url')
            stories.tag = form.cleaned_data.get('tag')
            stories.price = form.cleaned_data.get('price')
            stories.save()
            return to_json_data(errmsg='文章更新成功')
        else:
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

#后台人员章节编辑
class StoryEditView(PermissionRequiredMixin,View):
    permission_required = ('stories.add_stories', 'stories.view_stories')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(StoryEditView, self).handle_no_permission()

    def get(self, request, stories_id):
        stories = Stories.objects.filter(is_delete=False, id=stories_id).first()
        if stories:
            tags = Tag.objects.only('id', 'name').filter(is_delete=False)
            context = {
                "stories": stories,
                "tags": tags
            }
            return render(request, 'admin/stories/stories_publish.html', context=context)
        else:
            raise Http404('需要更新的文章不存在')

#所有用户管理界面
class NormalView(PermissionRequiredMixin,View):
    #权限校验
    permission_required = ('users.add_users', 'users.view_users')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(NormalView, self).handle_no_permission()

    def get(self,request):

        users_info = models.Users.objects.only('mobile','username','vip','remark','id')

        author_name = request.GET.get('author_name', '')
        if author_name:
            users_info = users_info.filter(username__icontains=author_name)

        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.info("当前页数错误：\n{}".format(e))
            page = 1
        paginator = Paginator(users_info, constants.PER_PAGE_STORIES_COUNT)  # 分页对象
        try:
            users_info = paginator.page(page)  # 第几页数据
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logging.info("用户访问的页数大于总页数。")
            users_info = paginator.page(paginator.num_pages)  # 最后一页

        paginator_data = paginator_script.get_paginator_data(paginator, users_info)

        #数据格式化
        context = {
            'users_info': users_info,
            'paginator': paginator,
            'author_name': author_name,
        }
        context.update(paginator_data)

        return render(request,'admin/user_manage/normal_user.html',context=context)

    def post(self, request, user_id):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        user_remark = dict_data.get('remark')
        user = models.Users.objects.only('id').filter(id=user_id).first()
        if user:
            user.remark = user_remark
            user.save(update_fields=['remark'])
            return to_json_data(errmsg="备注更新成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要更新的备注不存在")


    def put(self,request,user_id):

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        type_vip = dict_data.get('type_vip')

        user = models.Users.objects.only('id').filter(id=user_id).first()
        if user:
            if type_vip == 'normal':
                user.vip = False
                user.save(update_fields=['vip'])
                return to_json_data(errmsg="更新成功")
            else:
                user.vip = True
                user.save(update_fields=['vip'])
                return to_json_data(errmsg="更新成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要更新的备注不存在")

#vip用户管理界面
class VIPView(PermissionRequiredMixin,View):
    #权限管理界面
    permission_required = ('users.add_users', 'users.view_users')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(VIPView, self).handle_no_permission()

    def get(self,request):
        users_info = models.Users.objects.only('mobile', 'username', 'vip', 'remark', 'id').filter(vip=True)

        author_name = request.GET.get('author_name', '')
        if author_name:
            users_info = users_info.filter(username__icontains=author_name)

        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.info("当前页数错误：\n{}".format(e))
            page = 1
        paginator = Paginator(users_info, constants.PER_PAGE_STORIES_COUNT)  # 分页对象
        try:
            users_info = paginator.page(page)  # 第几页数据
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logging.info("用户访问的页数大于总页数。")
            users_info = paginator.page(paginator.num_pages)  # 最后一页

        paginator_data = paginator_script.get_paginator_data(paginator, users_info)

        context = {
            'users_info': users_info,
            'paginator': paginator,
            'author_name': author_name,
        }
        context.update(paginator_data)

        return render(request,'admin/user_manage/vip_user.html',context=context)

    def post(self, request, user_id):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        user_remark = dict_data.get('remark')
        user = models.Users.objects.only('id').filter(id=user_id).first()
        if user:
            user.remark = user_remark
            user.save(update_fields=['remark'])
            return to_json_data(errmsg="备注更新成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要更新的备注不存在")
    
    
    def put(self,request,user_id):

        user = models.Users.objects.only('id').filter(id=user_id).first()
        if user:        
            user.vip = False
            user.save(update_fields=['vip'])
            return to_json_data(errmsg="更新成功")
          
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要更新的备注不存在")

#违规用户管理
class IllegalView(PermissionRequiredMixin,View):
    #权限管理界面
    permission_required = ('users.add_users', 'users.view_users')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(IllegalView, self).handle_no_permission()


    def get(self,request):
        users_info = models.Users.objects.only('mobile', 'username', 'vip', 'remark', 'id')

        author_name = request.GET.get('author_name', '')
        if author_name:
            users_info = users_info.filter(username__icontains=author_name)
            #如果用户有备注则取出备注内容
            users_info = [i for i in users_info if i.remark]

        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.info("当前页数错误：\n{}".format(e))
            page = 1
        paginator = Paginator([i for i in users_info if i.remark ], constants.PER_PAGE_STORIES_COUNT)  # 分页对象
        try:
            users_info = paginator.page(page)  # 第几页数据
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logging.info("用户访问的页数大于总页数。")
            users_info = paginator.page(paginator.num_pages)  # 最后一页

        paginator_data = paginator_script.get_paginator_data(paginator, users_info)

        context = {
            'users_info': users_info,
            'paginator': paginator,
            'author_name': author_name,
        }
        #将字典数据组合
        context.update(paginator_data)


        return render(request,'admin/user_manage/illegal_user.html',context=context)


    #给用户增删备注
    def put(self, request, user_id):

        user = models.Users.objects.only('id').filter(id=user_id).first()
        if user:
            user.remark =""
            user.save(update_fields=['remark'])
            return to_json_data(errmsg="解除成功")

        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要更新的备注不存在")


#下载内容管理
class DownloadView(PermissionRequiredMixin,View):
    permission_required = ('doc.add_doc', 'doc.view_doc')
    raise_exception = True


    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(DownloadView, self).handle_no_permission()

    def get(self,request):
        docs = Doc.objects.select_related("story").only('story__title','create_time').filter(is_delete=False)

        return  render(request,'admin/docdownl/download_manage.html',locals())

    #删除可下载小说
    def delete(self, request, stories_id):
        doc = Doc.objects.filter(is_delete=False, id=stories_id).first()
        if doc:
            doc.is_delete = True
            doc.save(update_fields=['is_delete'])
            return to_json_data(errmsg="小说文件删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要删除的小说不存在")


#小说下载管理页
class DownloadPubView(PermissionRequiredMixin,View):
    #权限校验
    permission_required = ('doc.add_doc', 'doc.view_doc')
    raise_exception = True


    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(DownloadPubView, self).handle_no_permission()
    #进入编辑下载小说页面
    def get(self, request):
        tags = Tag.objects.values('id', 'name').annotate(stories_news=Count('stories')). \
            filter(is_delete=False).order_by('-stories_news', 'update_time')

        return  render(request,'admin/docdownl/download_pub.html',locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        story_id = int(dict_data.get('story_id'))
        file_url = dict_data.get('file_url')
        if not story_id :
            return to_json_data(errno=Code.PARAMERR, errmsg='获取小说失败')

        if not file_url :
            logger.info('从前端获取文件失败')
            return to_json_data(errno=Code.NODATA, errmsg='从前端获取文件失败')

        if re.match(r'^https?:/{2}\w.+$', file_url):

            story_doc = Doc.objects.create(file_url=file_url,story_id=story_id)
            story_doc.save()

        return to_json_data(errmsg='小说下载创建成功')

    #跟新下载小说信息
    def put(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        story_id = int(dict_data.get('story_id'))
        file_url = dict_data.get('file_url')
        doc = Doc.objects.filter(is_delete=False, story_id=story_id).first()
        if not doc:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的文件不存在')

        if not file_url:
            logger.info('从前端获取文件失败')
            return to_json_data(errno=Code.NODATA, errmsg='从前端获取文件失败')

        if re.match(r'^https?:/{2}\w.+$', file_url):
            doc.file_url=file_url
            doc.save(update_fields=['file_url'])

        return to_json_data(errmsg='小说下载更新成功')


#小说下载发布页
class DownloadStoryView(PermissionRequiredMixin,View):
    permission_required = ('doc.add_doc', 'doc.view_doc')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(DownloadStoryView, self).handle_no_permission()

    def get(self,request,story_id):
        story_list = Stories.objects.select_related("tag","doc").values('id', 'title',"tag__name","tag_id","doc__file_url").filter(is_delete=False, id=story_id).first()
        return render(request,'admin/docdownl/download_pub.html',locals())

    def post(self, request, tag_id):
        story = Stories.objects.values('id', 'title').filter(is_delete=False, tag_id=tag_id)
        story_list = [i for i in story]

        return to_json_data(data={
            'story': story_list
        })


#视频管理界面
class VideoManageView(PermissionRequiredMixin,View):
    """
    route: /admin/courses/
    """
    #权限校验
    permission_required = ('storyvideo.add_storyvideo', 'storyvideo.view_storyvideo')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(VideoManageView, self).handle_no_permission()

    #进去小说管理界面
    def get(self, request):
        story_video = Storyvideo.objects.only('title','duration').filter(is_delete=False)
        return render(request, 'admin/storyvideo/video_manage.html', locals())


#编辑视频界面
class VideoEditView(PermissionRequiredMixin,View):
    """
    route: /admin/courses/<int:course_id>/
    """
    permission_required = ('storyvideo.add_storyvideo', 'storyvideo.view_storyvideo')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(VideoEditView, self).handle_no_permission()

    def get(self, request, video_id):
        """
        """
        story_video = Storyvideo.objects.filter(is_delete=False, id=video_id).first()
        if story_video:
            # teachers = Teacher.objects.only('name').filter(is_delete=False)
            # categories = CourseCategory.objects.only('name').filter(is_delete=False)
            return render(request, 'admin/storyvideo/vedio_pub.html', locals())
        else:
            raise Http404('需要更新的课程不存在！')

    #删除视频
    def delete(self, request, video_id):
        story = Storyvideo.objects.filter(is_delete=False, id=video_id).first()
        if story:
            story.is_delete = True
            story.save(update_fields=['is_delete'])
            return to_json_data(errmsg="课程删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要删除的课程不存在")

    #跟新视频
    def put(self, request, video_id):
        story = Storyvideo.objects.filter(is_delete=False, id=video_id).first()
        if not story:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的课程不存在')

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.VideoPubForm(data=dict_data)
        if form.is_valid():
            for attr, value in form.cleaned_data.items():
                setattr(story, attr, value)

            story.save()
            return to_json_data(errno=Code.OK,errmsg='课程更新成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


#新的视频发布界面
class VideoPubView(PermissionRequiredMixin,View):
    """
    route: /admin/courses/pub/
    # """
    # permission_required = ('course.add_course', 'course.view_course')
    # raise_exception = True
    #
    # def handle_no_permission(self):
    #     if self.request.method.lower() != 'get':
    #         return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
    #     else:
    #         return super(CoursesPubView, self).handle_no_permission()
    permission_required = ('storyvideo.add_storyvideo', 'storyvideo.view_storyvideo')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(VideoPubView, self).handle_no_permission()

    def get(self, request):

        return render(request, 'admin/storyvideo/vedio_pub.html', locals())

    #提交视频发布
    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.VideoPubForm(data=dict_data)
        if form.is_valid():
            form.save()
            return to_json_data(errmsg='视频发布成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


#上传文件到fast_dfs
class DocsUploadFile(View):
    """route: /admin/docs/files/
    """
    # permission_required = ('doc.add_doc', )

    # def handle_no_permission(self):
    #     return to_json_data(errno=Code.ROLEERR, errmsg='没有上传文件的权限')

    def post(self, request):
        text_file = request.FILES.get('text_file')

        if not text_file:
            logger.info('从前端获取文件失败')
            return to_json_data(errno=Code.NODATA, errmsg='从前端获取文件失败')

        if text_file.content_type not in ('application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/msword', 'application/octet-stream', 'application/pdf',
                                          'application/zip', 'text/plain', 'application/x-rar'):
            return to_json_data(errno=Code.DATAERR, errmsg='不能上传非文本文件')

        try:
            text_ext_name = text_file.name.split('.')[-1]
        except Exception as e:
            logger.info('文件拓展名异常：{}'.format(e))
            text_ext_name = 'pdf'

        try:
            upload_res = FDFS_Client.upload_by_buffer(text_file.read(), file_ext_name=text_ext_name)
        except Exception as e:
            logger.error('文件上传出现异常：{}'.format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg='文件上传异常')
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('文件上传到FastDFS服务器失败')
                return to_json_data(Code.UNKOWNERR, errmsg='文件上传到服务器失败')
            else:

                text_name = upload_res.get('Remote file_id')
                text_url = settings.FASTDFS_SERVER_DOMAIN + text_name
                return to_json_data(data={'text_file': text_url}, errmsg='文件上传成功')


#订单管理（是否发货）
class OrderFormView(PermissionRequiredMixin,View):
    #权限管理
    permission_required = ('admin.add_orderform', 'admin.view_orderform')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(OrderFormView, self).handle_no_permission()

    #订单发货管理
    def post(self,request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.OrderForm(data=dict_data)
        if form.is_valid():
            form.save()
            return to_json_data(errmsg='购买成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


#订单管理界面
class OrederListView(PermissionRequiredMixin,View):
    """
    # """

    permission_required = ('admin.add_orderform', 'admin.view_orderform')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(OrederListView, self).handle_no_permission()

    #进入订单界面
    def get(self, request):
        """
        获取文章列表信息
        """
        order_information = OrderForm.objects.defer("update_time").filter(is_delete=False).all()

        # 获取第几页内容
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.info("当前页数错误：\n{}".format(e))
            page = 1
        #每页展示多少条订单
        paginator = Paginator(order_information, constants.PER_PAGE_STORIES_COUNT)  # 分页对象
        try:
            order_info = paginator.page(page)  # 第几页数据
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logging.info("用户访问的页数大于总页数。")
            order_info = paginator.page(paginator.num_pages)  # 最后一页

        paginator_data = paginator_script.get_paginator_data(paginator, order_info)


        context = {
            'order_info': order_info,
            'paginator': paginator,

        }
        context.update(paginator_data)

        return render(request, 'admin/stories/buy_information.html', context=context)

    #删除订单
    def delete(self, request, goods_id):
        order_goods = OrderForm.objects.only('id').filter(id=goods_id).first()
        if order_goods:
            order_goods.is_delete = True

            order_goods.save(update_fields=['is_delete'])
            return to_json_data(errmsg='订单删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要删除的订单不存在')


    def put(self, request, goods_id):
        order_goods = OrderForm.objects.only('id').filter(id=goods_id).first()
        if not order_goods:
            return to_json_data(errno=Code.NODATA, errmsg='需要发货的订单不存在不存在')

        if order_goods:
            order_goods.status = True
            order_goods.place = "快递等待揽收"
            order_goods.save(update_fields=['status','place'])
            return to_json_data(errmsg='订单发货成功')

        else:

             return to_json_data(errno=Code.PARAMERR, errmsg='需要删除的订单不存在')







#后台人员权限管理组
class GroupsManageView(PermissionRequiredMixin, View):
    """
    route: /admin/groups/
    """
    permission_required = ('auth.add_group', 'auth.view_group')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(GroupsManageView, self).handle_no_permission()

    def get(self, request):

        groups = Group.objects.values('id', 'name').annotate(num_users=Count('user')). \
            order_by('-num_users', 'id')
        return render(request, 'admin/user_permission/groups_manage.html', locals())



#权限管理组编辑
class GroupsEditView(PermissionRequiredMixin, View):
    """
    route: /admin/groups/<int:group_id>/
    """
    permission_required = ('auth.change_group', 'auth.delete_group')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(GroupsEditView, self).handle_no_permission()

    def get(self, request, group_id):
        """
        """
        group = Group.objects.prefetch_related('permissions','permissions__content_type').filter(id=group_id).first()
        if group:
            permissions = Permission.objects.prefetch_related('content_type').only('id','name','content_type_id').all()
            return render(request, 'admin/user_permission/groups_add.html', locals())
        else:
            raise Http404('需要更新的组不存在！')

    def delete(self, request, group_id):
        group = Group.objects.filter(id=group_id).first()
        if group:
            group.permissions.clear()  # 清空权限
            group.delete()
            return to_json_data(errmsg="用户组删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要删除的用户组不存在")

    def put(self, request, group_id):
        group = Group.objects.prefetch_related('permissions').filter(id=group_id).first()
        if not group:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的用户组不存在')

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        # 取出组名，进行判断
        group_name = dict_data.get('name', '').strip()
        if not group_name:
            return to_json_data(errno=Code.PARAMERR, errmsg='组名为空')

        if group_name != group.name and Group.objects.filter(name=group_name).exists():
            return to_json_data(errno=Code.DATAEXIST, errmsg='组名已存在')

        # 取出权限
        group_permissions = dict_data.get('group_permissions')
        if not group_permissions:
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数为空')

        try:
            permissions_set = set(int(i) for i in group_permissions)
        except Exception as e:
            logger.info('传的权限参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数异常')

        all_permissions_set = set(i.id for i in Permission.objects.only('id'))
        if not permissions_set.issubset(all_permissions_set):
            return to_json_data(errno=Code.PARAMERR, errmsg='有不存在的权限参数')

        existed_permissions_set = set(i.id for i in group.permissions.all())
        if group_name == group.name and permissions_set == existed_permissions_set:
            return to_json_data(errno=Code.DATAEXIST, errmsg='用户组信息未修改')
        # 设置权限
        group.permissions.clear()
        group.save()
        for perm_id in permissions_set:
            p = Permission.objects.get(id=perm_id)
            group.permissions.add(p)
        group.name = group_name
        group.save()
        return to_json_data(errmsg='组更新成功！')

#权限管理组的创建
class GroupsAddView(PermissionRequiredMixin, View):
    """
    route: /admin/groups/add/
    """
    permission_required = ('auth.add_group', 'auth.view_group')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(GroupsAddView, self).handle_no_permission()


    def get(self, request):
        permissions = Permission.objects.prefetch_related('content_type').only('id', 'name', 'content_type_id').all()

        return render(request, 'admin/user_permission/groups_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))

        # 取出组名，进行判断
        group_name = dict_data.get('name', '').strip()
        if not group_name:
            return to_json_data(errno=Code.PARAMERR, errmsg='组名为空')

        one_group, is_created = Group.objects.get_or_create(name=group_name)
        if not is_created:
            return to_json_data(errno=Code.DATAEXIST, errmsg='组名已存在')

        # 取出权限
        group_permissions = dict_data.get('group_permissions')
        if not group_permissions:
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数为空')

        try:
            permissions_set = set(int(i) for i in group_permissions)
        except Exception as e:
            logger.info('传的权限参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数异常')

        all_permissions_set = set(i.id for i in Permission.objects.only('id'))
        if not permissions_set.issubset(all_permissions_set):
            return to_json_data(errno=Code.PARAMERR, errmsg='有不存在的权限参数')

        # 设置权限
        for perm_id in permissions_set:
            p = Permission.objects.get(id=perm_id)
            one_group.permissions.add(p)

        one_group.save()
        return to_json_data(errmsg='组创建成功！')

#后台人员权限管理
class UsersManageView(PermissionRequiredMixin, View):
    """
    route: /admin/users/
    """
    permission_required = ('users.add_users', 'users.view_users')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(UsersManageView, self).handle_no_permission()

    def get(self, request):
        users = models.Users.objects.prefetch_related('groups').only('username', 'is_staff', 'is_superuser','groups__name').filter(is_staff=True)
        return render(request, 'admin/user_permission/users_manage.html', locals())

#后台人员的权限编辑
class UsersEditView(PermissionRequiredMixin, View):
    """
    route: /admin/users/<int:user_id>/
    """
    permission_required = ('users.change_users', 'users.delete_users')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super(UsersEditView, self).handle_no_permission()

    def get(self, request, user_id):
        user_instance = models.Users.objects.filter(id=user_id).first()
        if user_instance:
            groups = Group.objects.only('name').all()
            return render(request, 'admin/user_permission/users_edit.html', locals())
        else:
            raise Http404('需要更新的用户不存在！')

    def delete(self, request, user_id):
        user_instance = models.Users.objects.filter(id=user_id).first()
        if user_instance:
            user_instance.groups.clear()  # 清除用户组
            user_instance.user_permissions.clear()  # 清除用户权限
            user_instance.is_active = False  # 设置为不激活状态
            user_instance.save()
            return to_json_data(errmsg="用户删除成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要删除的用户不存在")

    def put(self, request, user_id):
        user_instance = models.Users.objects.filter(id=user_id).first()
        if not user_instance:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的用户不存在')

        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        # 取出参数，进行判断
        try:
            groups = dict_data.get('groups')  # 取出用户组列表

            is_staff = int(dict_data.get('is_staff'))
            is_superuser = int(dict_data.get('is_superuser'))
            is_active = int(dict_data.get('is_active'))
            params = (is_staff, is_superuser, is_active)
            if not all([p in (0, 1) for p in params]):
                return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        except Exception as e:
            logger.info('从前端获取参数出现异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        try:
            groups_set = set(int(i) for i in groups) if groups else set()
            print(groups_set)
        except Exception as e:
            logger.info('传的用户组参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='用户组参数异常')

        all_groups_set = set(i.id for i in Group.objects.only('id'))
        if groups_set == {0}:
            user_instance.groups.clear()
            user_instance.save()
            return to_json_data(errmsg='用户信息更新成功！')

        if not groups_set.issubset(all_groups_set):
            return to_json_data(errno=Code.PARAMERR, errmsg='有不存在的用户组参数')

        gs = Group.objects.filter(id__in=groups_set)
        # 先清除组
        user_instance.groups.clear()
        user_instance.groups.set(gs)

        user_instance.is_staff = bool(is_staff)
        user_instance.is_superuser = bool(is_superuser)
        user_instance.is_active = bool(is_active)
        user_instance.save()
        return to_json_data(errmsg='用户信息更新成功！')


