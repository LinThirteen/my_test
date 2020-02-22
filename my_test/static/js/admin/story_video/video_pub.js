// 创建static/js/admin/course/courses_pub.js文件

$(function () {
  // let $e = window.wangEditor;
  // window.editor = new $e('#course-outline');
  // window.editor.create();


  let $thumbnailUrl = $("#news-thumbnail-url");   // 获取缩略图输入框元素
  let $courseFileUrl = $("#docs-file-url");    // 获取课程地址输入框元素

  // ================== 上传图片文件至服务器 ================
  let $upload_image_server = $("#upload-image-server");
  $upload_image_server.change(function () {
    // let _this = this;
    let file = this.files[0];   // 获取文件
    let oFormData = new FormData();  // 创建一个 FormData
    oFormData.append("image_file", file); // 把文件添加进去
    // 发送请求
    $.ajax({
      url: "/admin/fdfs/images/",
      method: "POST",
      data: oFormData,
      processData: false,   // 定义文件的传输
      contentType: false,
    })
      .done(function (res) {
        if (res.errno === "0") {
          message.showSuccess("图片上传成功");
          let sImageUrl = res.data.image_url;
          // let $inpuUrl = $(_this).parents('.input-group').find('input:nth-child(1)');
          $thumbnailUrl.val('');
          $thumbnailUrl.val(sImageUrl);

        } else {
          message.showError(res.errmsg)
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });

  });


  // ================== 上传图片至七牛（云存储平台） ================
  let $progressBar = $(".progress-bar");
  QINIU.upload({
    "domain":"http://q161k7dn6.bkt.clouddn.com/",  // 七牛空间域名
    // 后台返回 token的地址 (后台返回的 url 地址) 不可能成功
    "uptoken_url": "/admin/token/",
    // 按钮
    "browse_btn": "upload-image-btn",
    // 成功
    "success": function (up, file, info) {
      let domain = up.getOption('domain');
      let res = JSON.parse(info);
      let filePath = domain + res.key;
      console.log(filePath);  // 打印文件路径
      $thumbnailUrl.val('');
      $thumbnailUrl.val(filePath);
    },
    // 失败
    "error": function (up, err, errTip) {
      // console.log('error');
      console.log(up);
      console.log(err);
      console.log(errTip);
      // console.log('error');
      message.showError(errTip);
    },
    "progress": function (up, file) {
      let percent = file.percent;
      $progressBar.parent().css("display", 'block');
      $progressBar.css("width", percent + '%');
      $progressBar.text(parseInt(percent) + '%');
    },
    // 完成后 去掉进度条
    "complete": function () {
      $progressBar.parent().css("display", 'none');
      $progressBar.css("width", '0%');
      $progressBar.text('0%');
    }
  });


  // ================== 发布音频 ================
  let $docsBtn = $("#btn-pub-news");
  $docsBtn.click(function () {
    // 判断课程标题是否为空
    let sTitle = $("#news-title").val();  // 获取文件标题
    if (!sTitle) {
      message.showError('请填写视频标题！');
      return
    }


    // 判断课程缩略图url是否为空
    let sThumbnailUrl = $thumbnailUrl.val();
    if (!sThumbnailUrl) {
      message.showError('请上传课程缩略图');
      return
    }

    // 判断课程url是否为空
    let sCourseFileUrl = $courseFileUrl.val();
    if (!sCourseFileUrl) {
      message.showError('请上传视频或输入视频地址');
      return
    }

    // 判断视频时长是否为空
    let sCourseTime = $('#course-time').val();  // 获取视频时长
    if (!sCourseTime) {
      message.showError('请填写视频时长！');
      return
    }



    // 获取coursesId 存在表示更新 不存在表示发表
    let coursesId = $(this).data("news-id");
    let url = coursesId ? '/admin/video_edit/' + coursesId + '/' : '/admin/video_put/';
    let data = {
      "title": sTitle,
      "cover_url": sThumbnailUrl,
      "video_url": sCourseFileUrl,
      "duration": sCourseTime,


    };

    $.ajax({
      // 请求地址
      url: url,
      // 请求方式
      type: coursesId ? 'PUT' : 'POST',
      data: JSON.stringify(data),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          if (coursesId) {
            fAlert.alertNewsSuccessCallback("视频更新成功", '跳到课程管理页', function () {
              window.location.href = '/admin/video_manage/';
            });

          } else {
            fAlert.alertNewsSuccessCallback("课程发表成功", '跳到课程管理页', function () {
              window.location.href = '/admin/video_manage/'
            });
          }
        } else {
          fAlert.alertErrorToast(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });

  });


  // get cookie using jQuery
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  // Setting the token on the AJAX request
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });

});
