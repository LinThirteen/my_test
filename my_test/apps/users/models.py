from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager


# Create your models here.
from utils.models import ModelBase


class UserManager(_UserManager):

    #类的重写
    def create_superuser(self, username, password, email=None, **extra_fields):
        super().create_superuser(username=password,password=password, email=email, **extra_fields)

class Users(AbstractUser):
    """
    add mobile、email_active fields to Django users models.
    """
    objects = UserManager()
    # A list of the field names that will be prompted for
    # when creating a user via the createsuperuser management command.
    REQUIRED_FIELDS = ['mobile']

    # help_text在api接口文档中会用到
    # verbose_name在admin站点中会用到
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号", help_text='手机号',
                              error_messages={'unique': "此手机号已注册"} ) # 指定报错的中文信息

    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    #备注
    remark =  models.CharField(max_length=50,verbose_name="备注", help_text='备注',default="")

    vip  =  models.BooleanField(default=False,verbose_name="vip", help_text='vip')

    write = models.BooleanField(default=False,verbose_name="作者", help_text='作者')



    class Meta:
        db_table = "tb_users"  # 指明数据库表名
        verbose_name = "用户"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def get_groups_name(self):
        groups_name_list = [i.name for i in self.groups.all()]
        return ' | '.join(groups_name_list)

    def __str__(self):  # 打印对象时调用
        return self.username


class Detail(ModelBase):
    address = models.TextField(verbose_name="地址", help_text="地址", null=True,)
    SEX_CHOICES = (
        (0, '女'),
        (1, '男')
    )
    sex = models.SmallIntegerField(verbose_name="性别", default=0, choices=SEX_CHOICES, null=True)
    image_url = models.URLField(verbose_name="头像url", help_text="头像url",null=True)
    introduce = models.TextField(verbose_name="个人介绍", help_text="个人介绍", null=True,)
    user = models.OneToOneField('Users',on_delete=models.SET_NULL, null=True)


    class Meta:
        db_table = "tb_detail"  # 指明数据库表名
        verbose_name = "个人信息"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):  # 打印对象时调用
        return self.user.username