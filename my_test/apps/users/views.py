import json
import logging
import string
import qiniu
import random
import re
import datetime
from django.db.models import Count

from django.http import JsonResponse, Http404
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.hashers import make_password
from utils.secrets import qiniu_secret_info
from stories.models import Stories, Chapter, Tag

# Create your views here.

# 开始选择页面
from django_redis import get_redis_connection

from admin.models import OrderForm
from users import constants, forms
from users.models import Users, Detail
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from .forms import RegisterForm, LoginFrom, DetailForm, ChapterAddForm

logger = logging.getLogger('django')


# 最初开始页面(非首页
class StartView(View):

    def get(self, request):
        return render(request, 'users/start.html')


# 登录页面
class LoginView(View):

    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        # 从前端获取到的请求体数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # 将json数据转化为python数据
        json_data = json.loads(json_data.decode('utf8'))

        # from表单对数据进行校验
        form = LoginFrom(data=json_data, request=request)

        # 校验成功
        if form.is_valid():
            return to_json_data(errmsg="恭喜你登录成功")

        else:
            # 定义一个错误信息列表，校验数据错误信息
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 注册界面
class RegisterView(View):

    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        """
        """
        # 从前端获取数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # 将json数据转化为python数据
        dict_data = json.loads(json_data.decode('utf8'))

        #注册数据校验
        form = RegisterForm(data=dict_data)
        if form.is_valid():
            # 校验成功后
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')

            #创建新用户
            user = Users.objects.create_user(username=username, password=password, mobile=mobile)

            #创建一个新用户的个人信息
            Detail.objects.create(user_id=user.id, image_url="/media/head/default.jpg")
            login(request, user)
            return to_json_data(errmsg="恭喜您，注册成功！")

        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


#忘记密码逻辑
class Forget_Login_View(View):
    def get(self, request):
        return render(request, 'users/forget_remember.html')

    def post(self, request):
        """
        """
        #从前端获取到参数
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        #获取电话号码
        mobile = dict_data.get('mobile')

        #获取图片验证码
        sms_code = dict_data.get('sms_code')

        if mobile and sms_code:
            if not re.match(r"^1[3-9]\d{9}$", mobile):
                return to_json_data(errmsg="手机号码格式不正确")

            #连接redis数据库
            redis_conn = get_redis_connection(alias='verify_codes')

            sms_fmt = "sms_{}".format(mobile).encode('utf-8')
            real_sms = redis_conn.get(sms_fmt)

            #判断电话
            if (not real_sms) or (sms_code != real_sms.decode('utf-8')):
                return to_json_data(errmsg="短信验证码错误")

            user = Users.objects.filter(mobile=mobile).first()
            if not user:
                to_json_data(errmsg="此电话号码没有注册！")
            else:
                login(request, user)
                return to_json_data(errmsg="登录成功！")

        else:
            # 定义一个错误信息列表

            return to_json_data(errno=Code.PARAMERR, errmsg="登录失败")

#登出
class LoginoutView(View):

    def get(self, request):
        logout(request)

        return redirect(reverse("users:login"))


#个人信息查看界面
class DetailView(View):

    def get(self, request):
        return render(request, 'users/detail.html')

#修改个人信息是短信验证
class DetailPhoneView(View):
    def post(self, request):

        #获取取请求体数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        mobile = dict_data.get('mobile') if dict_data.get('mobile') else None

        if mobile and re.match(r"^1[3-9]\d{9}$", mobile):

            sms_num = ''.join([random.choice(string.digits) for _ in range(constants.SMS_CODE_NUMS)])
            # 4、建立连接
            redic_conn = get_redis_connection(alias='verify_codes')

            # 创建一个在60秒以内是否有发送记录的标记
            sms_flag_fmt = "sms_flag_{}".format(mobile)

            # 创建保存短信验证码的标记key
            sms_text_fmt = "sms_{}".format(mobile)

            try:
                #生成指定key保存进redis数据库
                redic_conn.setex(sms_text_fmt.encode('utf-8'), constants.SMS_CODE_REDIS_EXPIRES, sms_num)
                redic_conn.setex(sms_flag_fmt.encode('utf-8'), constants.SEND_SMS_CODE_INTERVAL, 1)

            except Exception as e:
                logging.debug('redis 执行出现异常:{}'.format(e))

                return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])
            logger.info("Sms code: {}".format(sms_num))
            return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
        else:

            return to_json_data(errno=Code.PARAMERR, errmsg="请输入正确的电话号码")


