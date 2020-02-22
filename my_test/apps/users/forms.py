import re

from django import forms
from django.contrib.auth import login
from django.db.models import Q
from django_redis import get_redis_connection

# from users import constants
from verifications.constants import SMS_CODE_NUMS
from .models import Users
from .cookies_pass import USER_SESSION_EXPIRES
from stories.models import Stories, Chapter


# 登录数据校验表单
class LoginFrom(forms.Form):
    user_account = forms.CharField()
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"})
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        """
        """
        self.request = kwargs.pop('request', None)
        super(LoginFrom, self).__init__(*args, **kwargs)

    # 判断是否用用户名
    def clean_user_account(self):

        user_info = self.cleaned_data.get('user_account')
        if not user_info:
            raise forms.ValidationError('用户账号不存在')

        # if not re.match(r"^1[3-9]\d{9}$", user_info) and (len(user_info) < 5 or len(user_info) > 20):
        #     raise forms.ValidationError("用户账号格式不正确，请重新输入")
        return user_info

    # 对所有数据进行校验
    def clean(self):

        cleaned_data = super().clean()
        use_info = cleaned_data.get('user_account')
        password = cleaned_data.get('password')
        remember = cleaned_data.get('remember_me')

        # 从数据库里面取数据
        user_queryset = Users.objects.filter(Q(mobile=use_info) | Q(username=use_info))
        # 如果检测到用户有备注（违规）则返回错误
        if user_queryset:
            if user_queryset.first().remark:
                raise forms.ValidationError(user_queryset.first().remark)
            else:
                user = user_queryset.first()
                # 检测密码是够输入正确，调用check_password方法
                if user.check_password(password):

                    if remember:
                        # 如果记住密码，则消去原有的cookies
                        self.request.seesion.set_expiry(None)

                    else:
                        self.request.session.set_expiry(USER_SESSION_EXPIRES)

                    # 该函数接受一个 HttpRequest 对象和一个 User 对象作为参数并使用Django的会话（ session ）框架把用户的ID保存在该会话中。
                    login(self.request, user)
                else:
                    raise forms.ValidationError("密码不正确,请重新输入")

        else:
            raise forms.ValidationError('用户账号不存在,请重新输入')


class RegisterForm(forms.Form):
    """
    """
    username = forms.CharField(label='用户名', max_length=20, min_length=1,
                               error_messages={"min_length": "用户名长度要大于1", "max_length": "用户名长度要小于20",
                                               "required": "用户名不能为空"}
                               )
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"}
                               )
    password_repeat = forms.CharField(label='确认密码', max_length=20, min_length=6,
                                      error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                                      "required": "密码不能为空"}
                                      )
    mobile = forms.CharField(label='手机号', max_length=11, min_length=11,
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})

    sms_code = forms.CharField(label='短信验证码', max_length=SMS_CODE_NUMS, min_length=SMS_CODE_NUMS,
                               error_messages={"min_length": "短信验证码长度有误", "max_length": "短信验证码长度有误",
                                               "required": "短信验证码不能为空"})

    def clean_username(self):
        user = self.cleaned_data.get('username')
        # 判断输入的用户名是否被注册了
        if Users.objects.filter(username=user).exists():
            raise forms.ValidationError('用户名已经注册')
        #一定要有返回数据
        return user


    #检测电话号码
    def clean_mobile(self):
        """
        """
        tel = self.cleaned_data.get('mobile')
        #查看输入的电话号码格式是否正确
        if not re.match(r"^1[3-9]\d{9}$", tel):
            raise forms.ValidationError("手机号码格式不正确")
        #查看电话号码是否存在
        if Users.objects.filter(mobile=tel).exists():
            raise forms.ValidationError("手机号已注册，请重新输入！")
        return tel


    #检测所有数据
    def clean(self):
        """
        """
        cleaned_data = super().clean()
        passwd = cleaned_data.get('password')
        passwd_repeat = cleaned_data.get('password_repeat')

        if passwd != passwd_repeat:
            raise forms.ValidationError("两次密码不一致")

        #获取电话号码
        tel = cleaned_data.get('mobile')

        #获取图片验证码
        sms_text = cleaned_data.get('sms_code')

        # 建立redis连接
        redis_conn = get_redis_connection(alias='verify_codes')

        #格式化电话验证码
        sms_fmt = "sms_{}".format(tel).encode('utf-8')

        #从数据库中获取眼图片验证码
        real_sms = redis_conn.get(sms_fmt)

        #
        if (not real_sms) or (sms_text != real_sms.decode('utf-8')):
            raise forms.ValidationError("短信验证码错误")


