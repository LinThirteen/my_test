from time import localtime

from django.db import models

from utils.models import ModelBase
# Create your models here.

class Tag(ModelBase):

    name = models.CharField(max_length=64, verbose_name="标签名", help_text="标签名")


    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_tag"  # 指明数据库表名
        verbose_name = "小说分类"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.name


class Stories(ModelBase):
    """
    """
    # PRI_CHOICES_STORY = [
    #     (1, '第一级'),
    #     (2, '第二级'),
    #     (3, '第三级'),
    # ]
    # author = models.CharField(max_length=150, verbose_name="作者", help_text="作者")
    title = models.CharField(max_length=150, verbose_name="标题", help_text="标题")
    digest = models.CharField(max_length=200, verbose_name="摘要", help_text="摘要")
    clicks = models.IntegerField(default=0, verbose_name="点击量", help_text="点击量")
    image_url = models.URLField(default="", verbose_name="图片url", help_text="图片url")
    price = models.IntegerField(default=0, verbose_name="价格", help_text="价格")
    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey('users.Users', on_delete=models.SET_NULL, null=True)
    # priority = models.IntegerField(choices=PRI_CHOICES_STORY, verbose_name="优先级", help_text="优先级")


    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_stories"  # 指明数据库表名
        verbose_name = "小说"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.title


class Chapter(ModelBase):
    chapter = models.CharField(max_length=10, verbose_name="章节数", help_text="章节数")
    chapter_title = models.CharField(max_length=64, verbose_name="章节标题", help_text="章节标题")
    content = models.TextField(verbose_name="内容", help_text="内容")
    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, null=True)
    story = models.ForeignKey('Stories', on_delete=models.SET_NULL, null=True)
    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_chapter"  # 指明数据库表名
        verbose_name = "小说章节"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.chapter

class Banner(ModelBase):
    PRI_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级'),
    ]

    image_url = models.URLField(verbose_name="轮播图url", help_text="轮播图url")
    priority = models.IntegerField(choices=PRI_CHOICES,verbose_name="优先级", help_text="优先级",default=1)
    stories = models.OneToOneField('stories', on_delete=models.CASCADE)

    class Meta:
        ordering = ['priority', '-update_time', '-id']
        db_table = "tb_banner"  # 指明数据库表名
        verbose_name = "轮播图"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '<轮播图{}>'.format(self.id)

class Announcement(ModelBase):
    PRI_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级'),
    ]

    content = models.CharField(max_length=200, verbose_name="公告内容", help_text="公告内容")
    priority = models.IntegerField(choices=PRI_CHOICES,verbose_name="优先级", help_text="优先级")



    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_announcement"  # 指明数据库表名
        verbose_name = "公告"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.content

class Comments(ModelBase):
    """
    """
    content = models.TextField(verbose_name="内容", help_text="内容")
    author = models.ForeignKey('users.Users', on_delete=models.SET_NULL, null=True)
    stories = models.ForeignKey('Stories', on_delete=models.CASCADE)    #models.CASCADE 级联删除
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # blank指前端可以不用传
    zan = models.IntegerField(verbose_name="点赞", help_text="点赞",default=0)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = "tb_comments"  # 指明数据库表名
        verbose_name = "评论"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称


    def to_dict_data(self):
        comment_dict = {
            'user_image_url':self.author.detail.image_url,     #        #
            'content_id': self.id,     #
            'content': self.content,
            'author': self.author.username,
            'update_time': self.update_time.strftime('%Y年%m月%d日'),    #
            'parent': self.parent.to_dict_data() if self.parent else None,
        }

        return comment_dict

    def __str__(self):
        return '<评论{}>'.format(self.id)