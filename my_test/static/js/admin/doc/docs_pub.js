// 创建static/js/admin/doc/docs_pub.js文件

$(function () {

  let $docFileUrl = $("#docs-file-url");    // 获取小说地址输入框元素
  let $tagSelect = $("#category-select");   // 获取选择分类标签元素
  let $newsSelect = $("#news-select");      // 获取选择文章标签元素

  // ================== 上传文件至服务器 ================
  let $upload_file_server = $("#upload-file-server");
  $upload_file_server.change(function () {
    // let _this = this;
    let file = this.files[0];   // 获取文件
    let oFormData = new FormData();  // 创建一个 FormData
    oFormData.append("text_file", file); // 把文件添加进去
    // 发送请求
    $.ajax({
      url: "/admin/docs/files/",
      method: "POST",
      data: oFormData,
      processData: false,   // 定义文件的传输
      contentType: false,
    })
      .done(function (res) {
        if (res.errno === "0") {
          message.showSuccess("文件上传成功");
          let sTextFileUrl = res.data.text_file;
          $docFileUrl.val('');
          $docFileUrl.val(sTextFileUrl);

        } else {
          message.showError(res.errmsg)
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });

  });


    $tagSelect.change(function () {
    // 获取当前选中的下拉框的value
    let sTagId = $(this).val();
    if (sTagId === '0') {
      $newsSelect.children('option').remove();
      $newsSelect.append(`<option value="0">--请选择文章--</option>`);
      return
    }
    // 根据文章分类id向后端发起get请求
    $.ajax({
      // 请求地址
     url: "/admin/story_by_tagid/" + sTagId + "/story/",  // url尾部需要添加/
      // 请求方式
      type: "POST",
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {

          $newsSelect.children('option').remove();
          $newsSelect.append(`<option value="0">--请选择文章--</option>`);
          res.data.story.forEach(function (one_story) {
            let content = `<option value="${one_story.id}">${one_story.title}</option>`;
            $newsSelect.append(content)
          });

        } else {
          // swal.showInputError(res.errmsg);
          fAlert.alertErrorToast(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });

  });



  // ================== 发布小说下载 ================
  let $docsBtn = $("#btn-pub-news");
  $docsBtn.click(function () {



    // 判断文档url是否为空
    let sDocFileUrl = $docFileUrl.val();
    if (!sDocFileUrl) {
      message.showError('请上传小说文件或输入小说文件地址地址');
      return
    }

    // 获取docsId 存在表示更新 不存在表示发表
    let sStoryId =$("#news-select").val();
    let stories_Id = $(this).data("news-id");
    let url = stories_Id ? '/admin/docs_put/' : '/admin/docs_put/';
    let data = {
      "story_id":sStoryId,
      "file_url": sDocFileUrl,
    };

    $.ajax({
      // 请求地址
      url: url,
      // 请求方式
      type:stories_Id ? 'PUT' : 'POST',
      data: JSON.stringify(data),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          if (stories_Id) {
            fAlert.alertNewsSuccessCallback("文档更新成功", '跳到文档管理页', function () {
              window.location.href = '/admin/docs_manage/'
            });

          } else {
            fAlert.alertNewsSuccessCallback("文档发表成功", '跳到文档管理页', function () {
              window.location.href = '/admin/docs_manage/'
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