class DetailForm(forms.Form):
    """
    """
    textareas = forms.CharField(label='个性签名', max_length=50, min_length=0,
                                error_messages={"min_length": "个性签名不能超过50个字", }

                                )
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"}
                               )
    password_repeat = forms.CharField(label='确认密码', max_length=20, min_length=6,
                                      error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                                      "required": "密码不能为空"}
                                      )
    mobile = forms.CharField(label='手机号', max_length=11, min_length=11,
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})

    sms_code = forms.CharField(label='短信验证码', max_length=SMS_CODE_NUMS, min_length=SMS_CODE_NUMS,
                               error_messages={"min_length": "短信验证码长度有误", "max_length": "短信验证码长度有误",
                                               "required": "短信验证码不能为空"})

    # def clean_username(self):
    #     user = self.cleaned_data.get('username')
    #     if Users.objects.filter(username=user).exists():
    #         raise forms.ValidationError('用户名已经注册')
    #     return user

    def clean_mobile(self):
        """
        """
        tel = self.cleaned_data.get('mobile')
        if not re.match(r"^1[3-9]\d{9}$", tel):
            raise forms.ValidationError("手机号码格式不正确")

        return tel

    def clean(self):
        """
        """
        #
        cleaned_data = super().clean()
        passwd = cleaned_data.get('password')
        passwd_repeat = cleaned_data.get('password_repeat')

        if passwd != passwd_repeat:
            #
            raise forms.ValidationError("两次密码不一致")

        #
        tel = cleaned_data.get('mobile')
        sms_text = cleaned_data.get('sms_code')

        # 建立redis连接
        redis_conn = get_redis_connection(alias='verify_codes')

        #格式化电话号码生成key
        sms_fmt = "sms_{}".format(tel).encode('utf-8')

        #从redis数据库里面获取电话号码的key
        real_sms = redis_conn.get(sms_fmt)

        #判断是够一样
        if (not real_sms) or (sms_text != real_sms.decode('utf-8')):
            raise forms.ValidationError("短信验证码错误")


class StoriesPubForm(forms.ModelForm):
    """
    """
    image_url = forms.URLField(label='文章图片url',
                               error_messages={"required": "文章图片url不能为空"})

    price = forms.IntegerField(label='小说价格',
                               error_messages={"required": "小说价格不能为空"}
                               )

    class Meta:
        model = Stories  # 与数据库模型关联
        # 需要关联的字段

        fields = ['title', 'digest', 'image_url', 'price', 'tag']
        error_messages = {
            'title': {
                'max_length': "文章标题长度不能超过150",
                'min_length': "文章标题长度大于1",
                'required': '文章标题不能为空',
            },
            'digest': {
                'max_length': "文章摘要长度不能超过200",
                'min_length': "文章标题长度大于1",
                'required': '文章摘要不能为空',
            },

        }


class ChapterAddForm(forms.ModelForm):
    """
    """
    chapter_title = forms.CharField(label='文章标题',
                                    error_messages={"required": "文章标题不能为空"})

    content = forms.CharField(label='章节内容',
                              error_messages={"required": "章节内容不能为空"}
                              )

    class Meta:
        model = Chapter  # 与数据库模型关联
        # 需要关联的字段
        # exclude 排除
        fields = ['chapter_title', 'content', 'chapter', 'tag']
