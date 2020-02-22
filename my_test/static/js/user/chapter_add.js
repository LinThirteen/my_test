
$(function () {



 // ================== 更新文章 ================
  let $newsBtn = $("#btn-pub-story");
  $newsBtn.click(function () {

    let chapter_number = $("#chapter-number").val();
    if (!chapter_number ) {
      message.showError('请填写小说章节')
      return
    }


    let chapter_title = $("#chapter-title").val();
    if (!chapter_title ) {
      message.showError('请填写章节标题')
      return
    }


    let sContentHtml = $("#content").val();
    if (!sContentHtml) {
        message.showError('请填写章节内容！');
        return
    }


    let tagId = $(this).data("tags-id");
    let storyId = $(this).data("story-id");
    let url =  '/chapter_add/' + storyId + '/';
    let data = {
      "tag":tagId ,
      "chapter":chapter_number,
      "chapter_title": chapter_title,
      "content": sContentHtml,
    };

    $.ajax({
      // 请求地址
      url: url,
      // 请求方式
      type: 'POST',
      data: JSON.stringify(data),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          if (storyId) {
            message.showSuccess("文章创建成功");
            setTimeout(function () {
              window.location.href = '/write_edit/' + storyId + '/';
            }, 1000)
          }
        }else {
            message.showError(res.errmsg);

          }})
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






