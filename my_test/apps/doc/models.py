from django.db import models

from utils.models import ModelBase


class Doc(ModelBase):
    """create doc view
    """
    file_url = models.URLField(verbose_name="小说文件url", help_text="小说文件url")
    one_otrher = models.IntegerField(verbose_name='预留',help_text='预留',null=True)
    story =models.OneToOneField('stories.Stories',on_delete=models.SET_NULL, null=True)


    class Meta:
        db_table = "tb_docs"   # 指明数据库表名
        verbose_name = "小说下载"    # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.file_url
