import logging
import json
import random
import string
import re
from django.shortcuts import render

from django.views import View
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse
from django.http import Http404

from . import constants
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from users.models import Users
from . import forms
from utils.yuntongxun.sms import CCP
from utils.captcha.captcha import captcha
from celery_tasks.sms import tasks as sms_tasks

# 导入日志器
logger = logging.getLogger('django')


# 前端使用ajax实现异步请求,获取图片验证码
class ImageCode(View):
    """
    define image verification view
    # /image_codes/<uuid:image_code_id>/
    """

    def get(self, request, image_code_id):

        #从captcha包里面取到图片验证码和图片
        text, image = captcha.generate_captcha()

        # 确保settings.py文件中有配置redis CACHE
        # Redis原生指令参考 http://redisdoc.com/index.html
        # Redis python客户端 方法参考 http://redis-py.readthedocs.io/en/latest/#indices-and-tables


        # 连接redis数据库
        con_redis = get_redis_connection(alias='verify_codes')

        #从前端的js里面获取到的uuid:128c3375-a90f-4c1b-8495-31879d75fadb
        img_key = "img_{}".format(image_code_id).encode('utf-8')

        # 将图片验证码的key和验证码文本保存到redis中，并设置过期时间
        con_redis.setex(img_key, constants.Verify_image, text)
        logger.info("Image code: {}".format(text))

        return HttpResponse(content=image, content_type="images/jpg")

#注册界面的异步检测用户名
class CheckUsernameView(View):

    def get(self, request, username):
        if username:
            if re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', username):
                # if re.search(u'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', username):
                data = {
                    'username': username,
                    'count': Users.objects.filter(username=username).count()
                }
                return JsonResponse(data=data)
            else:
                data = {
                    'errors': "用户名中不能含有非法字符"
                }
                return JsonResponse(data=data)
        else:
            logger.debug("username故障")
            # data = {
            #     'fault': '用户名不可以包含非法字符(!,@,#,$,%...)'
            # }
            #
            return Http404('1')

#注册界面的异步检测电话号码
class CheckMobileView(View):

    def get(self, request, Mobile_phone):
        if Mobile_phone:

            data = {
                'mobile': Mobile_phone,
                'count': Users.objects.filter(mobile=Mobile_phone).count()

            }

            return JsonResponse(data=data)

        else:
            logger.debug("数据库查询mobile_phone故障")

#注册界面的异步生成验证码
class SmsCodesView(View):
    """
    send mobile sms code
    POST /sms_codes/
    """

    def post(self, request):
        # 1、
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        # 2、
        form = forms.CheckImgCodeForm(data=dict_data)
        if form.is_valid():
            # 获取手机号
            mobile = form.cleaned_data.get('mobile')
            # 3、
            # 创建短信验证码内容
            sms_num = ''.join([random.choice(string.digits) for _ in range(constants.SMS_CODE_NUMS)])

            # 将短信验证码保存到数据库
            # 确保settings.py文件中有配置redis CACHE
            # Redis原生指令参考 http://redisdoc.com/index.html
            # Redis python客户端 方法参考 http://redis-py.readthedocs.io/en/latest/#indices-and-tables
            # 4、
            redis_conn = get_redis_connection(alias='verify_codes')
            # pl = redis_conn.pipeline()

            # 创建一个在60s以内是否有发送短信记录的标记
            sms_flag_fmt = "sms_flag_{}".format(mobile)
            # 创建保存短信验证码的标记key
            sms_text_fmt = "sms_{}".format(mobile)

            # 此处设置为True会出现bug
            try:
                redis_conn.setex(sms_flag_fmt.encode('utf8'), constants.SEND_SMS_CODE_INTERVAL, 1)
                redis_conn.setex(sms_text_fmt.encode('utf8'), constants.SMS_CODE_REDIS_EXPIRES, sms_num)
                # 让管道通知redis执行命令
                # pl.execute()
            except Exception as e:
                logger.debug("redis 执行出现异常：{}".format(e))
                return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

            logger.info("Sms code: {}".format(sms_num))
            # return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")

            # 发送短语验证码
            # try:
            #     result = CCP().send_template_sms(mobile,
            #                                      [sms_num, constants.SMS_CODE_REDIS_EXPIRES],
            #                                      constants.SMS_CODE_TEMP_ID)
            # except Exception as e:
            #     logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
            #     return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            # else:
            #     if result == 0:
            #         logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
            #         return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
            #     else:
            #         logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
            #         return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
            # celery -A celery_tasks.main worker -l info
            expires = constants.SMS_CODE_REDIS_EXPIRES
            sms_tasks.send_sms_code.delay(mobile, sms_num, expires, constants.SMS_CODE_TEMP_ID)
            return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")

        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

#忘记密码界面，电话登录
class ForgetMobileView(View):

    def get(self, request, Mobile_phone):
        if Mobile_phone:

            data = {
                'mobile': Mobile_phone,
                'count': Users.objects.filter(mobile=Mobile_phone).count()

            }

            return JsonResponse(data=data)

        else:
            logger.debug("数据库查询mobile_phone故障")

#忘记密码界面,电话登录验证码
class ForgetSmsCodesView(View):

    def post(self, request):

        # 1.获取所有数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        dict_data = json.loads(json_data.decode('utf-8'))

        mobile = dict_data.get('mobile', None)

        if mobile:

            # 创建短信验证码内容
            sms_num = ''.join([random.choice(string.digits) for _ in range(constants.SMS_CODE_NUMS)])

            # 将短信验证码保存到数据库
            # 确保settings.py文件中有配置redis CACHE
            # Redis原生指令参考 http://redisdoc.com/index.html
            # Redis python客户端 方法参考 http://redis-py.readthedocs.io/en/latest/#indices-and-tables
            # 4、建立连接

            redic_conn = get_redis_connection(alias='verify_codes')

            # 创建一个在60秒以内是否有发送记录的标记
            sms_flag_fmt = "sms_flag_{}".format(mobile)

            # 创建保存短信验证码的标记key
            sms_text_fmt = "sms_{}".format(mobile)

            try:
                #生成一个redis的键值
                redic_conn.setex(sms_text_fmt.encode('utf-8'), constants.SMS_CODE_REDIS_EXPIRES, sms_num)
                redic_conn.setex(sms_flag_fmt.encode('utf-8'), constants.SEND_SMS_CODE_INTERVAL, 1)

            except Exception as e:
                logging.debug('redis 执行出现异常:{}'.format(e))

                return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])
            logger.info("Sms code: {}".format(sms_num))
            #
            # return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
            # 发送短语验证码
            # try:
            #     result = CCP().send_template_sms(mobile,
            #                                      [sms_num, constants.SMS_CODE_REDIS_EXPIRES],
            #                                      constants.SMS_CODE_TEMP_ID)
            # except Exception as e:
            #     logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
            #     return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            # else:
            #     if result == 0:
            #         logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
            #         return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
            #     else:
            #         logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
            #         return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
            # 使用celery异步处理短信发送任务
            expires = constants.SMS_CODE_REDIS_EXPIRES
            sms_tasks.send_sms_code.delay(mobile, sms_num, expires, constants.SMS_CODE_TEMP_ID)
            return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
        else:
            # 定义一个错误列表

            return to_json_data(errno=Code.PARAMERR, errmsg="短信发送失败")