#个人信息更新
class DetailPutView(View):
    def post(self, request):
        #从前端获取到数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))


        mobile = dict_data.get('mobile') if dict_data.get('mobile') else None
        #将性别值进行转换为数字
        sex = int(dict_data.get("sex"))
        introduce = dict_data.get("textareas")
        sms_codes = dict_data.get("sms_code")
        top_imgae = dict_data.get("topimage")

        #对输入的信息值进行校验
        if not (mobile and re.match(r"^1[3-9]\d{9}$", mobile)):
            return to_json_data(errno=Code.PARAMERR, errmsg="请输入正确的电话号码")
        if not (sex == 0 or sex == 1):
            return to_json_data(errno=Code.PARAMERR, errmsg="请输入正确的性别值")
        if len(sms_codes) != 6:
            return to_json_data(errno=Code.PARAMERR, errmsg="请输入正确短信验证码")

        #连接redis数据库对电话号码进行校验
        redis_conn = get_redis_connection(alias='verify_codes')
        #
        sms_fmt = "sms_{}".format(mobile).encode('utf-8')
        real_sms = redis_conn.get(sms_fmt)

        if (not real_sms) or (sms_codes != real_sms.decode('utf-8')):
            return to_json_data(errno=Code.PARAMERR, errmsg="请输入正确短信验证码")
        try:
            #将数据信息存进数据库
            address = dict_data.get("address")
            user = Users.objects.get(username=request.user)
            user.mobile = mobile
            user.save(update_fields=['mobile'])
            detail = Detail.objects.only("user").filter(user__username=request.user).first()
            detail.introduce = introduce
            detail.sex = sex
            detail.address = address
            detail.image_url = top_imgae
            detail.save(update_fields=['sex', 'address', 'introduce', 'image_url'])
            login(request, user)

            return to_json_data(errmsg="修改成功！")
        except Exception as e:
            logger.info('修改用户信息：\n{}'.format(e))

            return render(request, 'users/500.html')

    def put(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict

        dict_data = json.loads(json_data.decode('utf8'))
        again_password = dict_data.get('password_repeat')
        # form = DetailForm(data=dict_data)
        # if password and again_password:
        # if form.is_valid():
        password = dict_data.get('password')
        mobile = dict_data.get('mobile')
        introduce = dict_data.get('textareas')
        sex = int(dict_data.get("sex"))
        topimgae = dict_data.get("topimage")
        print(request.data)

        if sex == 0 or sex == 1:
            try:
                address = dict_data.get("address")
                user = Users.objects.get(username=request.user)
                if password and again_password and password == again_password:
                    user.password = make_password(password)
                user.mobile = mobile
                user.save()
                detail = Detail.objects.filter(user_id=request.user.id).first()
                detail.introduce = introduce
                detail.sex = sex
                detail.address = address
                detail.image_url = topimgae
                detail.save(update_fields=['sex', 'address', 'introduce', 'image_url'])
                login(request, user)
                return to_json_data(errmsg="修改成功！")
            except Exception as e:
                #返回错误错误界面
                logger.info('修改用户信息：\n{}'.format(e))
                return render(request, 'users/500.html')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="请输入正确的性别值")

        # else:
        #     # 定义一个错误信息列表
        #     err_msg_list = []
        #     for item in form.errors.get_json_data().values():
        #         err_msg_list.append(item[0].get('message'))
        #     err_msg_str = '/'.join(err_msg_list)
        #
        #     return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


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


#购物车界面
class ShoppingView(View):

    def get(self, request):
        #判断用户是否登录，没有登录就从定向到登录界面
        if not request.user.is_authenticated:
            return render(request, 'users/login.html')

        #获取订单信息
        order_form = OrderForm.objects.defer("id", 'update_time', 'is_delete').filter(usesr=request.user)
        # print(order_form.place)

        return render(request, 'users/shopping_cart.html', locals())


#作者个人界面
class WriteView(View):
    def get(self, request):
        # 获取作者个人的所有小说
        write_book = Stories.objects.filter(is_delete=False, author_id=request.user.id).only("title", "clicks",
                                                                         'create_time',"price").order_by( '-clicks')

        # 格式化点击量前十的数据，并且用于对数据的可视化
        title_name = [str(i.title) for i in write_book[0:10]]
        cliks = [i.clicks for i in write_book]

        return render(request, 'users/write_view.html', locals())


