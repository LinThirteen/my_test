
$(function () {
  // let $e = window.wangEditor;
  // window.editor = new $e('#news-content');
  // window.editor.create();

  // 获取缩略图输入框元素
  let $thumbnailUrl = $("#news-thumbnail-url");



  $("#choice_chapter").change(function(){

    // let storyId = $("#read").attr("story-id");
    let chapterId = $("#choice_chapter").val();

    if (chapterId==='0'){

         $("#contentsss").remove();
            chapter_content = `<textarea name="content" id="contentsss" style="border:0;border-radius:5px;background-color:rgba(241,241,241,.98);width: 100%;height: 500px;padding: 10px;resize: none;" placeholder="小说章节内容"></textarea>`;
            $(".contexts").append(chapter_content);
    }else {

      // 2、创建ajax请求
      $.ajax({
        // 请求地址
        url: "/write_chapter/" + chapterId + "/", // url尾部需要添加/
        // 请求方式
        type: "POST",
        // 请求内容的数据类型（前端发给后端的格式）
        contentType: "application/json; charset=utf-8",
        // 响应数据的格式（后端返回给前端的格式）
        dataType: "json",
      })
          .done(function (res) {
            if (res.errno === "0") {

              let one_contents = res.data;

              $("#contentsss").remove();
              chapter_content = `<textarea name="content" id="contentsss" style="border:0;border-radius:5px;background-color:rgba(241,241,241,.98);width: 100%;height: 500px;padding: 10px;resize: none;" data-chapter-id="${one_contents.id}" placeholder="小说章节内容">&nbsp;&nbsp;&nbsp;&nbsp;${one_contents.content}</textarea>`;
              $(".contexts").append(chapter_content);

            } else {
              // 注册失败，打印错误信息
              message.showError(res.errmsg);
            }
          })
          .fail(function () {
            message.showError('服务器超时，请重试！');
          });
    }
  });



// ================== 上传至七牛（云存储平台） ================
  let $progressBar = $(".progress-bar");
  QINIU.upload({
    "domain": "http://q2p2pu8od.bkt.clouddn.com/",  // 七牛空间域名
    "uptoken_url": "/upload_token/",	 // 后台返回 token的地址
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


 // ================== 更新文章 ================
  let $newsBtn = $("#btn-pub-story");
  $newsBtn.click(function () {



    let chpterId = $("#choice_chapter").val();
    if (chpterId === '0' ) {
      message.showError('请选择小说章节')
      return
    }

    let sContentHtml = $("#contentsss").val();
    // let sContentHtml = $("#content").val();
    if (!sContentHtml) {
        message.showError('请填写章节内容！');
        return
    }



    let chapterId = $(this).data("chapter-id");
    let url = '/chapter_edit/' + chapterId + '/';
    let data = {

      "content": sContentHtml,
    };

    $.ajax({
      // 请求地址
      url: url,
      // 请求方式
      type: 'PUT' ,
      data: JSON.stringify(data),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          if (chapterId) {
              message.showSuccess("文章更新成功");
              setTimeout(function () {
                 window.location.reload();
                }, 1000)
          }

        } else {
          message.showError(res.errmsg);
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






