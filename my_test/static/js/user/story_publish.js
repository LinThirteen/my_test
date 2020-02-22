
$(function () {

  // 获取缩略图输入框元素
  let $thumbnailUrl = $("#news-thumbnail-url");
  let $StoryName = $("#story-title");
  let storyid = $("#btn-pub-stories").data("story-id");

  if(!storyid) {// 2、小说名字效验
    $StoryName.blur(function () {
      fn_check_storyname();
    });


    function fn_check_storyname() {
      let story_name = $StoryName.val();  // 获取用户名字符串
      let variable = "";
      if (story_name === "") {
        message.showError('小说标题不能为空！');
        return
      }
      let data = {
        "story_name": story_name,

      };
      //发送ajax请求
      $.ajax({
        url: '/story_publish/',
        type: 'POST',
        data: JSON.stringify(data),
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json; charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
        async: false   //异步
      })
          .done(function (res) {
            // /** @namespace res.data.fault */
            if (res.count & res.count !== 0) {
              message.showError("《" + res.title + "》" + ' 已存在，请重新输入')

            } else {
              message.showInfo("《" + res.title + "》" + ' 能正常使用！')
              variable = 'success'
            }
          })
          .fail(function () {
            message.showError('服务器超时，请重试')
          });
      return variable

    }
  }

// ================== 上传至七牛（云存储平台） ================
  let $progressBar = $(".progress-bar");
  QINIU.upload({
    "domain": "http://q2p2pu8od.bkt.clouddn.com/",  // 七牛空间域名
    "uptoken_url": "/admin/token/",	 // 后台返回 token的地址
    "browse_btn": "upload-btn",		// 按钮
    "success": function (up, file, info) {	 // 成功
      let domain = up.getOption('domain');
      let res = JSON.parse(info);
      let filePath = domain + res.key;
      console.log(filePath);
      $thumbnailUrl.val('');
      $thumbnailUrl.val(filePath);
    },
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
    "complete": function () {
      $progressBar.parent().css("display", 'none');
      $progressBar.css("width", '0%');
      $progressBar.text('0%');
    }
  });


 // ================== 发布/更新文章 ================
  let $storiesBtn = $("#btn-pub-stories");
  $storiesBtn.click(function () {
    // 判断文章标题是否为空
    let sTitle = $("#story-title").val();  // 获取文章标题
    if (!sTitle) {
        message.showError('请填写小说标题！');
        return
    }
    // 判断文章摘要是否为空
    let sDesc = $("#story-desc").val();  // 获取文章摘要
    if (!sDesc) {
        message.showError('请填写小说摘要！');
        return
    }
    if (sDesc.length > 200) {
        message.showError('请输入200个字以内的小说摘要！');
        return
    }

    let sTagId = $("#choice_chapter").val();
    if (!sTagId || sTagId === "0") {
      message.showError('请选择小说标签');
      return
    }

    let sThumbnailUrl = $thumbnailUrl.val();
    if (!sThumbnailUrl) {
      message.showError('请上传文章缩略图')
      return
    }

    let price = $("#story-price").val();
    if (!price) {
      message.showError('小说价格不能为空')
      return
    }

    // 获取news_id 存在表示更新 不存在表示发表
   let  storiesId = $(this).data("story-id");
    let url = storiesId ? '/story_put/' + storiesId + '/' : '/story_post/';
     if(sThumbnailUrl.indexOf("http") == -1){
      sThumbnailUrl =  'http://127.0.0.1:8000' + sThumbnailUrl
            }
    let data = ""
    if(!storyid){
       let chapter_title = $("#chapter-title").val();
    if (!chapter_title) {
      message.showError('小说章节标题不能为空！')
      return
    }
      let story_content = $("#story_content").val();
    if (!story_content) {
      message.showError('小说章节内容不能为空！')
      return
    }
   let chapter = $("#chapter-number").val();
    let ret = {
      "title": sTitle,
      "digest": sDesc,
      "tag": sTagId,
      "price":price,
      "image_url":sThumbnailUrl,
      "chapter":chapter,
      "content":story_content,
      "chapter_title":chapter_title,
    };

     data = ret
     }else{

       let ret = {
      "title": sTitle,
      "digest": sDesc,
      "tag": sTagId,
      "price":price,
      "image_url":sThumbnailUrl,

};
     data = ret

     }

    $.ajax({
      // 请求地址
      url: url,
      // 请求方式
      type: storiesId ? 'PUT' : 'POST',
      data: JSON.stringify(data),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          if (storiesId) {
              message.showSuccess("小说更新成功");
              setTimeout(function () {
                window.location.href='/story_change/'+ storiesId + '/';
                }, 800)

          } else {
              message.showSuccess("小说添加成功");
              setTimeout(function () {
               window.location.href='/write/';
                }, 1000)
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


