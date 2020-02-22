from django.db import models

# Create your models here.
from utils.models import ModelBase


class OrderForm(ModelBase):


    usesr = models.TextField(verbose_name="用户名", help_text="用户名", null=True)
    order_information = models.TextField(verbose_name="订单内容", help_text="订单内容", null=True)
    book_price = models.IntegerField(verbose_name="商品价格", help_text="商品价格",null=True)
    number = models.IntegerField(verbose_name="数量", help_text="数量",null=True)
    user_address = models.TextField(verbose_name="用户地址", help_text="用户地址",null=True)
    user_mobile = models.TextField(verbose_name="用户电话", help_text="用户电话",null=True)
    status = models.BooleanField(verbose_name="状态", help_text="状态",null=True)
    place  = models.TextField(verbose_name="物流", help_text="物流",null=True,default="等待商家处理")



    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_order_form"  # 指明数据库表名
        verbose_name = "订单信息"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.usesr