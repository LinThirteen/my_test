from django.db import models

from utils.models import ModelBase



class Storyvideo(ModelBase):
    title = models.CharField(max_length=150, verbose_name="视频名", help_text='视频名')
    cover_url = models.URLField(verbose_name="视频封面图URL", help_text='视频封面图URL')
    video_url = models.URLField(verbose_name="视频URL", help_text='视频URL')
    duration = models.FloatField(default=0.0, verbose_name="视频时长", help_text='视频时长')
    other = models.TextField(null=True, blank=True, verbose_name="其他", help_text='其他')

    class Meta:
        db_table = "tb_storyvideo"  # 指明数据库表名
        verbose_name = "小说视频"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.title
