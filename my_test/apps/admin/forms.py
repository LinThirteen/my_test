from django import forms
from stories.models import Stories, Tag
from storyvideo.models import Storyvideo
from . import models


class StoriesPubForm(forms.ModelForm):
    """
    """
    image_url = forms.URLField(label='文章图片url',
                               error_messages={"required": "文章图片url不能为空"})
    tag = forms.ModelChoiceField(queryset=Tag.objects.only('id').filter(is_delete=False),
                                 error_messages={"required": "文章标签id不能为空", "invalid_choice": "文章标签id不存在", }
                                 )
    price = forms.IntegerField(label='小说价格',
                                 error_messages={"required":"小说价格不能为空"}
                                 )

    class Meta:
        model = Stories  # 与数据库模型关联
        # 需要关联的字段
        # exclude 排除
        fields = ['title', 'digest', 'image_url', 'tag','price']
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


class VideoPubForm(forms.ModelForm):
    """create courses pub form
    """
    cover_url = forms.URLField(label='封面图url',
                               error_messages={"required": "封面图url不能为空"})

    video_url = forms.URLField(label='视频url',
                               error_messages={"required": "视频url不能为空"})



    class Meta:
        model =Storyvideo   # 与数据库模型关联
        # 需要关联的字段
        # exclude 排除
        exclude = ['is_delete', 'create_time', 'update_time']
        error_messages = {
            'title': {
                'max_length': "视频标题长度不能超过150",
                'min_length': "视频标题长度大于1",
                'required': '视频标题不能为空',
            },

        }


class OrderForm(forms.ModelForm):
    """create courses pub form
    """
    user_address = forms.CharField(label='地址',
                               error_messages={"required": "地址不能为空"})


    class Meta:
        model = models.OrderForm  # 与数据库模型关联
        # 需要关联的字段
        # exclude 排除
        exclude = ['is_delete', 'create_time', 'update_time','status','place']
