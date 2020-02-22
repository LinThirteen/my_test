$(function () {
  // 未登录提示框

  let $read_story = $('#read');
  let $loginComment = $('.please-login-comment input');
  let $send_comment = $('.logged-comment .comment-btn');

  $read_story.click(function (e) {


    // let storyId = $("#read").attr("story-id");
    let chapterId = $("#chapter").val();


    // 2、创建ajax请求
    $.ajax({
      // 请求地址
      url: "/read_chapter/" + chapterId  + "/" , // url尾部需要添加/
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

            $(".content_title").remove();
             $(".one_content").remove();
              tb_content = `<div class="content_title" style="width:90% ;margin:15px auto;text-align: center"><h4>${one_contents.chapter}: ${one_contents.chapter_title}</h4></div>`;
              ta_content = `<div class="one_content" style="width: 90%;border-bottom:1px solid #ddd;margin: auto;margin-bottom: 10%">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${one_contents.contents}</div>`;
            $("#context").prepend(ta_content);
             $("#context").prepend(tb_content);


          } else {
            // 注册失败，打印错误信息
            message.showError(res.errmsg);
          }
        })
        .fail(function () {
          message.showError('服务器超时，请重试！');
        });

  });

   $('.comment-list').delegate('a,input', 'click', function () {

    let sClassValue = $(this).prop('class');

    if (sClassValue.indexOf('reply_a_frist') >= 0) {
      $(this).next().toggle();
      $(".reply_a_frist").remove();
    }

    if (sClassValue.indexOf('reply_cancel') >= 0) {
      $(this).parent().toggle();
      tb_content = `<a href="javascript:" class="reply_a_frist" style="border-radius: 5px;margin-left: 94%;font-size: 14px;border: 2px solid #76b6f4;background-color: #76b6f4;color: white;text-decoration:none">&nbsp;回复&nbsp;</a>`;

      $(".comment-list").prepend(tb_content); //头部加入


    }


    if (sClassValue.indexOf('reply_btn') >= 0) {
      // 获取新闻id、评论id、评论内容
      let $this = $(this);
      let story_id = $this.parent().attr('stories-id');
      let parent_id = $this.parent().attr('comment-id');
      let content = $this.prev().val();

      if (!content) {
        message.showError('请输入评论内容！');
        return
      }
      // 定义发给后端的参数
      let sDataParams = {
        "content": content,
        "parent_id": parent_id
      };
      $.ajax({
        url: "/story_comment/" + story_id + "/",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(sDataParams),
        dataType: "json",
      })
          .done(function (res) {
            if (res.errno === "0") {
              let one_comment = res.data;
              let html_comment = ``;
              html_comment += ` <div style="width: 80%;background-color: white;margin: auto">
                <div><img src="${ one_comment.user_image_url }" style="margin-top: 7px;width: 35px;height: 35px;border-radius: 5px;" alt=""><span style="margin-left: 1.5%;margin-top: 10px">${ one_comment.author }&nbsp;&nbsp;回复：</span>
              </div>
                <h6 style="margin-left: 12%;width: 85%;margin-top: 0px;">${ one_comment.content }</h6>
                </div>`;

              $this.parent().parent().next().next().append(html_comment)

              // next().find('.son-comment').prepend(html_comment);
              $this.prev().val('');   // 请空输入框
              $this.parent().hide();  // 关闭评论框
              tb_content = `<a href="javascript:" class="reply_a_frist" style="border-radius: 5px;margin-left: 94%;font-size: 14px;border: 2px solid #76b6f4;background-color: #76b6f4;color: white;text-decoration:none">&nbsp;回复&nbsp;</a>`;

              $(".comment-list").prepend(tb_content); //头部加入

            } else if (res.errno === "4101") {
              // 用户未登录
              message.showError(res.errmsg);
              setTimeout(function () {
                // 重定向到打开登录页面
                window.location.href = "/login/";
              }, 800)

            } else {
              // 失败，打印错误信息
              message.showError(res.errmsg);
            }
          })
          .fail(function () {
            message.showError('服务器超时，请重试！');
          });

    }
  });


  // 点击评论框，重定向到用户登录页面
  $loginComment.click(function () {

    $.ajax({
      url: "/story_comment/" + $(".please-login-comment").attr('stories-id') + "/",
      type: "POST",
      contentType: "application/json; charset=utf-8",
      dataType: "json",
    })
        .done(function (res) {
          if (res.errno === "4101") {
            message.showError("请登录之后再评论！");
            setTimeout(function () {
              // 重定向到打开登录页面
              window.location.href = "/login/";
            }, 800)

          } else {
            // 失败，打印错误信息
            message.showError(res.errmsg);
          }
        })
        .fail(function () {
          message.showError('服务器超时，请重试！');
        });
  });




  // 发表评论
  $send_comment.click(function () {
    // 获取新闻id、评论id、评论内容
    let $this = $(this);
    let story_id = $this.parent().attr('stories-id');
    // let parent_id = $this.parent().attr('comment-id');
    let content = $this.prev().val();     // 当前的前一个元素的内容

    if (!content) {
      message.showError('请输入评论内容！');
      return
    }
    // 定义发给后端的参数
    let sDataParams = {
      "content": content
    };
    $.ajax({
      url: "/story_comment/" + story_id + "/",
      type: "POST",
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(sDataParams),
      dataType: "json",
    })
        .done(function (res) {
          if (res.errno === "0") {
            let one_comment = res.data;
            let html_comment = ``;
            html_comment += `
              <div  style="width: 90%;background-color:white;margin:10px auto;border-bottom: 1px solid #ddd;">
              <img src="${ one_comment.user_image_url }" style="width: 50px;height: 50px;border-radius: 5px" alt=""><span style="margin-left: 2%">${ one_comment.author }:</span><span style="color:grey;font-size:11px ;float: right;margin-top: 17px">${ one_comment.update_time }</span>
                <h5 style="margin-left: 12%;width: 85%">${ one_comment.content }</h5>
               <div class="comment-list"> </div>
            <div style="">&nbsp;</div>
             <div style="" class="son-comment" ></div>`;

            $(".comment-put").prepend(html_comment);  //头部加入
            $this.prev().val('');   // 请空输入框






            // $this.parent().hide();  // 关闭评论框

          } else if (res.errno === "4101") {
            // 用户未登录
            message.showError(res.errmsg);
            setTimeout(function () {
              // 重定向到打开登录页面
              window.location.href = "/login/";
            }, 800)

          } else {
            // 失败，打印错误信息
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