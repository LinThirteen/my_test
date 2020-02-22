import requests

from django.core.paginator import Paginator, EmptyPage
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.utils.encoding import escape_uri_path
from django.views import View
from django.shortcuts import render

from admin.views import logger
from doc import constants
from doc.models import Doc
from my_test import settings
from utils.json_fun import to_json_data
from . import models
# Create your views here.

class DocView(View):

    def get(self,request):

        doc_file_all = models.Doc.objects.select_related('story').only('id','story__title','story__image_url','story__id','story__digest','file_url','story__price')
        doc_file_all = doc_file_all.filter(story__price='0')[0:4]
        doc_list = []
        for doc_file in doc_file_all:
            doc_list.append({
                'id':doc_file.id,
                'title':doc_file.story.title,
                'image_url':doc_file.story.image_url,
                'story_id':doc_file.story.id,
                'story_digest':doc_file.story.digest,
                'file_url':doc_file.file_url,

            })
        return render(request,'doc/docDownload.html',locals())

class DocdownView(View):

    def get(self,request):

        try:
            page = int(request.GET.get('page',1))

        except Exception as e:
            logger.error("当前页数错误:\n{}".format(e))
            page = 1

        #取第8本到最后一本小说
        story_down = models.Doc.objects.select_related('story').only('story_id','file_url','id','story__title','story__digest','story__image_url').filter(is_delete=False)

        paginator = Paginator(story_down,constants.SHOW_DOWNLOAD_STORY_COUNT)  #将全部小说分成每页8条


        try:

            story_info = paginator.page(page) #第page页全部8条内容

        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logger.info("用户访问的页数大于总页数")
            story_info = paginator.page(paginator.num_pages)

        story_info_list = []

        for s in story_info:
            story_info_list.append({
                'id':s.id,
                'file_url':s.file_url,
                'story_id': s.story_id,
                'title': s.story.title,
                'image_url': s.story.image_url,
                'digest':s.story.digest,


            })


        #返回给前端数据
        data = {
            'total_pages':paginator.num_pages,     #总页数
            'stories':story_info_list
        }
        return to_json_data(data=data)

class DocDownload(View):

    def get(self, request, doc_id):
        if not request.user.is_authenticated:

            return render(request,'users/login.html')
        doc = Doc.objects.only('file_url').filter(is_delete=False, id=doc_id).first()
        if doc:
            doc_url = doc.file_url
            doc_url = settings.SITE_DOMAIN_PORT + doc_url

            try:
                res = FileResponse(requests.get(doc_url, stream=True))  # 有stream时只在需要下载时服务器才会下载
                # 仅测试的话可以这样子设置
                # res = FileResponse(open(doc.file_url, 'rb'))
            except Exception as e:
                logger.info("获取文档内容出现异常：\n{}".format(e))
                raise Http404("文档下载异常！")

            ex_name = doc_url.split('.')[-1]
            # https://stackoverflow.com/questions/23714383/what-are-all-the-possible-values-for-http-content-type-header
            # http://www.iana.org/assignments/media-types/media-types.xhtml#image
            if not ex_name:
                raise Http404("文档url异常！")
            else:
                ex_name = ex_name.lower()

            if ex_name == "pdf":
                res["Content-type"] = "application/pdf"
            elif ex_name == "zip":
                res["Content-type"] = "application/zip"
            elif ex_name == "doc":
                res["Content-type"] = "application/msword"
            elif ex_name == "xls":
                res["Content-type"] = "application/vnd.ms-excel"
            elif ex_name == "docx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ex_name == "ppt":
                res["Content-type"] = "application/vnd.ms-powerpoint"
            elif ex_name == "pptx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

            else:
                raise Http404("文档格式不正确！")

            doc_filename = escape_uri_path(doc_url.split('/')[-1])
            # 设置为inline，会直接打开
            res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)  # 显示下载文件名称
            return res

        else:
            raise Http404("文档不存在！")