#作者编辑界面
class WriteEditView(View):

    #进入编辑小说编辑章节界面
    def get(self, request, stories_id):

        #获取小说以及该小说的所有章节
        chapter = Chapter.objects.select_related("story"). \
            only('id', "content", 'chapter_title', 'chapter', 'story__title', 'story__digest',
                 'story__image_url').filter(story_id=stories_id).order_by('id')

        if not chapter:
            #错误则放回500界面
            return render(request, 'users/500.html')

        #获取小说的所有信息比如摘要等
        stories = chapter.first()

        return render(request, 'users/write_view_edit.html', locals())


    #获取某一章节的章节内容
    def post(self, request, chapter_id):

        content = Chapter.objects.only("id", "content").filter(id=chapter_id).first()

        if not content:
            return to_json_data(errno=Code.PARAMERR, errmsg='章节不存在')

        data = {
            "content": content.content,
            'id': content.id,
        }

        return to_json_data(data=data)

    #更新文章章节信息
    def put(self, request, chapter_id):
        #从前端获取到数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        #将json数据转换为python数据
        dict_data = json.loads(json_data.decode('utf8'))

        content = dict_data.get("content")
        #对内容进行检验
        if not content:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        chapter = Chapter.objects.only('id', 'content').filter(id=chapter_id).first()
        if not chapter:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的章节不存在')

        #存进数据库
        chapter.content = content
        chapter.update_time = datetime.datetime.now()
        chapter.save(update_fields=['content', 'update_time'])

        return to_json_data(errmsg='文章更新成功')

    # def delete(self,request,stories_id):
    #     if not request.user.is_superuser:
    #         return to_json_data(errno=Code.ROLEERR, errmsg='权限不够,不能删除')
    #     stories = Stories.objects.only('id').filter(id=stories_id).first()
    #     if stories:
    #         stories.is_delete = True
    #         stories.save(update_fields=['is_delete'])
    #         return to_json_data(errmsg='文章删除成功')
    #     else:
    #         return to_json_data(errno=Code.PARAMERR, errmsg='需要删除的文章不存在')


#增加章节界面
class Chapter_AddView(View):

    #获取章节界面
    def get(self, request, stories_id):
        chapter = Chapter.objects.select_related("story"). \
            only('id', "content", 'chapter_title', 'chapter', 'story__title', 'story__digest',
                 'story__image_url', 'tag_id').filter(story_id=stories_id).order_by('id')
        #对数据进行校验
        if not chapter:
            return render(request, 'users/500.html')

        stories = chapter.first()

        return render(request, 'users/chapter_add.html', locals())

    #增加章节信息
    def post(self, request, stories_id):

        chapter = Chapter.objects.filter(story_id=stories_id)
        #对数据进行校验
        if not chapter:
            return to_json_data(errno=Code.PARAMERR, errmsg='小说不存在')
        #从前端获取数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        #数据类型进行转换，json --->python
        dict_data = json.loads(json_data.decode('utf8'))

        #对章节数据进行分割并且校验
        chapter_number = dict_data.get("chapter").strip()
        if not chapter_number:
            return to_json_data(errno=Code.PARAMERR, errmsg='章节不存在')

        if chapter.filter(chapter=chapter_number):
            return to_json_data(errno=Code.PARAMERR, errmsg='章节已经存在')

        #form表单对章节信息进行校验
        form = forms.ChapterAddForm(data=dict_data)
        if form.is_valid():
            #代表先不要提交到数据库
            chapter_instance = form.save(commit=False)
            chapter_instance.story_id = stories_id
            # news_instance.author_id = 1     # for test
            #提交到数据库
            chapter_instance.save()
            return to_json_data(errmsg='小说文章增加成功')
        else:
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


#小说信息更新界面
class StoryPublishView(View):

    #获取小说的相关信息
    def get(self, request):
        if not request.user.write:
            return render(request, '500.html')

        tag = Tag.objects.only("id", "name").filter(is_delete=False)

        return render(request, 'users/story_publish.html', locals())

    def post(self, request):
        # 小说标题检验
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        title = dict_data.get("story_name").strip()
        if not title:
            return to_json_data(errno=Code.PARAMERR, errmsg='标题不存在')

        data = {
            'title': title,
            'count': Stories.objects.filter(title=title).count()

        }
        return JsonResponse(data=data)

#
class StoryChangeView(View):
    #没有登录就重定向到登录界面
    def get(self, request, story_id):
        if not request.user.write:
            return render(request, 'users/login.html')

        stories = Stories.objects.filter(is_delete=False, id=story_id).first()
        if stories:
            tag = Tag.objects.only('id', 'name').filter(is_delete=False)
            context = {
                "stories": stories,
                "tag": tag,
            }
            return render(request, 'users/story_publish.html', context=context)
        else:
            raise Http404('需要更新的文章不存在')


    def post(self, request):
        """
        新增小说
        """
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        chapter_title = dict_data.get("chapter_title")
        content = dict_data.get("content")
        chapter = dict_data.get("chapter")
        if not chapter_title:
            return to_json_data(errno=Code.PARAMERR, errmsg="章节标题为空！")
        if not content:
            return to_json_data(errno=Code.PARAMERR, errmsg="章节内容为空！")
        if not chapter:
            return to_json_data(errno=Code.PARAMERR, errmsg="章节为空")

        form = forms.StoriesPubForm(data=dict_data)
        if form.is_valid():
            stories_instance = form.save(commit=False)
            stories_instance.author_id = request.user.id
            # news_instance.author_id = 1     # for test
            stories_instance.save()
            story = Stories.objects.only("id").filter(title=dict_data.get("title")).first()
            print(story)
            Chapter.objects.create(chapter=chapter, tag_id=dict_data.get("tag"), content=content, story_id=story.id,
                                   chapter_title=chapter_title)
            return to_json_data(errmsg='小说创建成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

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
            return to_json_data(errmsg='小说更新成功')
        else:
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


