import logging

from django.http import Http404
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from . import models

logger = logging.getLogger('django')


# @method_decorator(cache_page(timeout=120, cache='page_cache'), name='dispatch')
def storyvideo_list(request):
    story_video = models.Storyvideo.objects.only('title', 'cover_url','id','duration').filter(is_delete=False)
    return render(request, 'storyvideo/storyvideo.html', locals())

# @method_decorator(cache_page(timeout=20, cache='page_cache'), name='dispatch')
class VideoDetailView(View):
    """
    """
    def get(self, request,video_id):
        try:
            video = models.Storyvideo.objects.only('title', 'cover_url', 'video_url' ).filter(is_delete=False, id=video_id).first()
            return render(request, 'storyvideo/video_detail.html',locals())
        except models.Storyvideo.DoesNotExist as e:    #抛出模型错误
            logger.info("当前课程出现如下异常：\n{}".format(e))
            raise Http404("此课程不存在！")